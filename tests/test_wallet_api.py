"""钱包 REST API 集成测试。

策略：
* 用隔离 FastAPI app 挂载钱包 router，dependency_overrides 覆盖权限和 session
* 额外一条集成断言：app.main:app 真的注册了 3 个 /api/fmcg/wallets/* 端点
  （不触发 lifespan，只看路由表，不跑 bootstrap）
"""
from decimal import Decimal

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app import plugins  # noqa: F401
plugins.install_models()

from app.models import AutoPart, Client  # noqa: F401
from app.database import get_session
from app.plugins.fmcg.services import wallet as ws
from app.plugins.fmcg.routers import wallet as wrouter


@pytest.fixture()
def engine(tmp_path):
    eng = create_engine(f"sqlite:///{tmp_path}/api.db")
    tables = [
        t for name, t in SQLModel.metadata.tables.items()
        if name in ("fmcg_wallet", "fmcg_wallet_ledger", "autopart", "client")
    ]
    SQLModel.metadata.create_all(eng, tables=tables)
    return eng


@pytest.fixture()
def api(engine):
    app = FastAPI()
    app.include_router(wrouter.router)

    def _session_override():
        with Session(engine) as s:
            yield s

    app.dependency_overrides[get_session] = _session_override
    app.dependency_overrides[wrouter._perm_view] = lambda: None
    app.dependency_overrides[wrouter._perm_credit] = lambda: None
    app.dependency_overrides[wrouter._perm_debit] = lambda: None

    with TestClient(app) as c:
        yield c


def test_credit_endpoint_returns_ledger(api):
    r = api.post("/api/fmcg/wallets/credit", json={
        "phone": "0414-111-0001",
        "currency": "USD",
        "amount": "3.50",
        "ref_type": "manual",
        "ref_id": "API-1",
    })
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["amount"] == "3.5000"
    assert body["balance_after"] == "3.5000"


def test_credit_endpoint_is_idempotent(api):
    payload = {
        "phone": "0414-111-0002",
        "currency": "USD",
        "amount": "1.00",
        "ref_type": "manual",
        "ref_id": "API-IDEMP",
    }
    r1 = api.post("/api/fmcg/wallets/credit", json=payload)
    r2 = api.post("/api/fmcg/wallets/credit", json=payload)
    assert r1.status_code == r2.status_code == 200
    assert r1.json()["id"] == r2.json()["id"]


def test_get_balance_returns_ledger(api):
    api.post("/api/fmcg/wallets/credit", json={
        "phone": "0414-111-0003", "currency": "USD", "amount": "5.00",
        "ref_type": "manual", "ref_id": "API-G1",
    })
    r = api.get("/api/fmcg/wallets/0414-111-0003?currency=USD")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["balance"] == "5.0000"
    assert len(body["recent_ledger"]) == 1
    assert body["recent_ledger"][0]["amount"] == "5.0000"


def test_get_balance_404_for_unknown(api):
    r = api.get("/api/fmcg/wallets/0414-999-9999?currency=USD")
    assert r.status_code == 404


def test_debit_endpoint_success(api):
    api.post("/api/fmcg/wallets/credit", json={
        "phone": "0414-111-0004", "currency": "USD", "amount": "5.00",
        "ref_type": "manual", "ref_id": "API-D-CREDIT",
    })
    r = api.post("/api/fmcg/wallets/debit", json={
        "phone": "0414-111-0004", "currency": "USD", "amount": "2.00",
        "ref_type": "sale", "ref_id": "API-D-SALE",
    })
    assert r.status_code == 200, r.text
    assert r.json()["balance_after"] == "3.0000"


def test_debit_endpoint_insufficient_returns_400(api):
    api.post("/api/fmcg/wallets/credit", json={
        "phone": "0414-111-0005", "currency": "USD", "amount": "1.00",
        "ref_type": "manual", "ref_id": "API-INS-CREDIT",
    })
    r = api.post("/api/fmcg/wallets/debit", json={
        "phone": "0414-111-0005", "currency": "USD", "amount": "2.00",
        "ref_type": "sale", "ref_id": "API-INS-SALE",
    })
    assert r.status_code == 400


def test_credit_rejects_zero_amount(api):
    r = api.post("/api/fmcg/wallets/credit", json={
        "phone": "0414-111-0006", "currency": "USD", "amount": "0",
        "ref_type": "manual",
    })
    assert r.status_code == 400


def test_main_app_registers_fmcg_wallet_routes():
    """集成断言：plugin.register_routes 真的把 3 个端点挂到 app.main:app。

    注意：FastAPI 0.143.0 起 include_router 把子路由包成 _IncludedRouter，
    不再平铺到 app.routes，因此用 openapi paths 做断言（跨版本稳定）。
    """
    from app.main import app
    paths = app.openapi()["paths"]
    assert "/api/fmcg/wallets/credit" in paths
    assert "/api/fmcg/wallets/debit" in paths
    assert "/api/fmcg/wallets/{phone}" in paths
    assert "post" in paths["/api/fmcg/wallets/credit"]
    assert "post" in paths["/api/fmcg/wallets/debit"]
    assert "get" in paths["/api/fmcg/wallets/{phone}"]
