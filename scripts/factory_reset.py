"""出厂重置：清空所有业务数据，保留 admin 与 system_settings。"""
import os
import sys

# 🌟 核心修复：将项目根目录加入 sys.path，确保能找到 app 模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, text
from app.database import engine

# 需要清空的业务表（注意顺序，先清子表再清主表）
TABLES_TO_CLEAR = [
    "order_items",
    "orders",
    "held_orders",
    "clientpaymentrecord",
    "inventorytransaction",
    "purchase_orders",
    "supplierpaymentrecord",
    "quotationrecord",
    "expenses",
    "auditlog",
    "cashregistersession",
    "autopart",
    "client",
    "suppliers",
]

def factory_reset():
    print("🚨 即将执行【出厂重置】：清空所有业务数据！")
    print("⚠️  admin 账号和系统设置将被保留。")
    confirm = input("确认执行请输入大写 'RESET': ")
    if confirm != "RESET":
        print("❌ 已取消。")
        return

    with Session(engine) as session:
        # SQLite 仅在主键声明 AUTOINCREMENT 时才创建 sqlite_sequence 表；
        # SQLModel 默认的 INTEGER PRIMARY KEY 不会建它，因此先一次性探测。
        has_sqlite_sequence = session.exec(
            text("SELECT 1 FROM sqlite_master "
                 "WHERE type='table' AND name='sqlite_sequence'")
        ).first() is not None

        for table in TABLES_TO_CLEAR:
            try:
                session.exec(text(f"DELETE FROM {table};"))
                if has_sqlite_sequence:
                    # 重置自增 ID（仅当存在 sqlite_sequence 时）
                    session.exec(text(
                        f"DELETE FROM sqlite_sequence WHERE name='{table}';"
                    ))
                print(f"  ✅ 已清空: {table}")
            except Exception as e:
                print(f"  ⚠️ 跳过 {table}: {e}")
        session.commit()

    print("\n🎉 出厂重置完成！数据库已恢复为 0 数据状态。")
    print("   管理员账号仍为: admin")

if __name__ == "__main__":
    factory_reset()
