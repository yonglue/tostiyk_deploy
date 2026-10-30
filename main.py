"""便捷启动入口。

应用装配在 ``app.main``（官方入口，见 start.sh / Dockerfile /
.github/workflows/ci.yml / README）。

本模块仅提供 ``python main.py`` 的快速本地启动方式。
测试与脚本请直接 ``from app.main import app``，不要依赖本模块。
"""

from app.database import engine, get_session, init_db
from app.main import app
from app.models import (
    AdminUser,
    AuditLog,
    AutoPart,
    CashRegisterSession,
    Client,
    ClientPaymentRecord,
    InventoryTransaction,
    Order,
    OrderItem,
    PurchaseOrder,
    QuotationRecord,
    StaffUser,
    Supplier,
)
from app.security import hash_password, verify_password
from app.services.audit import log_action

__all__ = [
    "app",
    "engine",
    "get_session",
    "init_db",
    "log_action",
    "hash_password",
    "verify_password",
    "AdminUser",
    "AuditLog",
    "AutoPart",
    "CashRegisterSession",
    "Client",
    "ClientPaymentRecord",
    "InventoryTransaction",
    "Order",
    "OrderItem",
    "PurchaseOrder",
    "QuotationRecord",
    "StaffUser",
    "Supplier",
]


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
