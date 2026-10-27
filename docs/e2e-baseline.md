# E2E Baseline Failures（大段 1 结束时记录）

记录时间：2026-10-27（大段 1 插件骨架完成后）
后端：9 passed / 0 failed
E2E：12 passed / 3 failed

## 失败清单（前端 selector 漂移，非逻辑 bug）

1. `app-smoke.spec.js:34` — 侧边栏激活态
   - 断言: `toHaveClass(/bg-blue-600/)`
   - 实际: `bg-blue-50/80 text-blue-700`
   - 原因: Tailwind 配色升级为深色模式友好
   - 修法（大段 4 一并处理）: 改测试为 `/bg-blue-(50\/80|600)/`

2. `pos-quote.spec.js:35` — 结账后购物车为空文案
   - 断言: `/购物车为空|Carrito vacío|Cart is empty/`
   - 原因: UI 文案或结构变化
   - 修法（大段 4 一并处理）: 重写 PosCart 空状态组件时同步 selector

3. `pos-quote.spec.js:76` — 历史补打弹窗
   - 现象: 45s 超时
   - 疑似: print-agent 未在测试环境启动 / PosHistoryModal selector 漂移
   - 修法（大段 4 一并处理）: E2E fixture 里启动 print-agent，或改 selector

## 不在本次修复的原因

大段 4/5 会重写前端路由、组件、selector，现在修会被推翻。


---

## 已知框架陷阱（FastAPI 0.143.0）

- `app.include_router(...)` 不再平铺子路由到 `app.routes`，而是包成 `_IncludedRouter`。
- 检查 app 路由存在性请用 `app.openapi()["paths"]`，不要遍历 `app.routes`。
- 所有"路由数量 / 路径存在性"的新测试已按此约定编写，见 `tests/test_wallet_api.py`。

## 待清理的技术债（不阻塞当前阶段）

- `staff.py` 有 Duplicate Operation ID 警告，疑似路由被注册两次或函数命名冲突
- `AUTO_CREATE_TABLES=1` 会掩盖 Alembic 问题（大段 2 已改用 autogenerate 绕过）
- E2E 3 项 selector 漂移（见上文）
