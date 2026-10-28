<template>
  <!-- 🌟 修复：把 h-screen 换成 h-[100dvh]，解决地址栏伸缩导致的溢出 -->
  <div class="h-[100dvh] w-screen flex flex-col bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 overflow-hidden">
    
    <!-- 核心内容区 -->
    <main class="flex-1 relative overflow-hidden">
      <Transition name="fade-slide" mode="out-in">
        <!-- 🌟 修复：给顶部加上 pt-safe，避免内容顶进状态栏 -->
        <div :key="activeTab" class="absolute inset-0 overflow-y-auto pb-[calc(68px+env(safe-area-inset-bottom))] pt-[env(safe-area-inset-top)]">
          <component :is="currentView" v-if="currentView" />
        </div>
      </Transition>
    </main>

    <!-- 底部导航 (5 个 Tab) -->
    <!-- 🌟 修复：给底部加上 pb-safe，避免被 iOS 的底部横条遮挡 -->
    <nav class="fixed bottom-0 left-0 right-0 bg-white/95 dark:bg-slate-900/95 backdrop-blur-xl border-t border-slate-100 dark:border-slate-800 flex items-center justify-around z-50 shrink-0 pb-[env(safe-area-inset-bottom)] h-[calc(68px+env(safe-area-inset-bottom))]">
      <button
        v-for="tab in tabs" :key="tab.key"
        @click="activeTab = tab.key"
        class="flex flex-col items-center justify-center w-full h-[68px] gap-1 transition-colors"
        :class="activeTab === tab.key ? 'text-blue-600 dark:text-blue-400' : 'text-slate-400 dark:text-slate-500'"
      >
        <component :is="tab.icon" :size="20" :stroke-width="activeTab === tab.key ? 2.4 : 1.8" />
        <span class="text-[10px] font-semibold">{{ tab.label }}</span>
      </button>
    </nav>
    
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Home, Package, ArrowRightLeft, Users, Settings } from 'lucide-vue-next'
import { useI18n } from '../composables/useI18n'
import { useTheme } from '../composables/useTheme'
import { usePlugins } from '../composables/usePlugins'

import MobileDashboardView from './MobileDashboardView.vue'
import MobileProductsView from './MobileProductsView.vue'
import MobileTransactionsView from './MobileTransactionsView.vue'
import MobileClientsView from './MobileClientsView.vue'
import MobileSettingsView from './MobileSettingsView.vue'

useTheme()

const { currentLang } = useI18n()
const { getMobileTabs } = usePlugins()
const activeTab = ref('home')

// icon 组件表（lucide 依赖保持在 MobileLayout 内，不进 registry）
const ICON_MAP = {
  Home,
  Package,
  ArrowRightLeft,
  Users,
  Settings,
}

// 视图组件表
const VIEW_MAP = {
  MobileDashboardView,
  MobileProductsView,
  MobileTransactionsView,
  MobileClientsView,
  MobileSettingsView,
}

// label 多语言映射（与 Sidebar 的 ICON_MAP 同构：数据在 manifest，映射表在组件）
const MOBILE_LABELS = {
  home:         { zh: '首页', es: 'Inicio',      en: 'Home' },
  products:     { zh: '产品', es: 'Productos',   en: 'Products' },
  transactions: { zh: '流水', es: 'Movimientos', en: 'History' },
  clients:      { zh: '客户', es: 'Clientes',    en: 'Clients' },
  mine:         { zh: '我的', es: 'Mi Perfil',   en: 'Me' },
}

const tabs = computed(() => {
  const lang = currentLang.value === 'zh' ? 'zh' : currentLang.value === 'es' ? 'es' : 'en'
  return getMobileTabs().map((t) => ({
    key: t.key,
    label: MOBILE_LABELS[t.labelKey]?.[lang] || t.labelKey,
    icon: ICON_MAP[t.iconName],
    componentKey: t.componentKey,
  }))
})

const currentView = computed(() => {
  const tab = tabs.value.find((t) => t.key === activeTab.value)
  return tab ? VIEW_MAP[tab.componentKey] : null
})
</script>

<style scoped>
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.25s cubic-bezier(0.25, 1, 0.5, 1);
}
.fade-slide-enter-from {
  opacity: 0;
  transform: translateX(10px);
}
.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(-10px);
}
</style>
