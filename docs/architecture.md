# Tostiyk ERP 架构文档

> 版本：v1.0（大段 6.1 完成时）
> 面向：核心团队 / 新加入的开发者 / 需要了解系统约束的外部集成方
> 本文档回答最初的 4 个架构问题，并给出已实现的代码引用与未来演进方向。

---

## 0. TL;DR

| 问题 | 答案摘要 |
|------|---------|
| 前后端如何解耦 | 后端 `app/plugins/` 插件注册表；前端 `src/plugins/registry.js` manifest 驱动 |
| Multi-Empaque / Monedero Schema | 4 张 `fmcg_*` 表，金额全 Numeric，钱包双表（余额冗余 + 流水 append-only） |
| 离线同步方案 | IndexedDB + Sync Queue + `apiFetch` 注入式钩子 + 幂等键（`request_id`） |
| 重构路线图 | 6 阶段渐进式，见第 4 节 |

**当前状态**：所有 FMCG 能力可被 POS 直接调用，且完全向后兼容；离线开单（含商品搜索）能力已通过 E2E 验证；E2E baseline `29/0`。

---

## 1. 架构拆分与设计：核心通用 + 行业插件

### 1.1 后端分层

`app/` 目录结构：

- `app/plugins/` 是插件体系根目录
  - `base.py` 定义 `BasePlugin` 抽象（`code` / `name` / `permissions` / `register_routes` / `register_models`）
  - `registry.py` 提供 `register()` / `all_plugins()` / `install_models()` / `install_routes()`
  - `auto_parts/` 汽配专属（OEM / 车型 / 挂账）
  - `fmcg/` 超市快消专属（多单位 / 钱包 / 未来促销引擎）
- `app/routers/` / `app/models.py` 是当前通用核心（未来抽出 `app/core/`）

**加载时序**（`app/main.py:bootstrap()`）：

1. `from app import plugins` → 触发 registry.register()
2. `plugins.install_models()` → 每个插件 import 自己的 models
3. `alembic upgrade head` → 迁移自动识别插件表
4. `plugins.install_routes(app)` → 挂载插件端点

**为什么这样拆**：

- 删除 `app/plugins/fmcg/` 不影响 POS 核心
- 新行业接入只需 3 个文件
- 共享表用 ForeignKey 引用，避免数据复制

### 1.2 前端分层

- `src/plugins/registry.js` 是唯一事实来源：`PLUGINS` + `DESKTOP_TAB_GROUPS`
- `src/composables/usePlugins.js` 提供 `isPluginEnabled()` / `listEnabledPlugins()`
- `Sidebar.vue` 从 `getDesktopTabGroups(isPluginEnabled)` 读 tab
- `App.vue` 里 15 个 `v-else-if` 分支保留结构，只加 `isPluginEnabled('xxx')` 条件

**为什么不用 `<component :is>` 完全动态化**：15 个 View 的 props 会失去类型推断，改动风险高。

### 1.3 请求链路

- `apiFetch` → 核心 router → 插件服务（unit.resolve_to_base_int）→ 核心写库
- 单向依赖：核心可依赖插件服务，插件不反向依赖核心 router


---

## 2. 数据库 Schema 设计

### 2.1 Multi-Empaque（多包装单位）

**问题**：一个商品有箱/包/单瓶，价格与库存需按主单位统一核算。

**表结构**（`app/plugins/fmcg/models.py`）：

    class ProductUnit(SQLModel, table=True):
        __tablename__ = "fmcg_product_unit"
        __table_args__ = (Index("uq_fmcg_unit_product_code", "product_id", "code", unique=True),)
        id: Optional[int] = Field(default=None, primary_key=True)
        product_id: int = Field(foreign_key="autopart.id", index=True)
        code: str           # "box" / "pack" / "unit"
        name: str
        is_base: bool       # True 那行是主单位
        qty_per_base: Decimal = Field(max_digits=12, decimal_places=4)
        barcode: Optional[str]

    class ProductPrice(SQLModel, table=True):
        __tablename__ = "fmcg_product_price"
        __table_args__ = (Index("uq_fmcg_price_dim", "product_id", "unit_id", "price_tier", unique=True),)
        product_id: int
        unit_id: int
        price_tier: str     # "retail" / "wholesale"
        price_usd: Decimal

**设计决策**：

| 决策 | 理由 |
|------|------|
| 金额用 Numeric(12,4) | SQLite 里 Float 是双精度浮点，1.15 存成 1.1499... |
| is_base 业务层保证唯一 | DB 无法用简单约束表达"每组只允许 1 个 True" |
| 单价与包装绑定 | 整箱优惠价 ≠ 单瓶价 × 24 |
| 条码放 ProductUnit | 一个商品 3 个包装 3 个条码 |

**库存扣减**（`app/routers/pos.py:_resolve_base_qty`）：

- `unit_code` 为空 → 恒等（老路径）
- 商品无 unit 定义（纯汽配）→ 恒等，不报错
- 否则 → `unit_service.resolve_to_base_int()` 折算

**向后兼容**：`OrderItem` 加 `unit_code` + `base_quantity`，老订单 `base_quantity = quantity` 由 Alembic 迁移 UPDATE 回填。

### 2.2 Monedero（找零钱包）

**问题**：委内瑞拉缺外币找零，需挂账到客户手机号，下次可抵。

**方案**：双表分离（余额冗余 + 流水 append-only）。

    class Wallet(SQLModel, table=True):
        __tablename__ = "fmcg_wallet"
        __table_args__ = (Index("uq_fmcg_wallet_phone_ccy", "customer_phone", "currency", unique=True),)
        customer_phone: str
        customer_id: Optional[int] = Field(foreign_key="client.id")
        currency: str        # USD / VES / USDT
        balance: Decimal     # 冗余列

    class WalletLedger(SQLModel, table=True):
        __tablename__ = "fmcg_wallet_ledger"
        __table_args__ = (
            Index("ix_fmcg_ledger_wallet_ts", "wallet_id", "created_at"),
            Index("uq_fmcg_ledger_ref", "ref_type", "ref_id", unique=True),  # 幂等键
        )
        wallet_id: int = Field(foreign_key="fmcg_wallet.id")
        tx_type: str           # credit / debit / adjustment
        amount: Decimal        # 有符号
        balance_after: Decimal # 快照
        ref_type: str
        ref_id: Optional[str]

**设计决策**：

| 决策 | 理由 |
|------|------|
| 余额冗余 + 流水真相 | 单纯读余额需 sum 全表，收银 10ms 都影响体验 |
| 幂等键 (ref_type, ref_id) | 重试、网络抖动、误触只入账一次 |
| amount 有符号 | sum(amount) == balance 是设计不变量 |
| balance_after 快照 | 事后对账不需重算所有历史流水 |

**核心 API**（`services/wallet.py`）：

- `credit()` / `debit()`：同一事务里 UPDATE balance + INSERT ledger
- `credit_change_short()`：找零不足场景，校验 order 存在 + COMPLETED + 金额 ≤ order.total

**为什么不用单表 + version 乐观锁**：

- 对账困难（并发写"最后一行"不确定）
- 幂等靠应用层 check-then-write 有 race
- SENAT 稽查要求"每条余额变动可追溯"

---

## 3. 离线同步方案

### 3.1 技术栈

| 层 | 选择 | 理由 |
|----|------|------|
| 存储 | IndexedDB（原生 API 封装） | 500MB+ 容量，事务性；不引 dexie 减依赖 |
| 队列 | `pending_orders` store | 3 个 store：orders / cached_parts / meta |
| 触发 | `online` event + 手动点击 | SW 被 block，不用 Background Sync |
| 幂等 | `request_id` = `local_id` | 后端 `Order.request_id` 唯一索引 |
| 冲突 | LWW + 业务幂等键 | 财务交易禁止自动合并 |

### 3.2 Sync Queue 结构

    // pending_orders（keyPath: 'local_id'）
    {
      local_id: "uuid-v4",
      request_id: "uuid-v4",       // 幂等键
      enqueued_at: "2026-...",     // FIFO 排序
      items: [...],
      payment_method: "...",
      bcv_rate: 887,
      total_usd: ...
    }

**流程**：

1. 断网结账 → `fetch` 抛错 → `_offlineEnqueue()` 存 IndexedDB → 返回合成 202
2. 联网恢复 → `online` event → `useOfflineQueue.flush()` → 逐条 POST
3. 200 → 从队列删除；4xx → 保留 + 中止本轮；5xx → 保留 + 中止本轮

### 3.3 冲突解决

| 冲突类型 | 策略 |
|---------|------|
| 重复提交 | 幂等键 `request_id` 唯一索引 |
| 离线订单同步时商品改价 | 用离线时点的价快照 |
| 离线订单同步时库存不足 | 拒绝 + 保留队列 + 人工介入 |
| 钱包多笔离线入账 | FIFO 顺序应用，每笔独立幂等 |
| 时钟不一致 | 金额用本地快照；后端只验证上限 |

**核心原则**：财务交易类禁止自动合并。

### 3.4 Service Worker 双角色

**生产环境**：SW 注册（缓存 + 未来 Background Sync）
**E2E 环境**：`playwright.config.js` 里 `serviceWorkers: 'block'`

- 原因：SW 会绕过 `page.route` / `context.route` 直接 fetch，导致断网模拟失效

### 3.5 cached_parts 填充（6.1 完成）

**问题**：离线开单最大障碍不是 POST 请求，而是离线查商品。

**方案**：

- `cached_parts.keyPath: 'id'`（修复同 OEM 多品牌覆盖）
- `fetchParts` 缓存优先：首屏读缓存秒开 + 网络成功覆盖写缓存 + 网络失败兜底读缓存
- POS 搜索是 `props.partsList.filter(...)` 本地过滤，缓存填充后离线可用

---

## 4. 重构路线图

### 4.1 已完成（大段 1–6.1）

| 阶段 | 内容 | 关键 commit |
|------|------|------------|
| 大段 1 | 插件骨架（base/registry） | cb745db |
| 大段 2.1 | FMCG 4 张表 + 单测 | 15e524d |
| 大段 2.2 | Alembic 迁移 | 15e524d |
| 大段 2.3 | 钱包服务层 + REST 端点 | 5eba941 |
| 大段 3.A | POS 多单位 + 找零入账 | 69948bb + 62c4874 |
| 大段 4.1 | 前端 manifest + Sidebar 迁移 | 650abd5 |
| 大段 4.2 | FMCG 钱包视图 | 53e6827 + 371240b |
| 大段 4.3 | IndexedDB 队列 + 指示器 + apiFetch 钩子 | 79218a6 + b1314f9 + 936d3b9 |
| 大段 4.4 | POS 接离线入队 + SW block | a4565d7 |
| 大段 6.1 | cached_parts 填充 + 离线搜索开单 | d9ed4f8 |

**E2E 里程碑**：

- 起点：12/3（3 项 selector 漂移）
- 大段 2 后：26/0（baseline 清零）
- 大段 4.4 后：28/0
- 大段 6.1 后：**29/0**

### 4.2 待办（大段 6.2+）

| 优先级 | 内容 |
|--------|------|
| P2 | MobileLayout 插件化（6.2） |
| P2 | Service Worker 缓存策略（6.3） |
| P3 | 技术债：staff.py Duplicate Operation ID、AUTO_CREATE_TABLES=0、根目录 sim 脚本归档 |
| P3 | 多租户/多店（大段 7，涉及所有表 + 权限） |

---

## 5. 关键约束与教训

### 5.1 框架陷阱（写新代码必读）

| 陷阱 | 教训 |
|------|------|
| FastAPI 0.143 include_router 包 _IncludedRouter | 路由断言用 `app.openapi()["paths"]` |
| SQLModel + Alembic 输出 AutoString | 手动改 `sa.String(length=N)` |
| Playwright `page.route` 不拦 SW | config 里 `serviceWorkers: 'block'` |
| Playwright `route.abort` 对所有 method 生效 | 断网测试明确 `if (method !== 'POST') continue` |
| Playwright `unroute` 函数引用不匹配 | 用开关变量而非 unroute |
| reload 后 Sidebar/modal 动画导致 stability 检查失败 | `evaluate(el => el.click())` |
| Vue props 数组 splice 是否生效 | 需 App.vue 传真实响应式 ref |
| 结账流程的 await 链阻塞 UI | 后台任务 fire-and-forget 化 |
| `receiptData` 在 confirmAndPrint 里不存在 | 变量作用域陷阱，改 `props.cartItems.map` |
| `useInventory()` 在 page.evaluate 里是不同实例 | E2E 诊断用 `getAllParts()` 直读缓存 |

### 5.2 数据不变量（写新代码前必读）

1. `sum(WalletLedger.amount) == Wallet.balance`
2. `OrderItem.base_quantity == OrderItem.quantity`（`unit_code IS NULL` 时）
3. `InventoryTransaction.quantity == OrderItem.base_quantity`
4. `(ref_type, ref_id)` 唯一（WalletLedger / Order.request_id）
5. Alembic `alembic_version` 单一 HEAD

### 5.3 测试分层

| 层 | 工具 | 覆盖 |
|----|------|------|
| 单元 | pytest | 14 条 DB 模型 + 服务层 |
| API 集成 | pytest + TestClient | 8 条 |
| E2E | Playwright | 29 条 |

**快速反馈技巧**：

- `--last-failed`：只跑上次失败的（~10s）
- `--workers=4` + isolated spec（~5s）
- 改敏感文件（App.vue / PosView / api.js / config）必须全量

---

## 6. 附录：文件索引

| 关注点 | 文件 |
|--------|------|
| 插件契约 | `app/plugins/base.py` |
| 插件注册 | `app/plugins/__init__.py` |
| FMCG 表定义 | `app/plugins/fmcg/models.py` |
| 钱包服务 | `app/plugins/fmcg/services/wallet.py` |
| 多单位服务 | `app/plugins/fmcg/services/unit.py` |
| 钱包 API | `app/plugins/fmcg/routers/wallet.py` |
| 前端 manifest | `frontend/src/plugins/registry.js` |
| 离线 DB | `frontend/src/offline/db.js` |
| 离线队列 | `frontend/src/composables/useOfflineQueue.js` |
| 离线指示器 | `frontend/src/components/OfflineIndicator.vue` |
| 前端 apiFetch | `frontend/src/utils/api.js` |
| POS 主流程 | `frontend/src/components/PosView.vue` |
| E2E baseline 记录 | `docs/e2e-baseline.md` |

---

**文档版本**：v1.0（大段 6.1 完成）
**下次更新**：大段 6.2/6.3 完成后
