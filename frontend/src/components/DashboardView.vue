<!-- src/components/DashboardView.vue -->
<template>
  <div class="space-y-6 max-w-11xl mx-auto">
    
    <!-- 欢迎横幅 (恢复经典的蓝紫渐变，与系统主色调完美统一) -->
    <div class="bg-gradient-to-r from-blue-700 to-indigo-800 dark:from-blue-900 dark:to-indigo-900 rounded-xl p-5 sm:p-6 text-white shadow-sm border border-transparent dark:border-slate-700 flex flex-col justify-center transition-colors">
      <div>
        <h1 class="text-xl sm:text-2xl md:text-3xl font-black tracking-tight">{{ t.dashboard.title }}</h1>
        <p class="text-blue-100 text-xs sm:text-sm mt-1 font-medium">{{ t.dashboard.subtitle }}</p>
      </div>
    </div>

    <!-- 📊 核心指标卡片网格 -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
      
      <!-- 卡片 1 (统一主色调底) -->
      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 sm:p-5 border border-slate-200 dark:border-slate-700 shadow-sm hover:border-blue-400 dark:hover:border-blue-600 transition-colors duration-200 flex flex-col justify-between">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">{{ t.dashboard.assetTitle }}</span>
          <div class="w-10 h-10 rounded-lg bg-accent/10 text-accent flex items-center justify-center">
            <Package :size="20" />
          </div>
        </div>
        <div class="mt-4">
          <div class="text-2xl sm:text-3xl font-black text-slate-900 dark:text-slate-100 font-mono">
            $ {{ formatNumber(stats.total_inventory_usd) }}
          </div>
          <div class="text-xs text-slate-400 dark:text-slate-500 font-mono mt-1">
            Bs. {{ formatNumber(stats.total_inventory_bs) }}
          </div>
        </div>
      </div>

      <!-- 卡片 2 (统一主色调底) -->
      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 sm:p-5 border border-slate-200 dark:border-slate-700 shadow-sm hover:border-blue-400 dark:hover:border-blue-600 transition-colors duration-200 flex flex-col justify-between">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">{{ t.dashboard.salesTitle }}</span>
          <div class="w-10 h-10 rounded-lg bg-accent/10 text-accent flex items-center justify-center">
            <TrendingUp :size="20" />
          </div>
        </div>
        <div class="mt-4">
          <div class="text-2xl sm:text-3xl font-black text-slate-900 dark:text-slate-100 font-mono">
            $ {{ formatNumber(stats.total_sales_usd) }}
          </div>
          <div class="text-xs text-slate-400 dark:text-slate-500 font-mono mt-1">
            Bs. {{ formatNumber(stats.total_sales_bs) }}
          </div>
        </div>
      </div>

      <!-- 卡片 3 (统一主色调底) -->
      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 sm:p-5 border border-slate-200 dark:border-slate-700 shadow-sm hover:border-blue-400 dark:hover:border-blue-600 transition-colors duration-200 flex flex-col justify-between">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">{{ t.dashboard.skuTitle }}</span>
          <div class="w-10 h-10 rounded-lg bg-accent/10 text-accent flex items-center justify-center">
            <Layers :size="20" />
          </div>
        </div>
        <div class="mt-4">
          <div class="text-2xl sm:text-3xl font-black text-slate-900 dark:text-slate-100 font-mono">
            {{ stats.total_skus || 0 }} <span class="text-sm">{{ tExt.itemsUnit }}</span>
          </div>
          <div class="text-xs text-slate-400 dark:text-slate-500 mt-1">{{ t.dashboard.skuSub }}</div>
        </div>
      </div>

      <!-- 卡片 4 (保留唯一需要警示的红色) -->
      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 sm:p-5 border border-slate-200 dark:border-slate-700 shadow-sm hover:border-blue-400 dark:hover:border-blue-600 transition-colors duration-200 flex flex-col justify-between">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">{{ t.dashboard.warningTitle }}</span>
          <div class="w-10 h-10 rounded-lg bg-rose-50 text-rose-600 dark:bg-rose-500/10 dark:text-rose-400 flex items-center justify-center">
            <AlertTriangle :size="20" />
          </div>
        </div>
        <div class="mt-4">
          <div class="text-2xl sm:text-3xl font-black text-rose-600 dark:text-rose-400 font-mono">
            {{ stats.low_stock_count || 0 }} <span class="text-sm">{{ tExt.itemsUnit }}</span>
          </div>
          <div class="text-xs text-slate-400 dark:text-slate-500 mt-1">{{ t.dashboard.warningSub }}</div>
        </div>
      </div>

    </div>

    <!-- 动态趋势图 -->
    <div class="bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-200 dark:border-slate-700 shadow-sm">
      <div class="flex items-center justify-between mb-4">
        <h3 class="font-bold text-slate-800 dark:text-slate-200 text-base flex items-center gap-2">
          <TrendingUp :size="18" class="text-accent" />
          {{ tExt.chartTitle }}
        </h3>
        <!-- 🌟 日期选择器 -->
        <div class="w-36">
          <BaseSelect 
            v-model="timeRange" 
            :options="[
              { label: tExt.timeRange7, value: 7 },
              { label: tExt.timeRange30, value: 30 }
            ]" 
            size="sm"
          />
        </div>
      </div>
      <div class="h-72 w-full">
        <TrendChart :dates="chartData.dates" :amounts="chartData.amounts" />
      </div>
    </div>

    <!-- 🚀 快捷业务直达面板 (统一极简灰底，悬浮显示主色调) -->
    <div class="bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-200 dark:border-slate-700 shadow-sm space-y-4">
      <h3 class="font-bold text-slate-800 dark:text-slate-200 text-base flex items-center gap-2">
        <Zap :size="18" class="text-amber-500" />
        {{ tExt.quickNavTitle }}
      </h3>
      <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
        
        <!-- 快速收银 -->
        <button @click="$emit('navigate', 'pos')" class="bg-slate-50 dark:bg-slate-900/50 hover:bg-blue-50 dark:hover:bg-blue-900/20 border border-slate-200 dark:border-slate-700 p-4 rounded-xl font-bold text-xs flex flex-col items-center gap-3 transition-all cursor-pointer shadow-sm group">
          <ShoppingCart :size="24" class="text-slate-400 group-hover:text-accent transition-colors" />
          <span class="text-slate-700 dark:text-slate-300 group-hover:text-accent transition-colors">{{ tExt.btnPos }}</span>
        </button>

        <!-- 开单报价 -->
        <button @click="$emit('navigate', 'quotation')" class="bg-slate-50 dark:bg-slate-900/50 hover:bg-blue-50 dark:hover:bg-blue-900/20 border border-slate-200 dark:border-slate-700 p-4 rounded-xl font-bold text-xs flex flex-col items-center gap-3 transition-all cursor-pointer shadow-sm group">
          <FileText :size="24" class="text-slate-400 group-hover:text-accent transition-colors" />
          <span class="text-slate-700 dark:text-slate-300 group-hover:text-accent transition-colors">{{ tExt.btnQuote }}</span>
        </button>

        <!-- 财务利润 -->
        <button @click="$emit('navigate', 'financial')" class="bg-slate-50 dark:bg-slate-900/50 hover:bg-blue-50 dark:hover:bg-blue-900/20 border border-slate-200 dark:border-slate-700 p-4 rounded-xl font-bold text-xs flex flex-col items-center gap-3 transition-all cursor-pointer shadow-sm group">
          <TrendingUp :size="24" class="text-slate-400 group-hover:text-accent transition-colors" />
          <span class="text-slate-700 dark:text-slate-300 group-hover:text-accent transition-colors">{{ tExt.btnFinancial }}</span>
        </button>

        <!-- 配件库存 -->
        <button @click="$emit('navigate', 'parts')" class="bg-slate-50 dark:bg-slate-900/50 hover:bg-blue-50 dark:hover:bg-blue-900/20 border border-slate-200 dark:border-slate-700 p-4 rounded-xl font-bold text-xs flex flex-col items-center gap-3 transition-all cursor-pointer shadow-sm group">
          <Boxes :size="24" class="text-slate-400 group-hover:text-accent transition-colors" />
          <span class="text-slate-700 dark:text-slate-300 group-hover:text-accent transition-colors">{{ tExt.btnParts }}</span>
        </button>

        <!-- 客户与账本 -->
        <button @click="$emit('navigate', 'clients')" class="bg-slate-50 dark:bg-slate-900/50 hover:bg-blue-50 dark:hover:bg-blue-900/20 border border-slate-200 dark:border-slate-700 p-4 rounded-xl font-bold text-xs flex flex-col items-center gap-3 transition-all cursor-pointer shadow-sm group">
          <Users :size="24" class="text-slate-400 group-hover:text-accent transition-colors" />
          <span class="text-slate-700 dark:text-slate-300 group-hover:text-accent transition-colors">{{ tExt.btnClients }}</span>
        </button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
// 🌟 补全了缺失的 Boxes 图标
import { Package, TrendingUp, Users, AlertTriangle, Layers, ShoppingCart, Zap, FileText, Boxes } from 'lucide-vue-next';
import { useI18n } from '../composables/useI18n'
import TrendChart from './TrendChart.vue'
import BaseSelect from './ui/BaseSelect.vue'

const { t, currentLang } = useI18n()

const isZh = computed(() => currentLang.value === 'zh')
const isEs = computed(() => currentLang.value === 'es')

const timeRange = ref(7)

const chartData = computed(() => {
  const days = timeRange.value
  const dates = []
  const amounts = []
  
  for (let i = days - 1; i >= 0; i--) {
    const d = new Date()
    d.setDate(d.getDate() - i)
    dates.push(`${d.getMonth() + 1}-${d.getDate()}`)
    if (i === 1) amounts.push(15)
    else if (i === 0) amounts.push(38)
    else amounts.push(0)
  }
  return { dates, amounts }
})

const formatNumber = (val) => {
  const num = Number(val) || 0
  return num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const tExt = computed(() => {
  const isZh = currentLang.value === 'zh'
  const isEs = currentLang.value === 'es'
  return {
    itemsUnit: isZh ? '项' : isEs ? 'ítems' : 'items',
    chartTitle: isZh ? '销售趋势' : isEs ? 'Tendencia de Ventas' : 'Sales Trend',
    timeRange7: isZh ? '近 7 天' : isEs ? 'Últimos 7 días' : 'Last 7 days',
    timeRange30: isZh ? '近 30 天' : isEs ? 'Últimos 30 días' : 'Last 30 days',
    
    quickNavTitle: isZh ? '常用功能快捷直达' : isEs ? 'Navegación Rápida' : 'Quick Navigation',
    btnPos: isZh ? '快速收银' : isEs ? 'Caja' : 'Quick Cashier',
    btnQuote: isZh ? '开单报价' : isEs ? 'Cotizar' : 'Quotation',
    btnFinancial: isZh ? '财务利润' : isEs ? 'Finanzas' : 'Financials',
    btnParts: isZh ? '配件库存' : isEs ? 'Inventario' : 'Inventory',
    btnClients: isZh ? '客户与挂账' : isEs ? 'Clientes' : 'Clients'
  }
})

defineProps({
  stats: {
    type: Object,
    default: () => ({
      total_inventory_usd: 0,
      total_inventory_bs: 0,
      total_sales_usd: 0,
      total_sales_bs: 0,
      total_skus: 0,
      low_stock_count: 0
    })
  },
  bcvRate: {
    type: Number,
    default: 36.50
  }
})

defineEmits(['navigate'])
</script>