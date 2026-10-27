"""POS 多单位集成测试：直接调 create_pos_order，绕过权限链。

覆盖 6 种场景：
1. 不传 unit_code（老路径）→ 行为不变
2. 传 unit_code 但商品无 unit 定义（纯汽配）→ 回落恒等，不报错
3. 传 box（qty_per_base=24）qty=2 → 扣 48 库存
4. 传主单位 code → 恒等
5. 库存不足应拒绝
6. 传未知 unit_code → 400
"""
from decimal import Decimal
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from sqlmodel import Session, SQLModel, create_engine, select

from app import plugins  # noqa: F401
plugins.install_models()

from app.models import AutoPart, InventoryTransaction, OrderItem
from app.plugins.fmcg.models import ProductUnit
from app.routers.pos import create_pos_order
from app.schemas import POSItemPayload, POSOrderCreatePayload


@pytest.fixture()
def engine(tmp_path):
    eng = create_engine(f"sqlite:///{tmp_path}/pos.db")
    wanted = (
        "autopart", "client", "orders", "order_items",
        "inventorytransaction", "auditlog", "fmcg_product_unit",
    )
    tables = [
        t for name, t in SQLModel.metadata.tables.items()
        if name in wanted
    ]
    SQLModel.metadata.create_all(eng, tables=tables)
    return eng


def _actor():
    return SimpleNamespace(username="tester", role="super_admin")


def _payload(items, **over):
    base = dict(
        client_name="Cliente General",
        payment_method="Cash_USD",
        bcv_rate=Decimal("36.50"),
        items=items,
    )
    base.update(over)
    return POSOrderCreatePayload(**base)


def _item(oem="SKU-1", name="Test Item", qty=2, price=Decimal("10"),
          unit_code=None, brand="GENERAL"):
    return POSItemPayload(
        oem=oem, name=name, brand=brand,
        quantity=qty, price=price, unit_code=unit_code,
    )


def test_no_unit_code_falls_back_to_legacy_behavior(engine):
    with Session(engine) as s:
        p = AutoPart(oem="SKU-A", name="Bujia", stock=100, price=10)
        s.add(p); s.commit()

        result = create_pos_order(
            payload=_payload([_item(oem="SKU-A", qty=3)]),
            actor=_actor(), session=s,
        )
        assert result["status"] == "success"

        oi = s.exec(select(OrderItem)).first()
        assert oi.quantity == 3
        assert oi.base_quantity == 3
        assert oi.unit_code is None

        s.refresh(p)
        assert p.stock == 97


def test_with_unit_code_but_no_units_defined_falls_back(engine):
    with Session(engine) as s:
        p = AutoPart(oem="SKU-B", name="Filtro", stock=50, price=8)
        s.add(p); s.commit()

        result = create_pos_order(
            payload=_payload([_item(oem="SKU-B", qty=2, unit_code="box")]),
            actor=_actor(), session=s,
        )
        assert result["status"] == "success"
        s.refresh(p)
        assert p.stock == 48

        oi = s.exec(select(OrderItem)).first()
        assert oi.quantity == 2
        assert oi.base_quantity == 2


def test_box_unit_multiplies_stock_deduction(engine):
    with Session(engine) as s:
        p = AutoPart(oem="SKU-C", name="Aceite", stock=100, price=120)
        s.add(p); s.commit(); s.refresh(p)
        s.add(ProductUnit(product_id=p.id, code="unit", name="Unidad",
                          is_base=True, qty_per_base=Decimal("1")))
        s.add(ProductUnit(product_id=p.id, code="box", name="Caja",
                          is_base=False, qty_per_base=Decimal("24")))
        s.commit()

        create_pos_order(
            payload=_payload([_item(oem="SKU-C", qty=2, price=Decimal("120"),
                                    unit_code="box")]),
            actor=_actor(), session=s,
        )

        s.refresh(p)
        assert p.stock == 52

        oi = s.exec(select(OrderItem)).first()
        assert oi.quantity == 2
        assert oi.base_quantity == 48
        assert oi.unit_code == "box"

        it = s.exec(select(InventoryTransaction)).first()
        assert it.quantity == 48


def test_base_unit_code_equals_quantity(engine):
    with Session(engine) as s:
        p = AutoPart(oem="SKU-D", name="Item", stock=20, price=5)
        s.add(p); s.commit(); s.refresh(p)
        s.add(ProductUnit(product_id=p.id, code="unit", name="Unidad",
                          is_base=True, qty_per_base=Decimal("1")))
        s.add(ProductUnit(product_id=p.id, code="box", name="Caja",
                          is_base=False, qty_per_base=Decimal("24")))
        s.commit()

        create_pos_order(
            payload=_payload([_item(oem="SKU-D", qty=5, price=Decimal("5"),
                                    unit_code="unit")]),
            actor=_actor(), session=s,
        )
        s.refresh(p)
        assert p.stock == 15
        oi = s.exec(select(OrderItem)).first()
        assert oi.quantity == 5
        assert oi.base_quantity == 5


def test_insufficient_stock_with_unit_conversion(engine):
    with Session(engine) as s:
        p = AutoPart(oem="SKU-E", name="Item", stock=20, price=120)
        s.add(p); s.commit(); s.refresh(p)
        s.add(ProductUnit(product_id=p.id, code="unit", name="Unidad",
                          is_base=True, qty_per_base=Decimal("1")))
        s.add(ProductUnit(product_id=p.id, code="box", name="Caja",
                          is_base=False, qty_per_base=Decimal("24")))
        s.commit()

        with pytest.raises(HTTPException) as ei:
            create_pos_order(
                payload=_payload([_item(oem="SKU-E", qty=2,
                                        price=Decimal("120"), unit_code="box")]),
                actor=_actor(), session=s,
            )
        assert ei.value.status_code == 400
        assert "库存不足" in ei.value.detail

        s.refresh(p)
        assert p.stock == 20


def test_unknown_unit_code_rejected(engine):
    with Session(engine) as s:
        p = AutoPart(oem="SKU-F", name="Item", stock=10, price=10)
        s.add(p); s.commit(); s.refresh(p)
        s.add(ProductUnit(product_id=p.id, code="unit", name="Unidad",
                          is_base=True, qty_per_base=Decimal("1")))
        s.commit()

        with pytest.raises(HTTPException) as ei:
            create_pos_order(
                payload=_payload([_item(oem="SKU-F", qty=1, unit_code="pallet")]),
                actor=_actor(), session=s,
            )
        assert ei.value.status_code == 400
