<template>
  <div class="min-h-full bg-slate-50 dark:bg-slate-950 pb-24 relative overflow-hidden">
    
    <!-- 顶部固定区 -->
    <div class="sticky top-0 z-10 bg-slate-50/90 dark:bg-slate-950/90 backdrop-blur-xl px-5 pt-6 pb-3 border-b border-slate-100 dark:border-slate-800/60">
      <div class="bg-gradient-to-r from-rose-500 to-rose-600 rounded-2xl p-4 shadow-lg shadow-rose-500/20 mb-4 flex items-center justify-between">
        <div>
          <p class="text-[11px] font-bold text-rose-100 uppercase tracking-wider">客户总应收欠款</p>
          <h2 class="text-2xl font-black text-white font-mono tabular-nums mt-1">$ {{ formatMoney(totalDebt) }}</h2>
        </div>
        <div class="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center"><HandCoins :size="20" class="text-white" /></div>
      </div>
      <div class="relative">
        <Search :size="18" class="absolute left-3.5 top-3 text-slate-400" />
        <input v-model="searchQuery" type="text" placeholder="搜索客户名称、店铺..." class="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-sm outline-none focus:border-blue-500 dark:text-white transition-colors" />
      </div>
    </div>

    <div v-if="isLoading" class="px-5 py-20 text-center">
      <div class="inline-block w-8 h-8 rounded-full border-2 border-blue-500/30 border-t-blue-500 animate-spin"></div>
    </div>

    <div v-else class="px-5 mt-4 space-y-3">
      <div 
        v-for="client in filteredClients" 
        :key="client.id" 
        @click="openDetail(client)"
        class="bg-white dark:bg-slate-900 rounded-2xl p-4 border border-slate-100 dark:border-slate-800 shadow-sm active:scale-[0.98] transition-transform cursor-pointer"
      >
        <div class="flex justify-between items-center">
          <div class="flex-1 min-w-0 pr-3">
            <h3 class="font-bold text-sm text-slate-800 dark:text-slate-100 truncate">{{ client.name }}</h3>
            <p class="text-xs text-slate-400 mt-0.5 truncate">{{ client.store_name || '未设置店铺名' }}</p>
            <div class="mt-2 flex items-center gap-2">
              <span class="text-sm font-black font-mono tabular-nums" :class="client.debt > 0 ? 'text-rose-600 dark:text-rose-400' : 'text-slate-400'">$ {{ formatMoney(client.debt) }}</span>
            </div>
          </div>
          <ChevronRight :size="20" class="text-slate-300" />
        </div>
      </div>
    </div>

    <!-- 详情面板 -->
    <div v-if="selectedClient" ref="panelRef" :style="swipeStyle" class="fixed inset-0 z-50 bg-slate-50 dark:bg-slate-950 flex flex-col">
      <header class="px-5 py-4 flex items-center justify-between border-b border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900 shrink-0">
        <button @click="selectedClient = null" class="p-2 -ml-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800">
          <ArrowLeft :size="20" class="text-slate-600 dark:text-slate-400" />
        </button>
        <h2 class="font-bold text-sm text-slate-800 dark:text-slate-100">客户详情</h2>
        <div class="w-8"></div>
      </header>

      <div class="flex-1 overflow-y-auto p-5 space-y-6">
        
        <div class="flex flex-col items-center justify-center pt-4">
          <div class="w-20 h-20 rounded-full bg-gradient-to-tr from-blue-500 to-indigo-600 flex items-center justify-center text-white font-black text-3xl shadow-xl shadow-blue-500/30 mb-3">
            {{ selectedClient.name.charAt(0).toUpperCase() }}
          </div>
          <h1 class="text-xl font-bold text-slate-800 dark:text-slate-100">{{ selectedClient.name }}</h1>
          <p class="text-sm text-slate-500 mt-1">{{ selectedClient.store_name || '未设置店铺名' }}</p>
        </div>

        <div class="bg-gradient-to-br from-rose-500 to-rose-600 rounded-3xl p-5 shadow-lg shadow-rose-500/20">
          <p class="text-[11px] font-bold text-rose-100 uppercase tracking-widest">当前欠款</p>
          <h2 class="text-4xl font-black text-white font-mono mt-1">$ {{ formatMoney(selectedClient.debt) }}</h2>
          <div class="mt-4 pt-4 border-t border-white/20 flex justify-between text-xs text-rose-100">
            <span>信用额度上限</span>
            <span class="font-bold font-mono">$ {{ formatMoney(selectedClient.credit_limit) }}</span>
          </div>
        </div>

        <!-- 历史交易记录 -->
        <div class="space-y-3">
          <h3 class="text-[11px] font-bold text-slate-400 uppercase tracking-wider ml-1">历史交易记录</h3>
          <div v-if="clientHistory.length === 0" class="text-center py-6 text-xs text-slate-400 bg-white dark:bg-slate-900 rounded-xl border border-slate-100 dark:border-slate-800">暂无历史记录</div>
          <div v-for="record in clientHistory" :key="record.id" class="bg-white dark:bg-slate-900 rounded-xl p-3 border border-slate-100 dark:border-slate-800 flex justify-between items-center">
            <div>
              <p class="text-xs font-bold text-slate-700 dark:text-slate-300">{{ record.payment_method === 'Fiado' ? '挂账' : '还款/销售' }}</p>
              <p class="text-[10px] text-slate-400 font-mono mt-0.5">{{ record.timestamp }}</p>
            </div>
            <p class="text-sm font-black font-mono text-rose-500">+${{ formatMoney(record.total_amount || record.amount_usd) }}</p>
          </div>
        </div>

      </div>

      <!-- 底部快捷操作区 -->
      <div class="p-4 bg-white dark:bg-slate-900 border-t border-slate-100 dark:border-slate-800 flex gap-3 shrink-0">
        <!-- 🌟 极速收款按钮 -->
        <button 
          v-if="selectedClient.debt > 0"
          @click="showPayModal = true"
          class="flex-1 py-3.5 bg-gradient-to-r from-emerald-500 to-teal-500 text-white rounded-xl font-bold flex items-center justify-center gap-2 shadow-lg shadow-emerald-500/30 active:scale-[0.98] transition-transform"
        >
          <HandCoins :size="18" /> 极速收款
        </button>
        <a v-if="selectedClient.phone" :href="`tel:${selectedClient.phone}`" class="w-14 h-[50px] bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-xl font-bold flex items-center justify-center active:scale-[0.98] transition-transform">
          <Phone :size="20" />
        </a>
        <a v-if="selectedClient.phone" :href="`https://wa.me/${selectedClient.phone.replace(/[^0-9]/g, '')}`" target="_blank" class="w-14 h-[50px] bg-[#25D366]/10 text-[#25D366] rounded-xl font-bold flex items-center justify-center active:scale-[0.98] transition-transform">
          <MessageCircle :size="20" />
        </a>
      </div>
    </div>

    <!-- 收款弹窗挂载 -->
    <MobilePaymentModal
      :visible="showPayModal"
      :client-debt="selectedClient ? selectedClient.debt : 0"
      :is-submitting="isSubmittingPay"
      @close="showPayModal = false"
      @submit="handleRepay"
    />

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Search, Phone, MessageCircle, HandCoins, ArrowLeft, ChevronRight } from 'lucide-vue-next'
import { apiFetch } from '../utils/api'
import { useSwipeBack } from '../composables/useSwipeBack'
import { useNotifications } from '../composables/useNotifications'
import MobilePaymentModal from './MobilePaymentModal.vue'

const clients = ref([])
const searchQuery = ref('')
const isLoading = ref(true)
const selectedClient = ref(null)
const clientHistory = ref([])

const showPayModal = ref(false)
const isSubmittingPay = ref(false)

const { showSuccessModal } = useNotifications()

const formatMoney = (n) => Number(n || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

const totalDebt = computed(() => clients.value.reduce((sum, c) => sum + (Number(c.debt) || 0), 0))

const filteredClients = computed(() => {
  let result = clients.value.filter(c => Number(c.debt) > 0)
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    result = result.filter(c => c.name.toLowerCase().includes(q) || (c.store_name && c.store_name.toLowerCase().includes(q)))
  }
  return result.sort((a, b) => Number(b.debt) - Number(a.debt))
})

const { panelRef, style: swipeStyle } = useSwipeBack(() => {
  selectedClient.value = null
})

const openDetail = async (client) => {
  selectedClient.value = client
  clientHistory.value = []
  try {
    const res = await apiFetch('/api/transactions?page=1&page_size=10')
    if (res.ok) {
      const data = await res.json()
      clientHistory.value = (data.items || []).filter(tx => tx.customer_or_supplier === client.name || tx.customer_or_supplier === client.store_name)
    }
  } catch (e) {}
}

// 🌟 核心：处理极速收款
const handleRepay = async (amount) => {
  if (!selectedClient.value) return
  isSubmittingPay.value = true
  try {
    const res = await apiFetch('/api/clients/repay', {
      method: 'POST',
      body: JSON.stringify({
        client_name: selectedClient.value.name,
        amount_paid: amount,
        currency: 'USD',
        payment_method: 'Cash_USD'
      })
    })

    if (res.ok) {
      const data = await res.json()
      // 更新本地数据
      selectedClient.value.debt = data.remaining_debt
      const clientInList = clients.value.find(c => c.id === selectedClient.value.id)
      if (clientInList) clientInList.debt = data.remaining_debt
      
      showPayModal.value = false
      showSuccessModal(`✅ 收款成功！剩余欠款: $${data.remaining_debt.toFixed(2)}`)
    } else {
      const err = await res.json()
      showSuccessModal(`❌ 收款失败: ${err.detail || '未知错误'}`)
    }
  } catch (e) {
    showSuccessModal('❌ 网络请求失败')
  } finally {
    isSubmittingPay.value = false
  }
}

onMounted(async () => {
  try {
    const res = await apiFetch('/api/clients')
    if (res.ok) clients.value = await res.json()
  } finally {
    isLoading.value = false
  }
})
</script>
