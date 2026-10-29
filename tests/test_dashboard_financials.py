# tests/test_dashboard_financials.py
"""
测试老板驾驶舱 (Dashboard Stats) 的财务数据准确性：
1. 基础库存资金占用
2. 应收账款 (客户欠款)
3. 应付账款 (供应商欠款)
4. 本月销售额与毛利计算
5. 低库存预警数量
"""
from fastapi.testclient import TestClient
from datetime import datetime
from app.models import AutoPart, Client, Supplier, Order, OrderItem
from sqlmodel import Session

def test_dashboard_stats_financials(client: TestClient, session: Session):
    """
    构造精准数据，验证看板计算结果是否完全吻合。
    """
    # ==================== 1. 准备测试数据 ====================
    
    # 1.1 商品：成本 10，售价 15，当前库存 2，最低库存 5（触发预警）
    part = AutoPart(oem="TEST-DASH-01", name="测试商品", cost_price=10.0, price=15.0, stock=2, min_stock=5)
    session.add(part)
    
    # 1.2 客户：欠款 $100
    client_db = Client(name="欠款客户", debt=100.0)
    session.add(client_db)
    
    # 1.3 供应商：欠款 $200
    supplier = Supplier(name="欠款供应商", debt_usd=200.0)
    session.add(supplier)
    
    session.commit()
    
    # 1.4 模拟一笔本月完成的 POS 订单 (卖出 2 个，产生销售额 $30，成本 $20，毛利 $10)
    order = Order(
        order_no="TEST-ORDER-DASH",
        client_name="散客",
        operator="tester",
        base_amount_usd=30.0,
        total_usd=30.0,
        total_bs=30.0 * 36.5,
        bcv_rate=36.5,
        payment_method="Cash_USD",
        status="COMPLETED",
        created_at=datetime.now() # 确保计入本月
    )
    session.add(order)
    session.commit() # 获取 order.id
    
    order_item = OrderItem(
        order_id=order.id,
        part_id=part.id,
        oem=part.oem,
        name=part.name,
        quantity=2,
        price_usd=15.0,
        subtotal_usd=30.0,
        cost_price_usd=10.0, # 这里的成本快照必须是 10
        base_quantity=2
    )
    session.add(order_item)
    session.commit()

    # ==================== 2. 调用接口 ====================
    # 去掉了 headers=auth_headers，直接请求
    response = client.get("/api/dashboard/stats")
    assert response.status_code == 200
    data = response.json()

    # ==================== 3. 断言验证 ====================
    
    # 验证应收账款 (客户总欠款)
    assert data["total_receivables"] == 100.0
    
    # 验证应付账款 (供应商总欠款)
    assert data["total_payables"] == 200.0
    
    # 验证本月销售额 (卖出 30)
    assert data["monthly_sales"] == 30.0
    
    # 验证本月预估毛利 (销售额 30 - 成本 20 = 10)
    assert data["monthly_profit"] == 10.0
    
    # 验证低库存预警 (2 <= 5 且 min_stock > 0，所以应该有 1 个)
    assert data["low_stock_count"] == 1
    
    # 验证库存资金占用 (库存 2 * 成本 10 = 20)
    assert data["total_inventory_usd"] == 20.0