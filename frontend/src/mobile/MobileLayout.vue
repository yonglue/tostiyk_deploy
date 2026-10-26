<template>
  <!-- 🌟 修复：把 h-screen 换成 h-[100dvh]，解决地址栏伸缩导致的溢出 -->
  <div class="h-[100dvh] w-screen flex flex-col bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 overflow-hidden">
    
    <!-- 核心内容区 -->
    <main class="flex-1 relative overflow-hidden">
      <Transition name="fade-slide" mode="out-in">
        <!-- 🌟 修复：给顶部加上 pt-safe，避免内容顶进状态栏 -->
        <div :key="activeTab" class="absolute inset-0 overflow-y-auto pb-[calc(68px+env(safe-area-inset-bottom))] pt-[env(safe-area-inset-top)]">
          <MobileDashboardView v-if="activeTab === 'home'" />
          <MobileProductsView v-else-if="activeTab === 'products'" />
          <MobileTransactionsView v-else-if="activeTab === 'transactions'" />
          <MobileClientsView v-else-if="activeTab === 'clients'" />
          <MobileSettingsView v-else-if="activeTab === 'mine'" />
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

import MobileDashboardView from './MobileDashboardView.vue'
import MobileProductsView from './MobileProductsView.vue'
import MobileTransactionsView from './MobileTransactionsView.vue'
import MobileClientsView from './MobileClientsView.vue'
import MobileSettingsView from './MobileSettingsView.vue'

useTheme()

const { currentLang } = useI18n()
const activeTab = ref('home')

const tabs = computed(() => {
  const isZh = currentLang.value === 'zh'
  const isEs = currentLang.value === 'es'
  return [
    { key: 'home', label: isZh ? '首页' : isEs ? 'Inicio' : 'Home', icon: Home },
    { key: 'products', label: isZh ? '产品' : isEs ? 'Productos' : 'Products', icon: Package },
    { key: 'transactions', label: isZh ? '流水' : isEs ? 'Movimientos' : 'History', icon: ArrowRightLeft },
    { key: 'clients', label: isZh ? '客户' : isEs ? 'Clientes' : 'Clients', icon: Users },
    { key: 'mine', label: isZh ? '我的' : isEs ? 'Mi Perfil' : 'Me', icon: Settings }
  ]
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
