"""A-3：找零不足入账钱包的 API 测试。"""
from decimal import Decimal

import pytest
from sqlmodel import Session, SQLModel, create_engine, select

from app import plugins  # noqa: F401
plugins.install_models()

from app.models import AutoPart, Client, Order, OrderItem  # noqa: F401
from app.plugins.fmcg.models import WalletLedger
from app.plugins.fmcg.services import wallet as ws
from app.plugins.fmcg.services.exceptions import WalletError


@pytest.fixture()
def engine(tmp_path):
    eng = create_engine(f"sqlite:///{tmp_path}/cs.db")
    wanted = (
        "fmcg_wallet", "fmcg_wallet_ledger",
        "autopart", "client", "orders", "order_items",
    )
    tables = [
        t for name, t in SQLModel.metadata.tables.items()
        if name in wanted
    ]
    SQLModel.metadata.create_all(eng, tables=tables)
    return eng


def _seed_order(s: Session, order_no="TK-100", total_usd=10.0, total_bs=365.0,
                status="COMPLETED") -> Order:
    o = Order(
        order_no=order_no, client_name="Cliente General",
        total_usd=total_usd, total_bs=total_bs, bcv_rate=36.5,
        payment_method="Cash_USD", status=status,
        operator="tester",
    )
    s.add(o); s.commit(); s.refresh(o)
    return o


def test_credit_change_short_happy_path(engine):
    with Session(engine) as s:
        _seed_order(s, "TK-100", total_usd=10.0)
        ledger = ws.credit_change_short(
            s, order_no="TK-100", phone="0414-111-0001",
            currency="USD", amount=Decimal("0.35"),
        )
        assert ledger.amount == Decimal("0.3500")
        assert ledger.ref_type == "change_short"
        assert ledger.ref_id == "TK-100"
        assert ws.get_balance(s, "0414-111-0001", "USD") == Decimal("0.3500")


def test_credit_change_short_is_idempotent(engine):
    with Session(engine) as s:
        _seed_order(s, "TK-101", total_usd=10.0)
        a = ws.credit_change_short(s, "TK-101", "0414-111-0002", "USD",
                                   Decimal("0.50"))
        b = ws.credit_change_short(s, "TK-101", "0414-111-0002", "USD",
                                   Decimal("0.50"))
        assert a.id == b.id
        assert ws.get_balance(s, "0414-111-0002", "USD") == Decimal("0.5000")
        assert len(s.exec(select(WalletLedger)).all()) == 1


def test_credit_change_short_order_not_found(engine):
    with Session(engine) as s:
        with pytest.raises(WalletError):
            ws.credit_change_short(s, "TK-999", "0414-111-0003", "USD",
                                   Decimal("0.10"))


def test_credit_change_short_order_not_completed(engine):
    with Session(engine) as s:
        _seed_order(s, "TK-102", total_usd=10.0, status="VOID")
        with pytest.raises(WalletError):
            ws.credit_change_short(s, "TK-102", "0414-111-0004", "USD",
                                   Decimal("0.10"))


def test_credit_change_short_exceeds_order_total(engine):
    with Session(engine) as s:
        _seed_order(s, "TK-103", total_usd=10.0)
        with pytest.raises(WalletError):
            ws.credit_change_short(s, "TK-103", "0414-111-0005", "USD",
                                   Decimal("15.00"))


def test_credit_change_short_ves_cap(engine):
    with Session(engine) as s:
        _seed_order(s, "TK-104", total_usd=10.0, total_bs=365.0)
        ws.credit_change_short(s, "TK-104", "0414-111-0006", "VES",
                               Decimal("360"))
        with pytest.raises(WalletError):
            ws.credit_change_short(s, "TK-104", "0414-111-0007", "VES",
                                   Decimal("400"))


def test_credit_change_short_rejects_non_positive(engine):
    with Session(engine) as s:
        _seed_order(s, "TK-105", total_usd=10.0)
        with pytest.raises(WalletError):
            ws.credit_change_short(s, "TK-105", "0414-111-0008", "USD",
                                   Decimal("0"))
