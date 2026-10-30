# Alembic 迁移链历史与异常记录

## 迁移链现状（截至 2026-10-29）

- HEAD: `cleanup_orphans_01`
- BASE: `082a363b8b44` (initial_migration)
- 总步数: 22（含 `cleanup_orphans_01`）

## ⚠️ 异常记录：`2a213f4f4a7e` 原始迁移文件丢失（不可删除）

- **原始文件名**：`2a213f4f4a7e_add_stock_alerts_and_adjustment_table.py`
- **当前状态**：文件丢失，仅剩编译产物 `__pycache__/2a213f4f4a7e_add_stock_alerts_and_adjustment_table.cpython-314.pyc`
- **现仓库中同名 revision**：`2a213f4f4a7e_stub.py`（占位壳，文件内注释已写明 "stub placeholder for missing revision 2a213f4f4a7e"）
- **🚫 禁止删除 `2a213f4f4a7e_stub.py`**：删除会使 `4f7b4846ede7` 的 `down_revision` 指向不存在的 revision，整条链断裂，`alembic upgrade head` 会失败
- **该原始迁移曾建立**：`inventory_adjustment` 表 + `autopart.stock_alert` 列
- **已处理**：`cleanup_orphans_01` 已清理 `inventory_adjustment` 表（当时 0 行、全代码无引用）

## 本次新增迁移：`cleanup_orphans_01`

清理历史遗留的模型/DB 漂移（`alembic check` 原报 4 处差异，现已归零）：

1. **删除孤儿表 `inventory_adjustment`** —— 原始迁移 `2a213f4f4a7e` 文件丢失导致建表动作"失忆"，此表从未被 drop，但 0 行、全代码无引用
2. **删除 `client.price_tier` 列** —— 迁移 `4f7b4846ede7` upgrade 加过该列，但模型已删、DB 未 drop
3. **`autopart.vip2_price` / `vip3_price` 收紧为 NOT NULL** —— 与模型声明 `float = Field(default=0.0)` 对齐

## 维护原则

1. **不可修改任何历史迁移文件的 `revision` / `down_revision`** —— 已 stamp 的 DB 会与链断开
2. **不可删除任何 `.py` 迁移文件** —— 即使它是 stub / 空迁移
3. 新增迁移一律用 `alembic revision -m "..."` 生成骨架，**在 head 之后追加**，不要重排
4. `alembic check` 必须保持 `No new upgrade operations detected.` —— 若报差异，说明模型与 DB 漂移，需补迁移而不是手改 DB
5. SQLite 不支持 `SELECT ... FOR UPDATE`，行锁方案需参考 README 的"数据一致性规则"

## 已知未完成（TODO，非本次范围）

- `app/routers/parts.py` 的 `update_part` 路由**仍不接收** `wholesale_price/vip2_price/vip3_price` 三个 Form 字段 —— 创建能设、更新不能改，属未完成的多级定价功能
- `tests/conftest.py` 用 `sqlite:///:memory:` + `StaticPool`（README 已明确说不能这么配并发测试），当前串行跑未爆，一旦加并发用例会挂
