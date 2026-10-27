"""找零钱包 REST API。

三个端点：
* GET  /api/fmcg/wallets/{phone}   查询余额 + 最近流水
* POST /api/fmcg/wallets/credit    入账
* POST /api/fmcg/wallets/debit     扣减

权限沿用现有 perm 位（不新增）：
* 查询：financial:view
* 入账/扣减：pos:checkout（收银权限）

权限依赖提取为模块级变量 _perm_view / _perm_credit / _perm_debit，
便于测试用 app.dependency_overrides 精确覆盖。
"""
from __future__ import annotations

from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlmodel import Session

from app.database import get_session
from app.deps import Actor, RequirePermission
from app.plugins.fmcg.services import wallet as ws
from app.plugins.fmcg.services.exceptions import (
    InsufficientBalance,
    WalletError,
    WalletNotFound,
)

router = APIRouter(prefix="/api/fmcg/wallets", tags=["FMCG 找零钱包"])

_perm_view = RequirePermission("financial:view")
_perm_credit = RequirePermission("pos:checkout")
_perm_debit = RequirePermission("pos:checkout")


class CreditPayload(BaseModel):
    phone: str = Field(min_length=3, max_length=32)
    currency: str = Field(default="USD", max_length=8)
    amount: Decimal
    ref_type: str = Field(min_length=1, max_length=32)
    ref_id: Optional[str] = Field(default=None, max_length=64)
    note: Optional[str] = Field(default=None, max_length=255)


class DebitPayload(CreditPayload):
    pass


class ChangeShortPayload(BaseModel):
    order_no: str = Field(min_length=1, max_length=64)
    phone: str = Field(min_length=3, max_length=32)
    currency: str = Field(default="USD", max_length=8)
    amount: Decimal
    note: Optional[str] = Field(default=None, max_length=255)


def _ledger_to_dict(r) -> dict:
    return {
        "id": r.id,
        "tx_type": r.tx_type,
        "amount": str(r.amount),
        "balance_after": str(r.balance_after),
        "ref_type": r.ref_type,
        "ref_id": r.ref_id,
        "note": r.note,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }


@router.post("/credit")
def credit_wallet(
    payload: CreditPayload,
    actor: Actor = Depends(_perm_credit),
    session: Session = Depends(get_session),
):
    try:
        ledger = ws.credit(
            session,
            phone=payload.phone,
            currency=payload.currency,
            amount=payload.amount,
            ref_type=payload.ref_type,
            ref_id=payload.ref_id,
            note=payload.note,
        )
    except WalletError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _ledger_to_dict(ledger)


@router.post("/debit")
def debit_wallet(
    payload: DebitPayload,
    actor: Actor = Depends(_perm_debit),
    session: Session = Depends(get_session),
):
    try:
        ledger = ws.debit(
            session,
            phone=payload.phone,
            currency=payload.currency,
            amount=payload.amount,
            ref_type=payload.ref_type,
            ref_id=payload.ref_id,
            note=payload.note,
        )
    except InsufficientBalance as e:
        raise HTTPException(status_code=400, detail=str(e))
    except WalletError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _ledger_to_dict(ledger)


@router.post("/change-short")
def credit_change_short_endpoint(
    payload: ChangeShortPayload,
    actor: Actor = Depends(_perm_credit),
    session: Session = Depends(get_session),
):
    """找零不足时把差额入账客户钱包（幂等：同一 order_no 只入账一次）。"""
    try:
        ledger = ws.credit_change_short(
            session,
            order_no=payload.order_no,
            phone=payload.phone,
            currency=payload.currency,
            amount=payload.amount,
            note=payload.note,
        )
    except WalletError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _ledger_to_dict(ledger)


@router.get("/{phone}")
def get_wallet_balance(
    phone: str,
    currency: str = Query(default="USD"),
    actor: Actor = Depends(_perm_view),
    session: Session = Depends(get_session),
):
    try:
        wallet = ws.get_wallet(session, phone, currency)
        if wallet is None:
            raise WalletNotFound(f"钱包不存在: phone={phone} currency={currency}")
        ledger = ws.list_ledger(session, wallet.id, limit=10)
    except WalletNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {
        "phone": phone,
        "currency": currency,
        "balance": str(wallet.balance),
        "recent_ledger": [_ledger_to_dict(r) for r in ledger],
    }
