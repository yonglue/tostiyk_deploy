<template>
  <div class="min-h-full bg-slate-50 dark:bg-slate-950 pb-24 relative overflow-hidden">
    
    <!-- 顶部固定区 -->
    <div class="sticky top-0 z-10 bg-slate-50/90 dark:bg-slate-950/90 backdrop-blur-xl px-5 pt-6 pb-3 border-b border-slate-100 dark:border-slate-800/60">
      <h1 class="text-lg font-bold text-slate-800 dark:text-slate-100 mb-3">进销存流水</h1>
      
      <!-- 筛选 Tab -->
      <div class="flex bg-slate-200/60 dark:bg-slate-800/80 p-1 rounded-xl">
        <button 
          v-for="tab in tabs" :key="tab.value"
          @click="switchTab(tab.value)"
          :class="currentTab === tab.value ? 'bg-white dark:bg-slate-700 text-blue-600 dark:text-blue-400 shadow-sm' : 'text-slate-500 dark:text-slate-400'"
          class="flex-1 py-1.5 rounded-lg text-xs font-bold transition-all"
        >
          {{ tab.label }}
        </button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="isLoading" class="px-5 py-20 text-center">
      <div class="inline-block w-8 h-8 rounded-full border-2 border-blue-500/30 border-t-blue-500 animate-spin"></div>
    </div>

    <!-- 流水列表 -->
    <div v-else class="px-5 mt-4 space-y-3">
      <div 
        v-for="tx in transactions" 
        :key="tx.id" 
        @click="openDetail(tx)"
        class="bg-white dark:bg-slate-900 rounded-2xl p-4 border border-slate-100 dark:border-slate-800 shadow-sm active:scale-[0.98] transition-transform cursor-pointer"
      >
        <div class="flex justify-between items-center">
          <div class="flex-1 min-w-0 pr-3">
            <div class="flex items-center gap-2 mb-1">
              <span class="text-[10px] font-bold px-2 py-0.5 rounded" 
                :class="tx.type === 'IN' ? 'bg-emerald-50 text-emerald-600' : tx.type === 'REFUND' ? 'bg-rose-50 text-rose-600' : 'bg-amber-50 text-amber-600'">
                {{ tx.type }}
              </span>
              <span class="text-[10px] text-slate-400 font-mono">{{ tx.timestamp }}</span>
            </div>
            <h3 class="font-bold text-sm text-slate-800 dark:text-slate-100 truncate">{{ tx.part_name }}</h3>
            <p class="text-xs text-slate-400 font-mono mt-0.5">{{ tx.part_oem }}</p>
          </div>
          <div class="text-right shrink-0">
            <p class="text-sm font-black font-mono tabular-nums" :class="tx.type === 'IN' ? 'text-emerald-600' : 'text-slate-700 dark:text-slate-300'">
              {{ tx.type === 'IN' ? '+' : '-' }}{{ tx.quantity }}
            </p>
            <p class="text-[10px] text-slate-400 font-mono mt-1">${{ Number(tx.total_amount || 0).toFixed(2) }}</p>
          </div>
        </div>
      </div>
      
      <div v-if="transactions.length === 0" class="text-center py-20">
        <p class="text-sm text-slate-400">暂无流水记录</p>
      </div>
    </div>

    <!-- 🌟 详情面板：绑定 panelRef 和 style -->
    <div v-if="selectedTx" ref="panelRef" :style="swipeStyle" class="fixed inset-0 z-50 bg-slate-50 dark:bg-slate-950 flex flex-col">
      <header class="px-5 py-4 flex items-center justify-between border-b border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900 shrink-0">
        <button @click="selectedTx = null" class="p-2 -ml-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800">
          <ArrowLeft :size="20" class="text-slate-600 dark:text-slate-400" />
        </button>
        <h2 class="font-bold text-sm text-slate-800 dark:text-slate-100">单据详情</h2>
        <div class="w-8"></div>
      </header>

      <div class="flex-1 overflow-y-auto p-5 space-y-6">
        <!-- 类型与时间 -->
        <div class="flex justify-between items-center border-b border-slate-100 dark:border-slate-800 pb-4">
          <div>
            <p class="text-[11px] font-bold text-slate-400 uppercase">时间</p>
            <p class="text-sm font-mono font-bold text-slate-800 dark:text-slate-100 mt-1">{{ selectedTx.timestamp }}</p>
          </div>
          <span class="px-3 py-1.5 rounded-lg text-sm font-bold border" 
            :class="selectedTx.type === 'IN' ? 'bg-emerald-50 text-emerald-600' : selectedTx.type === 'REFUND' ? 'bg-rose-50 text-rose-600' : 'bg-amber-50 text-amber-600'">
            {{ selectedTx.type }}
          </span>
        </div>

        <!-- 商品信息 -->
        <div class="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-100 dark:border-slate-800 space-y-3">
          <div class="flex justify-between items-center">
            <span class="text-xs font-semibold text-slate-500">OEM</span>
            <span class="font-mono font-bold text-blue-600 dark:text-blue-400">{{ selectedTx.part_oem }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-xs font-semibold text-slate-500">名称</span>
            <span class="font-bold text-slate-800 dark:text-slate-100">{{ selectedTx.part_name }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-xs font-semibold text-slate-500">客户/供应商</span>
            <span class="font-bold text-slate-700 dark:text-slate-300">{{ selectedTx.customer_or_supplier || '-' }}</span>
          </div>
        </div>

        <!-- 金额明细 -->
        <div class="bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-100 dark:border-slate-800 space-y-4">
          <div class="flex justify-between items-center text-sm">
            <span class="text-slate-500">数量 × 单价</span>
            <span class="font-mono text-slate-700 dark:text-slate-300">{{ selectedTx.quantity }} × ${{ Number(selectedTx.unit_price || 0).toFixed(2) }}</span>
          </div>
          <div class="h-px w-full bg-slate-100 dark:bg-slate-800"></div>
          <div class="flex justify-between items-center">
            <span class="text-sm font-bold text-slate-800 dark:text-slate-100">总金额</span>
            <span class="text-xl font-black font-mono" :class="selectedTx.type === 'IN' ? 'text-emerald-600' : 'text-slate-800 dark:text-slate-200'">
              ${{ Number(selectedTx.total_amount || 0).toFixed(2) }}
            </span>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ArrowLeft } from 'lucide-vue-next'
import { apiFetch } from '../utils/api'
import { useSwipeBack } from '../composables/useSwipeBack'

const tabs = [
  { label: '全部', value: 'ALL' },
  { label: '出库', value: 'OUT' },
  { label: '入库', value: 'IN' }
]

const currentTab = ref('ALL')
const transactions = ref([])
const isLoading = ref(true)
const selectedTx = ref(null)

// 挂载手势逻辑
const { panelRef, style: swipeStyle } = useSwipeBack(() => {
  selectedTx.value = null
})

const openDetail = (tx) => {
  selectedTx.value = tx
}

const fetchTransactions = async (type) => {
  isLoading.value = true
  try {
    const url = type === 'ALL' ? '/api/transactions?page=1&page_size=50' : `/api/transactions?page=1&page_size=50&tx_type=${type}`
    const res = await apiFetch(url)
    if (res.ok) {
      const data = await res.json()
      transactions.value = data.items || []
    }
  } finally {
    isLoading.value = false
  }
}

const switchTab = (type) => {
  currentTab.value = type
  fetchTransactions(type)
}

onMounted(() => {
  fetchTransactions(currentTab.value)
})
</script>
