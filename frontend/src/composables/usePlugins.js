/**
 * 插件状态 composable。
 *
 * 注意：这是包装层。目前所有 tab 数据仍由 Sidebar / App.vue 硬编码，
 * 4.1.2 起逐步改为从 usePlugins().listDesktopTabs() / .listMobileTabs() 读取。
 * 现在只提供 isEnabled 查询，方便有条件渲染时使用。
 */
import { computed } from 'vue'
import {
  PLUGINS,
  isPluginEnabled,
  listEnabledPlugins,
} from '../plugins/registry'

export function usePlugins() {
  const enabledPlugins = computed(() => listEnabledPlugins())
  const enabledCodes = computed(() => enabledPlugins.value.map((p) => p.code))

  return {
    plugins: PLUGINS,
    enabledPlugins,
    enabledCodes,
    isPluginEnabled,
  }
}
