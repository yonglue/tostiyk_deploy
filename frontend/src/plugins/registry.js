/**
 * 前端插件注册表。
 *
 * 说明：
 * - 本文件是前端唯一的"哪些行业插件可用"的事实来源。
 * - enabled=false 的插件：manifest 保留，但 UI 不渲染其 tab、路由不加载。
 * - 后续 4.1.x 会把 Sidebar / App.vue / MobileLayout 的 tab 定义迁移到这里。
 * - 当前里程碑只声明插件，不动任何现有 DOM。
 */

export const PLUGINS = Object.freeze({
  core: {
    code: 'core',
    label: '核心',
    description: '通用 POS/ERP 核心：汇率、双币、多通道支付、SENAT 小票、Cierre',
    enabled: true,
  },
  auto_parts: {
    code: 'auto_parts',
    label: '汽配',
    description: 'OEM 交叉检索、车型适配、修理厂挂账',
    enabled: true,
  },
  fmcg: {
    code: 'fmcg',
    label: '超市/快消',
    description: '多包装单位、称重码、组合包、找零钱包',
    // 🚧 阶段 4.2 完成 POS 前端集成后翻 true
    enabled: false,
  },
})

export function isPluginEnabled(code) {
  return PLUGINS[code]?.enabled === true
}

export function listEnabledPlugins() {
  return Object.values(PLUGINS).filter((p) => p.enabled)
}


/**
 * 桌面端侧边栏 tab 分组清单。
 *
 * 约束：
 * - 顺序、item key、labelKey、requiredPerm 必须与 Sidebar.vue 原来的硬编码完全一致。
 * - icon 用 iconName 字符串（lucide-vue-next 的具名导出），Sidebar 侧维护 ICON_MAP。
 * - plugin 字段决定该 group 是否需要插件启用：未启用的插件对应 group 会被过滤。
 */
export const DESKTOP_TAB_GROUPS = Object.freeze([
  {
    plugin: 'core',
    titleKey: 'groupCore',
    items: [
      { key: 'dashboard', iconName: 'LayoutDashboard' },
      { key: 'financial', iconName: 'TrendingUp', requiredPerm: 'financial:view' },
      { key: 'expenses', iconName: 'TrendingDown', requiredPerm: 'financial:view' },
    ],
  },
  {
    plugin: 'auto_parts',
    titleKey: 'groupWarehouse',
    items: [
      { key: 'parts', iconName: 'Package', requiredPerm: 'parts:view' },
      { key: 'inventory_audit', labelKey: 'inventoryAudit', iconName: 'ClipboardList', requiredPerm: 'parts:manage' },
    ],
  },
  {
    plugin: 'core',
    titleKey: 'groupSales',
    items: [
      { key: 'clients', iconName: 'Users', requiredPerm: 'clients:view' },
      { key: 'procurement', iconName: 'ShoppingCart', requiredPerm: 'procurement:view' },
      { key: 'transactions', iconName: 'History', requiredPerm: 'transactions:history' },
      { key: 'pos', iconName: 'Calculator', requiredPerm: 'pos:access' },
      { key: 'quotation', labelKey: 'quotation', iconName: 'FileText', requiredPerm: 'pos:access' },
      { key: 'quotations', labelKey: 'quotations', iconName: 'History', requiredPerm: 'pos:access' },
      { key: 'cash_register', labelKey: 'cashRegister', iconName: 'FileText', requiredPerm: 'shift:report' },
    ],
  },
  {
    plugin: 'core',
    titleKey: 'groupSystem',
    items: [
      { key: 'staff', iconName: 'ShieldCheck', requiredPerm: 'users:manage' },
      { key: 'audit_logs', labelKey: 'auditLogs', iconName: 'ShieldAlert', requiredPerm: 'users:manage' },
      { key: 'backup', iconName: 'Database', requiredPerm: 'settings:manage' },
    ],
  },
])

/**
 * 返回经过插件开关过滤后的 tab 分组。
 * @param {(code: string) => boolean} isPluginEnabled
 */
export function getDesktopTabGroups(isPluginEnabled) {
  return DESKTOP_TAB_GROUPS
    .filter((g) => isPluginEnabled(g.plugin))
    .map((g) => ({ titleKey: g.titleKey, items: g.items }))
}
