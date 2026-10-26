import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.models import Client, ClientPaymentRecord

def test_client_partial_repayment(client: TestClient, session: Session):
    """测试正常部分还款：欠款 $100，还 $40，剩 $60"""
    # 1. 准备客户
    client_obj = Client(name="正常还款客户", debt=100.0, credit_limit=500.0)
    session.add(client_obj)
    session.commit()

    # 2. 发起还款请求
    payload = {
        "client_name": "正常还款客户",
        "amount_paid": 40.0,
        "currency": "USD",
        "payment_method": "Cash_USD"
    }
    res = client.post("/api/clients/repay", json=payload)
    assert res.status_code == 200, f"还款失败: {res.text}"

    # 3. 断言欠款变为 60
    session.expire_all()
    updated_client = session.get(Client, client_obj.id)
    assert updated_client.debt == 60.0

    # 4. 断言生成了一条还款流水记录
    payment = session.exec(select(ClientPaymentRecord).where(ClientPaymentRecord.client_name == "正常还款客户")).first()
    assert payment is not None
    assert payment.amount_usd == 40.0
    print(f"\n✅ 正常还款测试通过：欠款从 $100 降至 ${updated_client.debt}")

def test_client_overpayment_bug(client: TestClient, session: Session):
    """测试超额还款拦截（目前后端存在漏洞，此测试预期会失败）"""
    # 1. 准备客户：只欠 $10
    client_obj = Client(name="超额还款客户", debt=10.0, credit_limit=500.0)
    session.add(client_obj)
    session.commit()

    # 2. 尝试还款 $50
    payload = {
        "client_name": "超额还款客户",
        "amount_paid": 50.0,
        "currency": "USD",
        "payment_method": "Cash_USD"
    }
    res = client.post("/api/clients/repay", json=payload)
    
    # 3. 期望后端应该拦截并报错 (由于现在没写拦截，这里会 AssertionError 失败)
    session.expire_all()
    updated_client = session.get(Client, client_obj.id)
    
    assert res.status_code == 400, f"❌ 发现漏洞：系统允许超额还款，客户欠款变成了 ${updated_client.debt}"
