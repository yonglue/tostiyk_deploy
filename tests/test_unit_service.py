"""主子单位换算服务测试。"""
from decimal import Decimal

import pytest
from sqlmodel import Session, SQLModel, create_engine

from app import plugins  # noqa: F401
plugins.install_models()

from app.models import AutoPart
from app.plugins.fmcg.models import ProductUnit
from app.plugins.fmcg.services import unit as us
from app.plugins.fmcg.services.exceptions import FmcgError


@pytest.fixture()
def engine(tmp_path):
    eng = create_engine(f"sqlite:///{tmp_path}/test.db")
    tables = [
        t for name, t in SQLModel.metadata.tables.items()
        if name in ("fmcg_product_unit", "autopart", "client")
    ]
    SQLModel.metadata.create_all(eng, tables=tables)
    return eng


def _seed(s: Session, oem: str = "SKU-1") -> int:
    p = AutoPart(oem=oem, name="Test Item")
    s.add(p); s.commit(); s.refresh(p)
    return p.id


def _seed_units(s: Session, pid: int):
    s.add(ProductUnit(product_id=pid, code="unit", name="Unidad",
                      is_base=True, qty_per_base=Decimal("1")))
    s.add(ProductUnit(product_id=pid, code="pack", name="Paquete",
                      is_base=False, qty_per_base=Decimal("6")))
    s.add(ProductUnit(product_id=pid, code="box", name="Caja",
                      is_base=False, qty_per_base=Decimal("24")))
    s.commit()


def test_resolve_base_unit_returns_same_qty(engine):
    with Session(engine) as s:
        pid = _seed(s)
        _seed_units(s, pid)
        assert us.resolve_to_base(s, pid, "unit", 3) == Decimal("3.0000")


def test_resolve_pack_multiplies_by_6(engine):
    with Session(engine) as s:
        pid = _seed(s)
        _seed_units(s, pid)
        assert us.resolve_to_base(s, pid, "pack", 2) == Decimal("12.0000")


def test_resolve_box_multiplies_by_24(engine):
    with Session(engine) as s:
        pid = _seed(s)
        _seed_units(s, pid)
        assert us.resolve_to_base(s, pid, "box", 2) == Decimal("48.0000")


def test_resolve_decimal_quantity(engine):
    with Session(engine) as s:
        pid = _seed(s)
        _seed_units(s, pid)
        # 0.5 箱 = 12 瓶
        assert us.resolve_to_base(s, pid, "box", Decimal("0.5")) == Decimal("12.0000")


def test_resolve_rejects_non_positive(engine):
    with Session(engine) as s:
        pid = _seed(s)
        _seed_units(s, pid)
        with pytest.raises(FmcgError):
            us.resolve_to_base(s, pid, "box", 0)
        with pytest.raises(FmcgError):
            us.resolve_to_base(s, pid, "box", -1)


def test_resolve_unknown_unit_code(engine):
    with Session(engine) as s:
        pid = _seed(s)
        _seed_units(s, pid)
        with pytest.raises(FmcgError):
            us.resolve_to_base(s, pid, "pallet", 1)


def test_resolve_to_base_int_rounds(engine):
    with Session(engine) as s:
        pid = _seed(s)
        _seed_units(s, pid)
        assert us.resolve_to_base_int(s, pid, "box", 2) == 48
        # 0.3 箱 = 7.2 瓶 → 四舍五入到 7
        assert us.resolve_to_base_int(s, pid, "box", Decimal("0.3")) == 7


def test_get_base_unit_requires_exactly_one(engine):
    with Session(engine) as s:
        pid = _seed(s)
        # 完全没定义单位
        with pytest.raises(FmcgError):
            us.get_base_unit(s, pid)

        # 定义两个 base（非法状态）
        s.add(ProductUnit(product_id=pid, code="a", name="A", is_base=True, qty_per_base=1))
        s.add(ProductUnit(product_id=pid, code="b", name="B", is_base=True, qty_per_base=1))
        s.commit()
        with pytest.raises(FmcgError):
            us.get_base_unit(s, pid)
