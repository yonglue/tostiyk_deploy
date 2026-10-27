"""FMCG 插件模型：建表 + 约束 + 金额精度的最小验证。"""
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, SQLModel, create_engine, select

# 触发插件注册，否则 SQLModel.metadata 里没有 fmcg 表
from app import plugins  # noqa: F401
plugins.install_models()

from app.plugins.fmcg.models import (  # noqa: E402
    ProductPrice,
    ProductUnit,
    Wallet,
    WalletLedger,
)


@pytest.fixture()
def engine():
    eng = create_engine("sqlite:///:memory:")
    tables = [
        t for name, t in SQLModel.metadata.tables.items()
        if name in (
            "fmcg_product_unit", "fmcg_product_price",
            "fmcg_wallet", "fmcg_wallet_ledger",
            "autopart", "client",
        )
    ]
    SQLModel.metadata.create_all(eng, tables=tables)
    return eng


def _seed_autopart(session: Session, oem: str = "SKU-1") -> int:
    from app.models import AutoPart
    part = AutoPart(oem=oem, name="Test Item")
    session.add(part)
    session.commit()
    session.refresh(part)
    return part.id


def test_product_unit_decimal_precision(engine):
    with Session(engine) as s:
        pid = _seed_autopart(s)
        s.add(ProductUnit(
            product_id=pid, code="box", name="Caja",
            is_base=False, qty_per_base=Decimal("24"),
        ))
        s.add(ProductUnit(
            product_id=pid, code="unit", name="Unidad",
            is_base=True, qty_per_base=Decimal("1"),
        ))
        s.commit()

        got = s.exec(select(ProductUnit).where(ProductUnit.code == "box")).first()
        assert got.qty_per_base == Decimal("24.0000")
        assert str(got.qty_per_base) == "24.0000"


def test_product_unit_unique_code_per_product(engine):
    with Session(engine) as s:
        pid = _seed_autopart(s)
        s.add(ProductUnit(product_id=pid, code="box", name="Caja"))
        s.commit()
        s.add(ProductUnit(product_id=pid, code="box", name="Caja Dup"))
        with pytest.raises(IntegrityError):
            s.commit()
        s.rollback()


def test_product_price_unique_dimension(engine):
    with Session(engine) as s:
        pid = _seed_autopart(s)
        u = ProductUnit(product_id=pid, code="unit", name="Unidad", is_base=True)
        s.add(u); s.commit(); s.refresh(u)

        s.add(ProductPrice(
            product_id=pid, unit_id=u.id,
            price_tier="retail", price_usd=Decimal("1.50"),
        ))
        s.commit()

        s.add(ProductPrice(
            product_id=pid, unit_id=u.id,
            price_tier="retail", price_usd=Decimal("1.75"),
        ))
        with pytest.raises(IntegrityError):
            s.commit()
        s.rollback()


def test_wallet_unique_phone_currency(engine):
    with Session(engine) as s:
        s.add(Wallet(customer_phone="0414-000-0001", currency="USD",
                     balance=Decimal("0")))
        s.commit()

        s.add(Wallet(customer_phone="0414-000-0001", currency="USD",
                     balance=Decimal("0")))
        with pytest.raises(IntegrityError):
            s.commit()
        s.rollback()  # 关键：IntegrityError 后必须回滚

        # 同手机号不同币种应允许
        s.add(Wallet(customer_phone="0414-000-0001", currency="VES",
                     balance=Decimal("0")))
        s.commit()
        assert len(s.exec(select(Wallet)).all()) == 2


def test_wallet_ledger_signed_amount_and_balance(engine):
    with Session(engine) as s:
        w = Wallet(customer_phone="0414-000-0002", currency="USD",
                   balance=Decimal("0"))
        s.add(w); s.commit(); s.refresh(w)

        s.add(WalletLedger(
            wallet_id=w.id, tx_type="credit",
            amount=Decimal("0.35"), balance_after=Decimal("0.35"),
            ref_type="change_short", ref_id="ORDER-1",
        ))
        w.balance = Decimal("0.35")
        s.add(w); s.commit()

        s.add(WalletLedger(
            wallet_id=w.id, tx_type="debit",
            amount=Decimal("-0.35"), balance_after=Decimal("0.00"),
            ref_type="sale", ref_id="ORDER-2",
        ))
        w.balance = Decimal("0.00")
        s.add(w); s.commit()

        ledger = s.exec(
            select(WalletLedger).where(WalletLedger.wallet_id == w.id)
        ).all()
        total = sum((r.amount for r in ledger), Decimal("0"))
        s.refresh(w)
        assert total == w.balance == Decimal("0.0000")
