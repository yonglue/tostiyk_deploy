import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.models import AutoPart, Client, Order

def test_pos_credit_limit_exceeded(client: TestClient, session: Session):
    """测试信用额度拦截：尝试挂账超过信用额度，必须返回 400 且欠款不增加"""
    # 1. 准备数据：一个只有 5 库存、售价 $10 的商品（税费设为0，方便断言）
    part = AutoPart(oem="TEST-POS-001", name="POS测试件", brand="GENERAL", stock=5, price=10.0, cost_price=5.0, tax_rate=0.0)
    session.add(part)
    
    # 2. 准备客户：当前欠款 $90，信用上限 $100（还能挂 10 块，但我们要买 20 块）
    client_obj = Client(name="额度测试客户", debt=90.0, credit_limit=100.0)
    session.add(client_obj)
    session.commit()

    # 3. 发起 POST 请求：买 2 个，总价 $20，支付方式为挂账 (Fiado)
    payload = {
        "client_id": client_obj.id,
        "client_name": client_obj.name,
        "bcv_rate": 40.0, 
        "payment_method": "Fiado_USD", # 挂账
        "items": [
            {"oem": "TEST-POS-001", "name": "POS测试件", "brand": "GENERAL", "quantity": 2, "price": 10.0}
        ]
    }
    
    res = client.post("/api/pos/orders", json=payload)
    
    # 4. 断言：必须拦截成功（返回 400 且提示超出信用额度）
    assert res.status_code == 400
    assert "超出客户信用额度" in res.json()["detail"]
    
    # 5. 断言：数据库里的客户欠款依然停留在 90，没被脏写
    session.expire_all()
    updated_client = session.get(Client, client_obj.id)
    assert updated_client.debt == 90.0
    
    # 6. 断言：商品库存没被扣减
    updated_part = session.exec(select(AutoPart).where(AutoPart.oem == "TEST-POS-001")).first()
    assert updated_part.stock == 5
    print(f"\n✅ 信用额度拦截测试通过：欠款保持 ${updated_client.debt}，库存保持 {updated_part.stock}")

def test_pos_normal_checkout(client: TestClient, session: Session):
    """测试正常收银：现金结账，扣减库存"""
    part = AutoPart(oem="TEST-POS-002", name="现金测试件", brand="GENERAL", stock=10, price=15.0, cost_price=10.0, tax_rate=0.0)
    session.add(part)
    session.commit()

    payload = {
        "client_name": "Cliente General",
        "bcv_rate": 40.0,
        "payment_method": "Cash_USD", # 现金
        "items": [
            {"oem": "TEST-POS-002", "name": "现金测试件", "brand": "GENERAL", "quantity": 3, "price": 15.0}
        ]
    }

    res = client.post("/api/pos/orders", json=payload)
    assert res.status_code == 200, f"收银失败: {res.text}"

    # 验证库存扣减
    session.expire_all()
    updated_part = session.exec(select(AutoPart).where(AutoPart.oem == "TEST-POS-002")).first()
    assert updated_part.stock == 7 # 10 - 3 = 7
    print(f"\n✅ 正常收银测试通过：库存成功扣减至 {updated_part.stock}")
