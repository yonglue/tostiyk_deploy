"""找零钱包服务层。

设计约定：
* Wallet.balance 是冗余列，真相在 WalletLedger；
  本模块的每次写操作都在同一事务里写 ledger + 更新 balance。
* (ref_type, ref_id) 是幂等键：同一键重复调用返回既有流水，不重复入账。
  DB 层有 uq_fmcg_ledger_ref 唯一索引做兜底。
* 金额一律 Decimal，内部用字符串构造避免 float 误差。
"""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Optional

from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.plugins.fmcg.models import Wallet, WalletLedger
from app.plugins.fmcg.services.exceptions import (
    InsufficientBalance,
    WalletError,
    WalletNotFound,
)

_ZERO = Decimal("0")
_QUANT = Decimal("0.0001")


def _to_decimal(value) -> Decimal:
    if isinstance(value, Decimal):
        d = value
    else:
        try:
            d = Decimal(str(value))
        except (InvalidOperation, ValueError) as e:
            raise WalletError(f"金额格式非法: {value!r}") from e
    return d.quantize(_QUANT)


def get_wallet(session: Session, phone: str, currency: str) -> Optional[Wallet]:
    return session.exec(
        select(Wallet).where(
            Wallet.customer_phone == phone,
            Wallet.currency == currency,
        )
    ).first()


def get_or_create_wallet(session: Session, phone: str, currency: str) -> Wallet:
    w = get_wallet(session, phone, currency)
    if w:
        return w
    w = Wallet(customer_phone=phone, currency=currency, balance=_ZERO)
    session.add(w)
    try:
        session.flush()
        return w
    except IntegrityError:
        session.rollback()
        w = get_wallet(session, phone, currency)
        if w is None:
            raise WalletError(
                f"并发创建钱包失败且重查不到: phone={phone} currency={currency}"
            )
        return w


def get_balance(session: Session, phone: str, currency: str) -> Decimal:
    w = get_wallet(session, phone, currency)
    if w is None:
        raise WalletNotFound(f"钱包不存在: phone={phone} currency={currency}")
    return w.balance


def list_ledger(session: Session, wallet_id: int, limit: int = 20) -> list[WalletLedger]:
    rows = session.exec(
        select(WalletLedger)
        .where(WalletLedger.wallet_id == wallet_id)
        .order_by(WalletLedger.id.desc())
        .limit(limit)
    ).all()
    return list(rows)


def _find_by_ref(session: Session, ref_type: str, ref_id: str) -> Optional[WalletLedger]:
    return session.exec(
        select(WalletLedger).where(
            WalletLedger.ref_type == ref_type,
            WalletLedger.ref_id == ref_id,
        )
    ).first()


def credit(session, phone, currency, amount, ref_type, ref_id=None, note=None):
    amt = _to_decimal(amount)
    if amt <= _ZERO:
        raise WalletError(f"入账金额必须 > 0，收到 {amt}")
    if ref_id is not None:
        existing = _find_by_ref(session, ref_type, ref_id)
        if existing:
            return existing
    wallet = get_or_create_wallet(session, phone, currency)
    session.exec(
        update(Wallet)
        .where(Wallet.id == wallet.id)
        .values(balance=Wallet.balance + amt)
    )
    session.refresh(wallet)
    ledger = WalletLedger(
        wallet_id=wallet.id, tx_type="credit", amount=amt,
        balance_after=wallet.balance, ref_type=ref_type,
        ref_id=ref_id, note=note,
    )
    session.add(ledger)
    try:
        session.commit()
    except IntegrityError as e:
        session.rollback()
        if ref_id is not None:
            existing = _find_by_ref(session, ref_type, ref_id)
            if existing:
                return existing
        raise WalletError(f"入账失败（DB 冲突）: {e}") from e
    session.refresh(ledger)
    return ledger


def debit(session, phone, currency, amount, ref_type, ref_id=None, note=None):
    amt = _to_decimal(amount)
    if amt <= _ZERO:
        raise WalletError(f"扣减金额必须 > 0，收到 {amt}")
    if ref_id is not None:
        existing = _find_by_ref(session, ref_type, ref_id)
        if existing:
            return existing
    wallet = get_or_create_wallet(session, phone, currency)
    session.refresh(wallet)
    if wallet.balance < amt:
        raise InsufficientBalance(f"余额不足: 当前 {wallet.balance}，需要 {amt}")
    session.exec(
        update(Wallet)
        .where(Wallet.id == wallet.id)
        .values(balance=Wallet.balance - amt)
    )
    session.refresh(wallet)
    ledger = WalletLedger(
        wallet_id=wallet.id, tx_type="debit", amount=-amt,
        balance_after=wallet.balance, ref_type=ref_type,
        ref_id=ref_id, note=note,
    )
    session.add(ledger)
    try:
        session.commit()
    except IntegrityError as e:
        session.rollback()
        if ref_id is not None:
            existing = _find_by_ref(session, ref_type, ref_id)
            if existing:
                return existing
        raise WalletError(f"扣减失败（DB 冲突）: {e}") from e
    session.refresh(ledger)
    return ledger


def credit_change_short(
    session: Session,
    order_no: str,
    phone: str,
    currency: str,
    amount,
    note: Optional[str] = None,
) -> WalletLedger:
    """找零不足时把差额入账客户钱包。

    校验：order 存在 → 状态 COMPLETED → amount <= 订单总额（按币种）。
    幂等：ref_type='change_short', ref_id=order_no。
    """
    from app.models import Order

    order = session.exec(select(Order).where(Order.order_no == order_no)).first()
    if order is None:
        raise WalletError(f"订单不存在: {order_no}")
    if order.status != "COMPLETED":
        raise WalletError(f"订单 {order_no} 状态非 COMPLETED: {order.status}")

    amt = _to_decimal(amount)
    if amt <= _ZERO:
        raise WalletError(f"找零金额必须 > 0，收到 {amt}")

    cap = _to_decimal(order.total_bs if currency == "VES" else order.total_usd)
    if amt > cap:
        raise WalletError(
            f"找零金额 {amt} 超过订单 {order_no} 总额 {cap}"
        )

    return credit(
        session,
        phone=phone,
        currency=currency,
        amount=amt,
        ref_type="change_short",
        ref_id=order_no,
        note=note,
    )
