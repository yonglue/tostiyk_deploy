"""FMCG 插件数据模型：Multi-Empaque（多包装）+ Monedero（找零钱包）。

设计约束：
* 表名一律 `fmcg_` 前缀，避免与既有表冲突
* 不改动既有 autopart / client / orders 表，FK 引用其主键
* 金额统一用 Decimal(12,4)，避免 float 精度问题
* Wallet.balance 是冗余列，真相在 WalletLedger，由服务层保证一致
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from pydantic import NaiveDatetime
from sqlalchemy import Index
from sqlmodel import Field, SQLModel


def _utcnow_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ══════════════════════════ Multi-Empaque ══════════════════════════
class ProductUnit(SQLModel, table=True):
    """商品的一个包装单位。"""
    __tablename__ = "fmcg_product_unit"
    __table_args__ = (
        Index("uq_fmcg_unit_product_code", "product_id", "code", unique=True),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="autopart.id", index=True)
    code: str = Field(max_length=32)
    name: str = Field(max_length=64)
    is_base: bool = Field(default=False)
    qty_per_base: Decimal = Field(
        default=Decimal("1"), max_digits=12, decimal_places=4,
    )
    barcode: Optional[str] = Field(default=None, max_length=64, index=True)
    created_at: NaiveDatetime = Field(default_factory=_utcnow_naive)


class ProductPrice(SQLModel, table=True):
    """每个 (商品, 包装单位, 价格层级) 只有一行当前有效价。"""
    __tablename__ = "fmcg_product_price"
    __table_args__ = (
        Index(
            "uq_fmcg_price_dim",
            "product_id", "unit_id", "price_tier",
            unique=True,
        ),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="autopart.id", index=True)
    unit_id: int = Field(foreign_key="fmcg_product_unit.id", index=True)
    price_tier: str = Field(default="retail", max_length=32)
    price_usd: Decimal = Field(max_digits=12, decimal_places=4)
    updated_at: NaiveDatetime = Field(default_factory=_utcnow_naive)


# ══════════════════════════ Monedero ══════════════════════════
class Wallet(SQLModel, table=True):
    """找零钱包。手机号 + 币种 唯一。"""
    __tablename__ = "fmcg_wallet"
    __table_args__ = (
        Index("uq_fmcg_wallet_phone_ccy", "customer_phone", "currency", unique=True),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    customer_phone: str = Field(max_length=32, index=True)
    customer_id: Optional[int] = Field(
        default=None, foreign_key="client.id", index=True,
    )
    currency: str = Field(default="USD", max_length=8)
    balance: Decimal = Field(
        default=Decimal("0"), max_digits=14, decimal_places=4,
    )
    created_at: NaiveDatetime = Field(default_factory=_utcnow_naive)
    updated_at: NaiveDatetime = Field(default_factory=_utcnow_naive)


class WalletLedger(SQLModel, table=True):
    """钱包流水（append-only）。"""
    __tablename__ = "fmcg_wallet_ledger"
    __table_args__ = (
        Index("ix_fmcg_ledger_wallet_ts", "wallet_id", "created_at"),
        # 幂等键：同一 (ref_type, ref_id) 只允许一条流水；
        # SQLite 允许多个 NULL ref_id，所以手工调整类流水不受限
        Index("uq_fmcg_ledger_ref", "ref_type", "ref_id", unique=True),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    wallet_id: int = Field(foreign_key="fmcg_wallet.id", index=True)
    tx_type: str = Field(max_length=16)
    amount: Decimal = Field(max_digits=14, decimal_places=4)
    balance_after: Decimal = Field(max_digits=14, decimal_places=4)
    ref_type: str = Field(max_length=32)
    ref_id: Optional[str] = Field(default=None, max_length=64)
    note: Optional[str] = Field(default=None, max_length=255)
    created_at: NaiveDatetime = Field(default_factory=_utcnow_naive)


__all__ = [
    "ProductUnit",
    "ProductPrice",
    "Wallet",
    "WalletLedger",
]
