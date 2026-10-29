cat > frontend/src/mobile/MobileDashboardView.vue << 'EOF'
<template>
  <div class="min-h-full bg-slate-50 dark:bg-slate-950 pb-6">
    
    
    <header class="px-5 pt-6 pb-4 flex items-center justify-between">
      <div>
        <p class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">{{ todayDate }}</p>
        <h1 class="text-lg font-bold text-slate-800 dark:text-slate-100 mt-0.5">{{ isZh ? 'TOSTIYK 驾驶舱' : isEs ? 'Cabina TOSTIYK' : 'TOSTIYK Cockpit' }}</h1>
      </div>
      <div class="w-10 h-10 rounded-full bg-gradient-to-tr from-blue-500 to-indigo-600 flex items-center justify-center text-white font-bold text-sm shadow-sm">
        {{ userInitial }}
      </div>
    </header>

    <!-- 🌟 玩法升级：骨架屏 (Skeleton) -->
    <div v-if="isLoading" class="px-5 animate-pulse">
      <!-- 顶部主卡占位 -->
      <div class="h-40 bg-slate-200 dark:bg-slate-800 rounded-3xl mt-2"></div>
      
      <!-- 两列小卡占位 -->
      <div class="grid grid-cols-2 gap-3 mt-4">
        <div class="h-24 bg-slate-200 dark:bg-slate-800 rounded-2xl"></div>
        <div class="h-24 bg-slate-200 dark:bg-slate-800 rounded-2xl"></div>
      </div>
      
      <!-- 利润卡占位 -->
      <div class="h-20 bg-slate-200 dark:bg-slate-800 rounded-2xl mt-3"></div>
      
      <!-- 最近动态占位 -->
      <div class="mt-6 space-y-3">
        <div class="w-24 h-4 bg-slate-200 dark:bg-slate-800 rounded-md"></div>
        <div class="h-14 bg-slate-200 dark:bg-slate-800 rounded-xl mt-3"></div>
        <div class="h-14 bg-slate-200 dark:bg-slate-800 rounded-xl"></div>
        <div class="h-14 bg-slate-200 dark:bg-slate-800 rounded-xl"></div>
      </div>
    </div>

    <template v-else>
      <section class="px-5">
        <!-- 锁死高度的滑动组件 -->
        <div class="flex overflow-x-auto snap-x snap-mandatory gap-0 [&::-webkit-scrollbar]:hidden -mx-5">
          
          <!-- 卡片 1：库存总资产 -->
          <div class="w-[100vw] shrink-0 snap-center px-5 h-[170px]">
            <div class="h-full flex flex-col justify-between relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 dark:from-blue-950 dark:via-slate-900 dark:to-slate-900 p-6 shadow-xl">
              <div class="absolute -top-10 -right-10 w-40 h-40 rounded-full bg-accent/100/20 blur-3xl"></div>
              <div class="relative flex flex-col justify-between h-full">
                <div>
                  <p class="text-[11px] font-bold text-blue-300/80 uppercase tracking-widest">{{ isZh ? '库存总资产 (USD)' : isEs ? 'Valor del inventario (USD)' : 'Total Inventory (USD)' }}</p>
                  <h2 class="text-4xl font-black text-white mt-1 font-mono tabular-nums tracking-tight">
                    $ {{ formatMoney(stats.totalAssetUSD) }}
                  </h2>
                  <p class="text-[11px] text-slate-400 mt-1">
                    折合 Bs. {{ formatMoney(stats.totalAssetUSD * bcvRate) }}
                  </p>
                </div>
                <div class="pt-3 border-t border-white/10 flex items-center justify-between text-xs">
                  <span class="text-slate-400">{{ isZh ? '潜在销售额' : isEs ? 'Ventas potenciales' : 'Potential Sales' }}</span>
                  <span class="text-emerald-400 font-mono font-bold tabular-nums">$ {{ formatMoney(stats.totalRetailUSD) }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 卡片 2：近 7 天趋势 -->
          <div class="w-[100vw] shrink-0 snap-center px-5 h-[170px]">
            <TrendChart class="h-full w-full" />
          </div>

        </div>
      </section>

      <section class="px-5 mt-4 grid grid-cols-2 gap-3">
        <div class="bg-white dark:bg-slate-900 rounded-2xl p-4 border border-slate-100 dark:border-slate-800">
          <div class="flex items-center gap-1.5 mb-2">
            <span class="w-1.5 h-1.5 rounded-full bg-rose-500"></span>
            <p class="text-[10px] font-bold text-slate-500 uppercase tracking-wider">{{ isZh ? '应收欠款' : isEs ? 'Cuentas por cobrar' : 'Receivables' }}</p>
          </div>
          <p class="text-xl font-black text-rose-600 dark:text-rose-400 font-mono tabular-nums">$ {{ formatMoney(stats.totalDebt) }}</p>
        </div>
        <div class="bg-white dark:bg-slate-900 rounded-2xl p-4 border border-slate-100 dark:border-slate-800">
          <div class="flex items-center gap-1.5 mb-2">
            <span class="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
            <p class="text-[10px] font-bold text-slate-500 uppercase tracking-wider">{{ isZh ? '库存预警' : isEs ? 'Alerta de stock' : 'Stock Alert' }}</p>
          </div>
          <p class="text-xl font-black text-amber-600 dark:text-amber-400 font-mono tabular-nums">{{ stats.lowStock }} <span class="text-xs font-medium text-slate-400">{{ isZh ? '项' : isEs ? 'ítems' : 'items' }}</span></p>
        </div>
      </section>

      <section class="px-5 mt-3">
        <div class="bg-white dark:bg-slate-900 rounded-2xl p-4 border border-slate-100 dark:border-slate-800 flex items-center justify-between">
          <div class="flex items-center gap-2.5">
            <div class="w-9 h-9 rounded-xl bg-emerald-50 dark:bg-emerald-900/30 flex items-center justify-center">
              </div>
            <div>
              <p class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">{{ isZh ? '预估销售利润' : isEs ? 'Beneficio estimado' : 'Estimated Profit' }}</p>
              <p class="text-base font-black text-slate-800 dark:text-slate-100 font-mono tabular-nums mt-0.5">$ {{ formatMoney(stats.totalRetailUSD - stats.totalAssetUSD) }}</p>
            </div>
          </div>
          <span class="text-[10px] font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-900/30 px-2 py-1 rounded-lg">{{ profitRate }}%</span>
        </div>
      </section>

      <section class="px-5 mt-6">
        <div class="flex items-center justify-between mb-3 ml-1">
          <h3 class="text-[11px] font-bold text-slate-400 uppercase tracking-wider">{{ isZh ? '最近动态' : isEs ? 'Actividad reciente' : 'Recent Activity' }}</h3>
          <button @click="$parent.activeTab = 'transactions'" class="text-[10px] font-bold text-blue-500">{{ isZh ? '查看全部' : isEs ? 'Ver todo' : 'View All' }}</button>
        </div>
        <div class="space-y-2">
          <div v-for="tx in recentTxs" :key="tx.id" class="bg-white dark:bg-slate-900 p-3 rounded-xl border border-slate-100 dark:border-slate-800 flex items-center justify-between">
            <div class="flex items-center gap-3 overflow-hidden">
              <div class="w-8 h-8 rounded-full flex items-center justify-center shrink-0" 
                :class="tx.type === 'IN' ? 'bg-emerald-50 text-emerald-600' : 'bg-amber-50 text-amber-600'">
                <ArrowDownLeft v-if="tx.type === 'IN'" :size="14" />
                <ArrowUpRight v-else :size="14" />
              </div>
              <div class="truncate">
                <p class="text-xs font-bold text-slate-700 dark:text-slate-300 truncate">{{ tx.part_name }}</p>
                <p class="text-[10px] text-slate-400 font-mono mt-0.5">{{ tx.timestamp.split(' ')[1] || tx.timestamp }}</p>
              </div>
            </div>
            <p class="text-xs font-black font-mono" :class="tx.type === 'IN' ? 'text-emerald-600' : 'text-slate-700 dark:text-slate-300'">
              {{ tx.type === 'IN' ? '+' : '-' }}{{ tx.quantity }}
            </p>
          </div>
          <div v-if="recentTxs.length === 0" class="text-center py-4 text-xs text-slate-400">{{ isZh ? '今日暂无动态' : isEs ? 'Sin actividad hoy' : 'No activity today' }}</div>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { useI18n } from '../composables/useI18n'

const { currentLang } = useI18n()

const isZh = computed(() => currentLang.value === 'zh')
const isEs = computed(() => currentLang.value === 'es')


import { ref, computed, onMounted } from 'vue'
import { TrendingUp, ArrowDownLeft, ArrowUpRight } from 'lucide-vue-next'
import { apiFetch } from '../utils/api'
import { useAuth } from '../composables/useAuth'
import TrendChart from '../components/TrendChart.vue'

const { currentUserObj } = useAuth()
const todayDate = new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' })
const userInitial = computed(() => (currentUserObj.value?.username || 'A').charAt(0).toUpperCase())

const isLoading = ref(true)
const bcvRate = ref(1)
const stats = ref({ totalAssetUSD: 0, totalRetailUSD: 0, totalDebt: 0, lowStock: 0 })
const recentTxs = ref([])

const formatMoney = (n) => Number(n || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
const profitRate = computed(() => {
  if (!stats.value.totalRetailUSD) return 0
  const profit = stats.value.totalRetailUSD - stats.value.totalAssetUSD
  return ((profit / stats.value.totalRetailUSD) * 100).toFixed(1)
})

onMounted(async () => {
  try {
    const [dashRes, debtRes, rateRes, txRes] = await Promise.all([
      apiFetch('/api/dashboard/stats'),
      apiFetch('/api/clients/analytics/debt-summary'),
      apiFetch('/api/settings/bcv-rate'),
      apiFetch('/api/transactions?page=1&page_size=5')
    ])
    if (dashRes.ok) {
      const d = await dashRes.json()
      stats.value.totalAssetUSD = d.totalAssetUSD || 0
      stats.value.totalRetailUSD = d.totalRetailUSD || 0
      stats.value.lowStock = d.low_stock_count || 0
    }
    if (debtRes.ok) stats.value.totalDebt = (await debtRes.json()).total_debt_usd || 0
    if (rateRes.ok) bcvRate.value = (await rateRes.json()).rate || 1
    if (txRes.ok) recentTxs.value = (await txRes.json()).items || []
  } finally {
    isLoading.value = false
  }
})
</script>