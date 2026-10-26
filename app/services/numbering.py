import random
import string
import datetime
import uuid

def _random_digits(k=4) -> str:
    return ''.join(random.choices(string.digits, k=k))

def make_order_no() -> str:
    """生成 POS 收银订单号 (TK-xxxx-xxxx)"""
    return f"TK-{_random_digits(4)}-{_random_digits(4)}"

def make_po_no() -> str:
    """生成采购订单号 (PO-YYYYMMDD-XXXX)"""
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    return f"PO-{date_str}-{_random_digits(4)}"

def make_quotation_no() -> str:
    """生成报价单号 (QT-YYYYMMDD-XXXX)"""
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    return f"QT-{date_str}-{_random_digits(4)}"

def make_transaction_no() -> str:
    """生成交易流水号 (TX-YYYYMMDD-XXXX)"""
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    return f"TX-{date_str}-{_random_digits(4)}"

def make_request_id() -> str:
    """生成唯一请求 ID，防止重复提交"""
    return str(uuid.uuid4())
