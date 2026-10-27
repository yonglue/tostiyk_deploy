<!-- src/components/Sidebar.vue -->
<template>
  <div 
    v-if="mobileMenuOpen" 
    @click="$emit('update:mobileMenuOpen', false)"
    class="fixed inset-0 bg-slate-950/45 backdrop-blur-md z-20 md:hidden transition-opacity"
  ></div>

  <aside 
    :class="[
      'fixed md:static inset-y-0 left-0 z-30 bg-gradient-to-b from-white to-slate-50/50 dark:from-slate-900 dark:to-slate-900/95 border-r border-slate-200/60 dark:border-slate-800/60 shadow-[1px_0_10px_rgba(0,0,0,0.02)] flex flex-col transition-all duration-300 shrink-0 relative group/sidebar',
      mobileMenuOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0',
      isCollapsed ? 'w-[64px]' : 'w-[224px]'
    ]"
  >
    
        <!-- Logo 区域 -->
    <div :class="['h-16 border-b border-slate-200/60 dark:border-slate-800 flex items-center shrink-0 bg-white/40 dark:bg-slate-900/40 transition-all', isCollapsed ? 'justify-center px-0' : 'justify-between px-3']">
      
      <!-- 展开状态：显示 Logo 和标题 -->
      <div v-show="!isCollapsed" @click.stop.prevent="handleMenuClick('dashboard')" class="flex items-center gap-3 overflow-hidden cursor-pointer hover:opacity-80 transition-opacity" title="返回主页">
        <div class="w-9 h-9 min-w-[36px] rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/25 shrink-0">
          <Cpu :size="20" />
        </div>
        <div class="whitespace-nowrap transition-opacity duration-300">
          <h1 class="font-bold text-sm tracking-tight text-slate-900 dark:text-white">TOSTIKYK ERP</h1>
          <p class="text-[10px] text-slate-400 dark:text-slate-500 font-medium tracking-wide">Automotive Parts System</p>
        </div>
      </div>
      
      <!-- 桌面端折叠/展开按钮 (常驻原位) -->
      <button type="button" @click.stop="toggleSidebar" class="hidden md:flex p-1.5 text-slate-400 bg-transparent hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-700 dark:text-slate-500 rounded-lg cursor-pointer transition-colors" :title="isCollapsed ? '展开' : '折叠'">
        <!-- 图标根据折叠状态切换 -->
        <svg v-if="isCollapsed" xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 text-slate-500 hover:text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
        </svg>
      </button>
      
      <!-- 移动端关闭按钮 -->
      <button type="button" @click="$emit('update:mobileMenuOpen', false)" class="md:hidden p-1.5 text-slate-400 hover:text-slate-700 dark:text-slate-500 dark:hover:text-slate-300 rounded-lg cursor-pointer">
        ✕
      </button>
    </div>

    <!-- 导航菜单列表 -->
    <nav class="flex-1 px-3 py-4 space-y-3 overflow-y-auto overflow-x-hidden custom-scrollbar">
      <div v-for="(group, groupIndex) in groupedMenuItems" :key="groupIndex" class="space-y-1">
        
        <!-- 分组标题 -->
        <div v-show="!isCollapsed" @click.stop.prevent="toggleGroup(groupIndex)" class="flex items-center justify-between px-3 pb-1 text-[11px] font-bold tracking-wider text-slate-400 dark:text-slate-500 uppercase cursor-pointer hover:text-slate-700 dark:hover:text-slate-300 transition-colors select-none">
          <span>{{ group.title }}</span>
          <svg xmlns="http://www.w3.org/2000/svg" :class="['w-3 h-3 transition-transform duration-300', collapsedGroups.includes(groupIndex) ? '-rotate-90' : '']" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
          </svg>
        </div>
        
        <!-- 组内菜单项 -->
        <div v-show="isCollapsed || !collapsedGroups.includes(groupIndex)" class="space-y-0.5">
          <button
            type="button"
            v-for="item in group.items"
            :key="item.key"
            :data-testid="`nav-${item.key}`"
            @click.stop.prevent="handleMenuClick(item.key)"
            :title="isCollapsed ? t.menu[item.labelKey || item.key] : ''"
            :class="[
              'w-full flex items-center rounded-lg font-bold text-sm tracking-wide transition-all duration-200 cursor-pointer relative group',
              isCollapsed ? 'justify-center px-0 py-2.5 my-1' : 'px-2.5 py-2 my-0.5',
              activeTab === item.key 
                ? 'bg-blue-50/80 text-blue-700 dark:bg-blue-500/10 dark:text-blue-400' 
                : 'text-slate-700 dark:text-slate-300 hover:bg-slate-100/80 dark:hover:bg-slate-800/60 hover:text-slate-900 dark:hover:text-slate-100'
            ]"
          >
            <!-- 激活态左侧小竖条 -->
            <div v-if="activeTab === item.key" class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-4 bg-blue-600 dark:bg-blue-500 rounded-r-full pointer-events-none"></div>
            
            <component :is="item.icon" :size="18" :class="['shrink-0 transition-colors', activeTab === item.key ? 'text-blue-600 dark:text-blue-400' : 'text-slate-400 group-hover:text-slate-600 dark:text-slate-500 dark:group-hover:text-slate-300']" />
            <span v-show="!isCollapsed" class="truncate leading-tight text-left whitespace-nowrap ml-3">
              {{ t.menu[item.labelKey || item.key] }}
            </span>
          </button>
        </div>

        <!-- 组间分隔线 -->
        <div v-if="groupIndex < groupedMenuItems.length - 1" class="pt-2.5 mx-3 border-b border-slate-200/50 dark:border-slate-700/50"></div>
      </div>
    </nav>

    <!-- 底部实时时间胶囊 -->
    <div class="p-3 border-t border-slate-200/60 dark:border-slate-800 shrink-0 bg-white/40 dark:bg-slate-900/40 flex flex-col gap-2">

      <div 
        class="w-full h-10 bg-white/80 dark:bg-slate-800/80 backdrop-blur-md rounded-xl flex items-center justify-center border border-white/80 dark:border-slate-700 shadow-sm text-xs font-mono font-semibold text-slate-700 dark:text-slate-300 transition-all overflow-hidden"
        :class="isCollapsed ? 'px-0' : 'px-3 gap-2'"
      >
        <span v-show="!isCollapsed" class="truncate tabular-nums tracking-wide">{{ currentDateTime }}</span>
        <span v-if="isCollapsed" class="text-[10px] text-center leading-tight text-slate-500 dark:text-slate-400 tabular-nums">
          {{ currentDateTime.split(' ')[1] || '⏱' }}
        </span>
      </div>
    </div>

    
  </aside>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from '../composables/useI18n'
import { useAuth } from '../composables/useAuth'
import { usePlugins } from '../composables/usePlugins'
import { getDesktopTabGroups } from '../plugins/registry'
import { 
  Cpu, LayoutDashboard, TrendingUp, TrendingDown, Package, ShieldCheck, 
  Users, ShoppingCart, History, Calculator, FileText, Database, ShieldAlert, ClipboardList 
} from 'lucide-vue-next'

const props = defineProps({
  activeTab: String,
  mobileMenuOpen: Boolean,
  currentDateTime: String,
  isCollapsed: { type: Boolean, default: false }
})

const emit = defineEmits([
  'update:activeTab', 
  'update:mobileMenuOpen', 
  'update:isCollapsed', 
  'update:is-collapsed', 
  'menu-click'
])

const { t } = useI18n()
const { currentUserObj } = useAuth()
const { isPluginEnabled } = usePlugins()

const handleMenuClick = (key) => {
  emit('update:activeTab', key)
  emit('update:mobileMenuOpen', false)
  emit('menu-click', key)
}

const toggleSidebar = () => {
  emit('update:isCollapsed', !props.isCollapsed)
  emit('update:is-collapsed', !props.isCollapsed)
}

const collapsedGroups = ref([])
const toggleGroup = (index) => {
  if (collapsedGroups.value.includes(index)) {
    collapsedGroups.value = collapsedGroups.value.filter(i => i !== index)
  } else {
    collapsedGroups.value.push(index)
  }
}

// 🌟 4.1.2：tab 分组从 manifest 读取（icons 保留在 Sidebar 侧，避免 lucide 耦合到 registry）
const ICON_MAP = {
  LayoutDashboard,
  TrendingUp,
  TrendingDown,
  Package,
  ClipboardList,
  Users,
  ShoppingCart,
  History,
  Calculator,
  FileText,
  ShieldCheck,
  ShieldAlert,
  Database,
}

const groupedMenuItems = computed(() => {
  const groups = getDesktopTabGroups(isPluginEnabled).map((g) => ({
    title: t.value.menu[g.titleKey],
    items: g.items.map((item) => {
      // 显式构造：输出对象结构与原硬编码完全一致（不含 iconName 残留）
      const mapped = { key: item.key, icon: ICON_MAP[item.iconName] }
      if (item.labelKey) mapped.labelKey = item.labelKey
      if (item.requiredPerm) mapped.requiredPerm = item.requiredPerm
      return mapped
    }),
  }))

  const role = currentUserObj.value?.role || 'staff'
  const userPerms = currentUserObj.value?.permissions || []

  return groups.map(group => {
    const filteredItems = group.items.filter(item => {
      if (role === 'super_admin' || role === 'admin' || userPerms.includes('*')) return true
      if (item.requiredPerm) return userPerms.includes(item.requiredPerm)
      return true
    })
    return { title: group.title, items: filteredItems }
  }).filter(group => group.items.length > 0)
})
</script>

<style scoped>
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: transparent transparent; 
  transition: scrollbar-color 0.3s ease;
}
.custom-scrollbar:hover {
  scrollbar-color: rgba(255, 255, 255, 0.6) transparent; 
}
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: transparent; 
  border-radius: 10px;
  transition: background-color 0.3s ease;
}
.custom-scrollbar:hover::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.6); 
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: rgba(255, 255, 255, 0.95); 
}
</style>
