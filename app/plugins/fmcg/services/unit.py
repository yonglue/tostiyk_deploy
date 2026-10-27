"""主子单位换算服务。

职责：把「按包装单位下的 qty」折算成「主单位 (base unit) 的数量」，
供 POS 下单时扣库存使用。

约定：
* 每个 product 恰有 1 个 is_base=True 的 ProductUnit（不做 DB 强制，由业务层保证）；
* qty_per_base = 1 个该包装单位 = N 个主单位；
  例如 box.qty_per_base=24，表示 1 箱 = 24 瓶。
* 计算全程用 Decimal，避免 float 累积误差；入库时按需 cast 到 int 或 Decimal。
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from sqlmodel import Session, select

from app.plugins.fmcg.models import ProductUnit
from app.plugins.fmcg.services.exceptions import FmcgError


class UnitError(FmcgError):
    """单位相关错误（找不到单位、无主单位、参数非法等）。"""


def _to_decimal(value) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def get_unit_by_code(
    session: Session, product_id: int, code: str,
) -> Optional[ProductUnit]:
    return session.exec(
        select(ProductUnit).where(
            ProductUnit.product_id == product_id,
            ProductUnit.code == code,
        )
    ).first()


def get_base_unit(session: Session, product_id: int) -> ProductUnit:
    units = session.exec(
        select(ProductUnit).where(ProductUnit.product_id == product_id)
    ).all()
    if not units:
        raise UnitError(f"商品 {product_id} 未定义任何包装单位")
    bases = [u for u in units if u.is_base]
    if len(bases) != 1:
        raise UnitError(
            f"商品 {product_id} 主单位数量异常: {len(bases)}（应恰为 1）"
        )
    return bases[0]


def resolve_to_base(
    session: Session,
    product_id: int,
    unit_code: str,
    qty,
) -> Decimal:
    """把 unit_code 包装的 qty 折算为主单位数量。

    例：product_id=1 有 box(code='box', qty_per_base=24)，resolve_to_base(1, 'box', 2)
    返回 Decimal('48.0000')。
    """
    q = _to_decimal(qty)
    if q <= 0:
        raise UnitError(f"数量必须 > 0，收到 {q}")

    unit = get_unit_by_code(session, product_id, unit_code)
    if unit is None:
        raise UnitError(
            f"商品 {product_id} 未定义单位 {unit_code!r}"
        )

    qpb = _to_decimal(unit.qty_per_base)
    result = (q * qpb).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    return result


def resolve_to_base_int(
    session: Session,
    product_id: int,
    unit_code: str,
    qty,
) -> int:
    """同 resolve_to_base，但返回 int（用于 POS 库存扣减，库存是 int）。"""
    d = resolve_to_base(session, product_id, unit_code, qty)
    # 4 位小数 → 整数，四舍五入到个位
    return int(d.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def has_any_units(session: Session, product_id: int) -> bool:
    """该商品是否定义了任何单位（纯汽配老数据返回 False）。"""
    row = session.exec(
        select(ProductUnit).where(ProductUnit.product_id == product_id).limit(1)
    ).first()
    return row is not None
