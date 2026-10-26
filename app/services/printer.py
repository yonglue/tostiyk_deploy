import logging

logger = logging.getLogger("tk.printer")

def print_receipt(data: dict) -> dict:
    # 现在完全由前端浏览器负责排版和调起系统打印机
    # 后端仅作简单的日志记录，不碰任何硬件驱动
    order_no = data.get('order_no', 'UNKNOWN')
    total = data.get('total_usd', 0.0)
    logger.info(f"[前端打印模式] 记录订单: {order_no}, 金额: ${total:.2f}")
    return {"ok": True, "mode": "frontend_handled"}

def print_test_page() -> dict:
    return {"ok": True, "message": "Test handled by frontend"}

def printer_status() -> dict:
    return {"mode": "frontend_browser_print"}
