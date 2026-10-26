<template>
  <div class="bg-white dark:bg-slate-800/80 backdrop-blur-xl rounded-3xl p-4 border border-slate-200/50 dark:border-slate-700/50 shadow-sm">
    <div class="flex justify-between items-center mb-4">
      <h3 class="text-sm font-bold text-slate-800 dark:text-white flex items-center gap-2">
        <span class="w-1.5 h-3.5 bg-blue-500 rounded-full inline-block"></span>
        {{ isZh ? '近 7 天销售趋势' : isEs ? 'Tendencia de ventas 7 días' : '7-day Sales Trend' }}
      </h3>
      <span class="text-[10px] bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 px-2 py-0.5 rounded-md font-bold">USD</span>
    </div>
    
    <div v-if="isLoading" class="h-32 flex items-center justify-center text-xs text-slate-400">
      {{ isZh ? '加载中...' : isEs ? 'Cargando...' : 'Loading...' }}
    </div>
    
    <div v-else class="flex items-end justify-between h-32 gap-2 relative mt-2">
      <!-- 背景辅助线 -->
      <div class="absolute inset-0 flex flex-col justify-between pointer-events-none">
        <div class="border-t border-slate-100 dark:border-slate-700/50 w-full"></div>
        <div class="border-t border-slate-100 dark:border-slate-700/50 w-full"></div>
        <div class="border-t border-slate-100 dark:border-slate-700/50 w-full"></div>
      </div>
      
      <!-- 柱状图 -->
      <div v-for="d in data" :key="d.date" class="flex-1 flex flex-col items-center justify-end h-full relative group">
        <div class="opacity-0 group-hover:opacity-100 absolute -top-6 bg-slate-800 text-white text-[10px] py-1 px-2 rounded pointer-events-none transition-opacity whitespace-nowrap z-10">
          $ {{ d.amount.toFixed(2) }}
        </div>
        <div 
          class="w-full max-w-[24px] bg-gradient-to-t from-blue-500 to-indigo-400 rounded-t-sm transition-all duration-500 ease-out" 
          :style="{ height: `${getBarHeight(d.amount)}%` }"
        ></div>
        <div class="text-[9px] text-slate-400 mt-2 font-mono">{{ d.display_date }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { apiFetch } from '../utils/api'
import { useI18n } from '../composables/useI18n'

const { currentLang } = useI18n()
const isZh = computed(() => currentLang.value === 'zh')
const isEs = computed(() => currentLang.value === 'es')

const data = ref([])
const isLoading = ref(true)

onMounted(async () => {
  try {
    const res = await apiFetch('/api/reports/trend-7days')
    if (res.ok) data.value = await res.json()
  } catch (e) {
    console.error('获取趋势失败', e)
  } finally {
    isLoading.value = false
  }
})

const getBarHeight = (amount) => {
  if (!data.value || data.value.length === 0) return 0
  const max = Math.max(...data.value.map(d => d.amount), 1) 
  const h = (amount / max) * 100
  return Math.max(h, 5) // 最小高度 5%
}
</script>
