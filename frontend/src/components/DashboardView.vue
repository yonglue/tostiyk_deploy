<!-- src/components/DashboardView.vue -->
<template>
  <div class="space-y-6 max-w-11xl mx-auto">
    
    <!-- 欢迎横幅与系统概览 (恢复蓝底，移除汇率) -->
    <div class="bg-gradient-to-r from-blue-700 to-indigo-800 dark:from-blue-900 dark:to-indigo-900 rounded-xl p-5 sm:p-6 text-white shadow-md border border-transparent dark:border-slate-700 flex flex-col justify-center">
      <div>
        <h1 class="text-xl sm:text-2xl md:text-3xl font-black tracking-tight">{{ t.dashboard.title }}</h1>
        <p class="text-blue-100 text-xs sm:text-sm mt-1">{{ t.dashboard.subtitle }}</p>
      </div>
    </div>

    <!-- 📊 核心指标卡片网格 -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
      
      <!-- 卡片 1：当前库存总资产 -->
      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 sm:p-5 border border-slate-200 dark:border-slate-700 shadow-sm hover:border-blue-400 dark:hover:border-blue-600 transition-colors duration-200 flex flex-col justify-between">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">{{ t.dashboard.assetTitle }}</span>
          <div class="w-10 h-10 rounded-lg bg-accent/100/10 text-accent dark:text-accent flex items-center justify-center">
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

      <!-- 卡片 2：累计销售总额 -->
      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 sm:p-5 border border-slate-200 dark:border-slate-700 shadow-sm hover:border-blue-400 dark:hover:border-blue-600 transition-colors duration-200 flex flex-col justify-between">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">{{ t.dashboard.salesTitle }}</span>
          <div class="w-10 h-10 rounded-lg bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 flex items-center justify-center">
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

      <!-- 卡片 3：配件总SKU数 -->
      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 sm:p-5 border border-slate-200 dark:border-slate-700 shadow-sm hover:border-blue-400 dark:hover:border-blue-600 transition-colors duration-200 flex flex-col justify-between">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">{{ t.dashboard.skuTitle }}</span>
          <div class="w-10 h-10 rounded-lg bg-amber-500/10 text-amber-600 dark:text-amber-400 flex items-center justify-center">
            <Layers :size="20" />
          </div>
        </div>
        <div class="mt-4">
          <div class="text-2xl sm:text-3xl font-black text-slate-900 dark:text-slate-100 font-mono">
            {{ stats.total_skus || 0 }} <span class="text-sm">{{ tExt.itemsUnit }}</span>
          </div>
          <div class="text-xs text-amber-600 dark:text-amber-500 font-medium mt-1">{{ t.dashboard.skuSub }}</div>
        </div>
      </div>

      <!-- 卡片 4：库存低水位预警 -->
      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 sm:p-5 border border-slate-200 dark:border-slate-700 shadow-sm hover:border-blue-400 dark:hover:border-blue-600 transition-colors duration-200 flex flex-col justify-between">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">{{ t.dashboard.warningTitle }}</span>
          <div class="w-10 h-10 rounded-lg bg-rose-500/10 text-rose-600 dark:text-rose-400 flex items-center justify-center">
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

    <!-- 7天趋势图 -->
    <TrendChart />

    <!-- 🚀 快捷业务直达面板 (Quick Actions) -->
    <div class="bg-white dark:bg-slate-800 rounded-xl p-5 border border-slate-200 dark:border-slate-700 shadow-sm space-y-4">
      <h3 class="font-bold text-slate-800 dark:text-slate-200 text-base flex items-center gap-2">
        <span>⚡</span> {{ tExt.quickNavTitle }}
      </h3>
      <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
        
        <!-- 🌟 快速收银 -->
        <button 
          @click="$emit('navigate', 'pos')" 
          :title="tExt.btnPos"
          class="bg-accent/10/60 dark:bg-blue-900/20 hover:bg-accent dark:hover:bg-accent hover:text-white text-accent dark:text-accent border border-blue-200/80 dark:border-blue-800 p-4 rounded-lg font-bold text-xs flex flex-col items-center gap-2 transition-all cursor-pointer shadow-sm hover:border-transparent hover:shadow-md group"
        >
          <span class="text-2xl group-hover:scale-110 transition-transform">🛒</span>
          <span>{{ tExt.btnPos }}</span>
        </button>

        <!-- 🌟 开单报价 -->
        <button 
          @click="$emit('navigate', 'quotation')" 
          :title="tExt.btnQuote"
          class="bg-amber-50/60 dark:bg-amber-900/20 hover:bg-amber-500 dark:hover:bg-amber-500 hover:text-white text-amber-800 dark:text-amber-400 border border-amber-200/80 dark:border-amber-800 p-4 rounded-lg font-bold text-xs flex flex-col items-center gap-2 transition-all cursor-pointer shadow-sm hover:border-transparent hover:shadow-md group"
        >
          <span class="text-2xl group-hover:scale-110 transition-transform">📝</span>
          <span>{{ tExt.btnQuote }}</span>
        </button>

        <!-- 财务利润 -->
        <button 
          @click="$emit('navigate', 'financial')" 
          :title="tExt.btnFinancial"
          class="bg-emerald-50/60 dark:bg-emerald-900/20 hover:bg-emerald-500 dark:hover:bg-emerald-500 hover:text-white text-emerald-800 dark:text-emerald-400 border border-emerald-200/80 dark:border-emerald-800 p-4 rounded-lg font-bold text-xs flex flex-col items-center gap-2 transition-all cursor-pointer shadow-sm hover:border-transparent hover:shadow-md group"
        >
          <span class="text-2xl group-hover:scale-110 transition-transform">📈</span>
          <span>{{ tExt.btnFinancial }}</span>
        </button>

        <!-- 配件库存 -->
        <button 
          @click="$emit('navigate', 'parts')" 
          :title="tExt.btnParts"
          class="bg-slate-50/60 dark:bg-slate-900/50 hover:bg-slate-600 dark:hover:bg-slate-600 hover:text-white text-slate-700 dark:text-slate-300 border border-slate-200/80 dark:border-slate-700 p-4 rounded-lg font-bold text-xs flex flex-col items-center gap-2 transition-all cursor-pointer shadow-sm hover:border-transparent hover:shadow-md group"
        >
          <span class="text-2xl group-hover:scale-110 transition-transform">📦</span>
          <span>{{ tExt.btnParts }}</span>
        </button>

        <!-- 客户与账本 -->
        <button 
          @click="$emit('navigate', 'clients')" 
          :title="tExt.btnClients"
          class="bg-purple-50/60 dark:bg-purple-900/20 hover:bg-purple-500 dark:hover:bg-purple-500 hover:text-white text-purple-800 dark:text-purple-400 border border-purple-200/80 dark:border-purple-800 p-4 rounded-lg font-bold text-xs flex flex-col items-center gap-2 transition-all cursor-pointer shadow-sm hover:border-transparent hover:shadow-md group"
        >
          <span class="text-2xl group-hover:scale-110 transition-transform">👥</span>
          <span>{{ tExt.btnClients }}</span>
        </button>
      </div>
    </div>

  </div>
</template>

<script setup>
const isZh = computed(() => currentLang.value === 'zh')
const isEs = computed(() => currentLang.value === 'es')

import { computed } from 'vue'
import { Package, TrendingUp, Layers, AlertTriangle } from 'lucide-vue-next'
import { useI18n } from '../composables/useI18n'
import TrendChart from './TrendChart.vue'

const { t, currentLang } = useI18n()

// 格式化货币数字
const formatNumber = (val) => {
  const num = Number(val) || 0
  return num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const tExt = computed(() => {
  const isZh = currentLang.value === 'zh'
  const isEs = currentLang.value === 'es'
  return {
    itemsUnit: isZh ? '项' : isEs ? 'ítems' : 'items',
    quickNavTitle: isZh ? '常用功能快捷直达' : isEs ? 'Navegación Comercial Rápida' : 'Quick Navigation',
    btnPos: isZh ? '快速收银' : isEs ? 'Caja Rápida' : 'Quick POS',
    btnQuote: isZh ? '开单报价' : isEs ? 'Cotización' : 'Billing & Quote',
    btnFinancial: isZh ? '查看财务利润' : isEs ? 'Ver Finanzas' : 'View Financials',
    btnParts: isZh ? '配件库存与条码' : isEs ? 'Inventario y Códigos' : 'Inventory & Barcodes',
    btnClients: isZh ? '客户与挂账管理' : isEs ? 'Clientes y Fiado' : 'Clients & Fiado'
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