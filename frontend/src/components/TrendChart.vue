<template>
  <div class="bg-white dark:bg-slate-800/80 backdrop-blur-xl rounded-3xl p-4 border border-slate-100 dark:border-slate-700 shadow-sm h-full flex flex-col justify-between">
    <div class="flex justify-between items-center mb-1">
      <h3 class="font-bold text-slate-800 dark:text-slate-200 flex items-center gap-2 text-sm">
        <span class="w-1.5 h-3.5 bg-blue-500 rounded-full"></span>{{ isZh ? '近 7 天销售趋势' : isEs ? 'Tendencia de ventas 7 días' : '7-day Sales Trend' }}</h3>
      <span class="text-[10px] font-bold text-blue-500 bg-blue-50 dark:bg-blue-900/30 px-2 py-0.5 rounded-md">USD</span>
    </div>

    <div v-if="isLoading" class="flex-1 flex items-center justify-center">
      <div class="w-5 h-5 border-2 border-blue-500/30 border-t-blue-500 rounded-full animate-spin"></div>
    </div>

    <div v-else class="relative flex-1 flex items-end justify-between gap-1 mt-2">
      <!-- 背景辅助线 -->
      <div class="absolute inset-0 flex flex-col justify-between pointer-events-none -z-10">
        <div class="w-full border-t border-dashed border-slate-100 dark:border-slate-700/50"></div>
        <div class="w-full border-t border-dashed border-slate-100 dark:border-slate-700/50"></div>
        <div class="w-full border-t border-dashed border-slate-100 dark:border-slate-700/50"></div>
      </div>

      <!-- 柱状图 -->
      <div v-for="item in data" :key="item.date" class="relative flex-1 flex flex-col items-center group h-full justify-end">
        <div 
          v-if="item.amount > 0"
          class="w-full max-w-[20px] bg-gradient-to-t from-blue-600 to-blue-400 rounded-t-sm transition-all duration-700 ease-out relative shadow-[0_0_12px_rgba(59,130,246,0.2)]"
          :style="{ height: `${getBarHeight(item.amount)}%` }"
        >
        </div>
        <div v-else class="w-1.5 h-1.5 bg-slate-200 dark:bg-slate-700 rounded-full mb-1"></div>
        <div class="mt-1 text-[9px] text-slate-400 dark:text-slate-500 font-mono">{{ item.display_date }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiFetch } from '../utils/api'

const data = ref([])
const isLoading = ref(true)

onMounted(async () => {
  try {
    const res = await apiFetch('/api/reports/trend-7days')
    if (res.ok) data.value = await res.json()
  } finally {
    isLoading.value = false
  }
})

const getBarHeight = (amount) => {
  if (!data.value || data.value.length === 0) return 0
  const max = Math.max(...data.value.map(d => d.amount), 1) 
  const h = (amount / max) * 100
  return Math.max(h, 5)
}
</script>
