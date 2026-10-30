# tests/test_multi_tier_pricing.py
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.models import AutoPart, Client, Order, OrderItem

def test_create_part_with_multi_prices(client: TestClient, session: Session):
    """
    测试 1：后端能够正确接收并保存商品的 4 个级别价格。
    """
    # 使用 Form 数据提交，模拟前端新增商品
    data = {
        "oem": "TEST-VIP-PART-01",
        "name": "多级价格测试商品",
        "brand": "GENERAL",
        "category": "测试类",
        "stock": "100",
        "price": "15.00",           # 零售
        "wholesale_price": "12.00", # VIP1
        "vip2_price": "10.00",      # VIP2
        "vip3_price": "8.00",       # VIP3
        "cost_price": "5.00",
        "tax_rate": "0.16"
    }
    response = client.post("/api/parts", data=data)
    assert response.status_code == 200, response.text
    
    # 验证数据库是否存对了
    part = session.exec(select(AutoPart).where(AutoPart.oem == "TEST-VIP-PART-01")).first()
    assert part is not None
    assert part.price == 15.00
    assert part.wholesale_price == 12.00
    assert part.vip2_price == 10.00
    assert part.vip3_price == 8.00

@pytest.mark.skip(reason="Client.price_tier 字段已从模型移除（迁移 4f7b4846ede7 遗留）；当前系统无客户价格分级功能")
def test_create_client_with_price_tier(client: TestClient, session: Session):
    """
    测试 2：后端能够正确保存客户的价格等级 (price_tier)。
    """
    payload = {
        "name": "VIP2级核心代理",
        "phone": "04141234567",
        "price_tier": "VIP2",  # 核心测试点
        "address": "Valencia"
    }
    response = client.post("/api/clients", json=payload)
    assert response.status_code == 200, response.text
    
    client_db = session.exec(select(Client).where(Client.name == "VIP2级核心代理")).first()
    assert client_db is not None
    assert client_db.price_tier == "VIP2"

def test_pos_checkout_with_vip_price(client: TestClient, session: Session):
    """
    测试 3：POS 收银时，前端传入了 VIP 价格 (如 10.00)。
    后端应据此计算订单总价，并正确扣减库存、记录成本快照。
    """
    # 1. 准备商品数据：库存 10，进价 5
    part = AutoPart(
        oem="TEST-POS-VIP", name="POS VIP测试", stock=10, 
        price=15.0, wholesale_price=12.0, vip2_price=10.0, vip3_price=8.0, 
        cost_price=5.0, tax_rate=0.16
    )
    session.add(part)
    session.commit()
    
    # 2. 模拟前端 POS 下单（选中 VIP2 客户，单价按 vip2_price 传 10.00）
    order_payload = {
        "client_name": "VIP2级核心代理",
        "payment_method": "Cash_USD",
        "bcv_rate": 36.5,
        "items": [
            {
                "oem": "TEST-POS-VIP",
                "name": "POS VIP测试",
                "brand": "GENERAL",
                "quantity": 2,       # 买 2 个
                "price": 10.00,      # 单价锁定 VIP2 价格
                "tax_rate": 0.16
            }
        ]
    }
    
    response = client.post("/api/pos/orders", json=order_payload)
    assert response.status_code == 200, response.text
    data = response.json()
    order_id = data["order_id"]
    
    # 3. 验证库存是否扣减：原本 10，买 2，剩 8
    session.refresh(part)
    assert part.stock == 8
    
    # 4. 验证订单金额和明细快照
    order = session.get(Order, order_id)
    assert order is not None
    # 总价 = 2 * 10 = 20 (因为含税，此处 total_usd 为 20)
    assert order.total_usd == 20.00
    
    # 验证订单明细 (OrderItem) 里的价格和成本快照
    items = session.exec(select(OrderItem).where(OrderItem.order_id == order_id)).all()
    assert len(items) == 1
    assert items[0].price_usd == 10.00  # 确认下单价格被正确记录
    assert items[0].cost_price_usd == 5.00  # 成本快照被正确记录，用于后续算毛利