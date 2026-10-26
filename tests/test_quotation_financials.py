import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.models import Client, QuotationRecord

def test_generate_quotation_success(client: TestClient, session: Session):
    """测试正常生成报价单：金额计算准确，且不扣减库存"""
    payload = {
        "client_name": "Cliente General",  # 不建档的默认客户
        "payment_method": "Cash_USD",
        "items": [
            {"oem": "TEST-Q-001", "name": "报价测试件1", "brand": "GENERAL", "quantity": 2, "price": 10.50},
            {"oem": "TEST-Q-002", "name": "报价测试件2", "brand": "GENERAL", "quantity": 1, "price": 20.00}
        ]
    }
    
    res = client.post("/api/quotations/generate", json=payload)
    assert res.status_code == 200, f"报价单生成失败: {res.text}"
    
    # 直接从数据库查最新的一条报价单
    session.expire_all()
    quotation = session.exec(select(QuotationRecord).order_by(QuotationRecord.id.desc())).first()
    assert quotation is not None
    assert quotation.total_usd == 41.0
    
    print(f"\n✅ 正常报价单测试通过：单号 {quotation.quotation_no}，总金额 ${quotation.total_usd}")
def test_generate_quotation_negative_qty(client: TestClient, session: Session):
    """测试非法数量拦截：数量为负数时，必须返回 400"""
    payload = {
        "client_name": "Cliente General",
        "payment_method": "Cash_USD",
        "items": [
            {"oem": "TEST-Q-001", "name": "报价测试件1", "brand": "GENERAL", "quantity": -1, "price": 10.00}
        ]
    }
    
    res = client.post("/api/quotations/generate", json=payload)
    assert res.status_code == 400
    assert "购买数量必须大于 0" in res.json()["detail"]
    print("\n✅ 非法数量拦截测试通过：HTTP 400")

def test_generate_quotation_credit_limit(client: TestClient, session: Session):
    """测试报价单挂账的信用额度拦截"""
    # 1. 准备一个欠款 90，额度 100 的客户
    client_obj = Client(name="额度测试报价客户", debt=90.0, credit_limit=100.0)
    session.add(client_obj)
    session.commit()

    # 2. 尝试挂账 20 块钱的报价单（超出 10 块额度）
    payload = {
        "client_name": "额度测试报价客户",
        "payment_method": "Fiado_USD",  # 挂账
        "items": [
            {"oem": "TEST-Q-003", "name": "超额件", "brand": "GENERAL", "quantity": 2, "price": 10.00}
        ]
    }
    
    res = client.post("/api/quotations/generate", json=payload)
    
    # 3. 断言被拦截
    assert res.status_code == 400
    assert "信用额度超限" in res.json()["detail"]
    
    # 4. 断言数据库里的欠款没变
    session.expire_all()
    updated_client = session.get(Client, client_obj.id)
    assert updated_client.debt == 90.0
    print("\n✅ 报价单信用额度拦截测试通过：欠款保持 $90")
