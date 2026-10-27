"""钱包服务层测试：幂等、原子性、余额校验、多币种隔离。

用临时文件 DB（而非 :memory:），因为服务层多次 session.refresh，
:memory: 每个 connection 是独立实例，会丢数据。
"""
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, SQLModel, create_engine, select

from app import plugins  # noqa: F401  触发插件注册
plugins.install_models()

from app.models import AutoPart, Client  # noqa: F401  确保 FK 目标表在 metadata
from app.plugins.fmcg.models import Wallet, WalletLedger
from app.plugins.fmcg.services.exceptions import (
    InsufficientBalance,
    WalletError,
    WalletNotFound,
)
from app.plugins.fmcg.services import wallet as ws


@pytest.fixture()
def engine(tmp_path):
    eng = create_engine(f"sqlite:///{tmp_path}/test.db")
    wanted = (
        "fmcg_wallet", "fmcg_wallet_ledger",
        "autopart", "client",
    )
    tables = [
        t for name, t in SQLModel.metadata.tables.items()
        if name in wanted
    ]
    SQLModel.metadata.create_all(eng, tables=tables)
    return eng


def test_credit_creates_wallet_and_increases_balance(engine):
    with Session(engine) as s:
        ledger = ws.credit(
            s, phone="0414-000-1000", currency="USD",
            amount=Decimal("2.50"),
            ref_type="manual", ref_id="MAN-1",
        )
        assert ledger.amount == Decimal("2.5000")
        assert ledger.balance_after == Decimal("2.5000")
        assert ws.get_balance(s, "0414-000-1000", "USD") == Decimal("2.5000")


def test_credit_is_idempotent_by_ref(engine):
    with Session(engine) as s:
        first = ws.credit(
            s, phone="0414-000-1001", currency="USD",
            amount=Decimal("1.00"),
            ref_type="sale_short_change", ref_id="ORDER-100",
        )
        second = ws.credit(
            s, phone="0414-000-1001", currency="USD",
            amount=Decimal("1.00"),
            ref_type="sale_short_change", ref_id="ORDER-100",
        )
        assert first.id == second.id
        assert ws.get_balance(s, "0414-000-1001", "USD") == Decimal("1.0000")
        assert len(s.exec(select(WalletLedger)).all()) == 1


def test_debit_reduces_balance(engine):
    with Session(engine) as s:
        ws.credit(s, "0414-000-1002", "USD", Decimal("5.00"),
                  ref_type="manual", ref_id="MAN-A")
        ws.debit(s, "0414-000-1002", "USD", Decimal("1.25"),
                 ref_type="sale", ref_id="ORDER-A")
        assert ws.get_balance(s, "0414-000-1002", "USD") == Decimal("3.7500")
        ledger = s.exec(
            select(WalletLedger).where(WalletLedger.ref_type == "sale")
        ).first()
        assert ledger.amount == Decimal("-1.2500")
        assert ledger.balance_after == Decimal("3.7500")


def test_debit_insufficient_balance(engine):
    with Session(engine) as s:
        ws.credit(s, "0414-000-1003", "USD", Decimal("1.00"),
                  ref_type="manual", ref_id="MAN-B")
        with pytest.raises(InsufficientBalance):
            ws.debit(s, "0414-000-1003", "USD", Decimal("2.00"),
                     ref_type="sale", ref_id="ORDER-B")
        assert ws.get_balance(s, "0414-000-1003", "USD") == Decimal("1.0000")


def test_debit_is_idempotent_by_ref(engine):
    with Session(engine) as s:
        ws.credit(s, "0414-000-1004", "USD", Decimal("5.00"),
                  ref_type="manual", ref_id="MAN-C")
        d1 = ws.debit(s, "0414-000-1004", "USD", Decimal("2.00"),
                      ref_type="sale", ref_id="ORDER-C")
        d2 = ws.debit(s, "0414-000-1004", "USD", Decimal("2.00"),
                      ref_type="sale", ref_id="ORDER-C")
        assert d1.id == d2.id
        assert ws.get_balance(s, "0414-000-1004", "USD") == Decimal("3.0000")


def test_reject_non_positive_amount(engine):
    with Session(engine) as s:
        with pytest.raises(WalletError):
            ws.credit(s, "0414-000-1005", "USD", Decimal("0"),
                      ref_type="manual")
        with pytest.raises(WalletError):
            ws.credit(s, "0414-000-1005", "USD", Decimal("-1"),
                      ref_type="manual")


def test_db_unique_index_blocks_duplicate_ref(engine):
    """绕过服务层直插两条同 ref 的流水，必须被 DB 唯一索引拦下。"""
    with Session(engine) as s:
        ws.credit(s, "0414-000-1006", "USD", Decimal("1.00"),
                  ref_type="manual", ref_id="MAN-UNIQ")
        w = ws.get_wallet(s, "0414-000-1006", "USD")
        s.add(WalletLedger(
            wallet_id=w.id, tx_type="credit",
            amount=Decimal("1.00"), balance_after=Decimal("2.00"),
            ref_type="manual", ref_id="MAN-UNIQ",
        ))
        with pytest.raises(IntegrityError):
            s.commit()
        s.rollback()


def test_get_balance_missing_wallet(engine):
    with Session(engine) as s:
        with pytest.raises(WalletNotFound):
            ws.get_balance(s, "0414-999-9999", "USD")


def test_ledger_and_balance_are_consistent(engine):
    with Session(engine) as s:
        ws.credit(s, "0414-000-1007", "USD", Decimal("3.00"),
                  ref_type="manual", ref_id="MAN-X1")
        ws.credit(s, "0414-000-1007", "USD", Decimal("2.00"),
                  ref_type="manual", ref_id="MAN-X2")
        ws.debit(s, "0414-000-1007", "USD", Decimal("1.50"),
                 ref_type="sale", ref_id="ORDER-X1")
        w = ws.get_wallet(s, "0414-000-1007", "USD")
        rows = list(s.exec(
            select(WalletLedger).where(WalletLedger.wallet_id == w.id)
        ).all())
        total = sum((r.amount for r in rows), Decimal("0"))
        assert total == w.balance == Decimal("3.5000")


def test_multiple_currencies_same_phone(engine):
    with Session(engine) as s:
        ws.credit(s, "0414-000-1008", "USD", Decimal("1.00"),
                  ref_type="manual", ref_id="M-USD")
        ws.credit(s, "0414-000-1008", "VES", Decimal("100.00"),
                  ref_type="manual", ref_id="M-VES")
        assert ws.get_balance(s, "0414-000-1008", "USD") == Decimal("1.0000")
        assert ws.get_balance(s, "0414-000-1008", "VES") == Decimal("100.0000")
