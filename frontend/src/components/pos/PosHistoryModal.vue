<!-- src/components/pos/PosHistoryModal.vue -->
<template>
  <div v-if="visible" @click.self="$emit('close')" class="fixed inset-0 bg-slate-900/40 backdrop-blur-md flex items-center justify-center z-50 p-6 cursor-pointer">
    <div class="bg-white/95 backdrop-blur-2xl rounded-3xl shadow-2xl max-w-5xl w-full h-[88vh] max-h-[900px] overflow-hidden border border-white/80 flex flex-col cursor-default">
      
      <!-- 头部 -->
      <div class="p-5 border-b border-slate-200/60 flex items-center justify-between bg-white/50 shrink-0">
        <h3 class="font-extrabold text-base text-slate-900 flex items-center gap-2">
          <span>{{ tExt.title }}</span>
        </h3>
        <button @click="$emit('close')" class="text-slate-400 hover:text-slate-700 text-base font-bold p-1 cursor-pointer">✕</button>
      </div>

      <!-- 工具栏 (搜索与日期) -->
      <div class="p-4 border-b border-slate-200/60 bg-white/40 shrink-0 flex flex-wrap gap-4 items-center">
        <div class="relative flex-1 min-w-[200px]">
          <Search class="absolute left-3.5 top-3 text-slate-400" :size="16" />
          <input v-model="searchQuery" type="text" :placeholder="isZh ? '搜索单号/客户名称...' : isEs ? 'Buscar Nro. / Cliente...' : 'Search Order / Client...'" class="w-full bg-white border border-slate-200 rounded-xl pl-10 pr-4 py-2.5 text-xs outline-none focus:border-accent font-bold text-slate-900 transition-colors" />
        </div>
        
        <div class="flex items-center gap-2 flex-wrap">
          <div class="flex items-center gap-1 bg-white border border-slate-200 rounded-xl px-2 py-1 focus-within:border-accent transition-colors">
            <input type="date" :lang="currentLang" v-model="startDate" class="bg-transparent border-none text-xs outline-none font-mono font-bold text-slate-700 cursor-pointer" />
            <span class="text-slate-400 text-xs font-bold px-1">~</span>
            <input type="date" :lang="currentLang" v-model="endDate" class="bg-transparent border-none text-xs outline-none font-mono font-bold text-slate-700 cursor-pointer" />
          </div>
          <button @click="setDateToday" class="px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-bold transition-colors cursor-pointer">{{ isZh ? '今日' : isEs ? 'Hoy' : 'Today' }}</button>
          <button @click="setDateAll" class="px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-bold transition-colors cursor-pointer">{{ isZh ? '全部历史' : isEs ? 'Todo el Historial' : 'All History' }}</button>
        </div>
      </div>

      <!-- 状态 Tabs -->
      <div class="px-5 py-3 border-b border-slate-200/60 bg-white/30 flex items-center gap-2 shrink-0">
        <button 
          @click="statusFilter = 'ALL'" 
          :class="['px-4 py-1.5 rounded-lg text-xs font-bold transition-all', statusFilter === 'ALL' ? 'bg-slate-800 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100']"
        >{{ isZh ? '全部' : isEs ? 'Todo' : 'All' }}</button>
        <button 
          @click="statusFilter = 'COMPLETED'" 
          :class="['px-4 py-1.5 rounded-lg text-xs font-bold transition-all', statusFilter === 'COMPLETED' ? 'bg-emerald-600 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100']"
        >{{ isZh ? '正常销售' : isEs ? 'Ventas Normales' : 'Normal Sales' }}</button>
        <button 
          @click="statusFilter = 'REFUNDED'" 
          :class="['px-4 py-1.5 rounded-lg text-xs font-bold transition-all', statusFilter === 'REFUNDED' ? 'bg-rose-600 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100']"
        >{{ isZh ? '已退货' : isEs ? 'Devuelto' : 'Refunded' }}</button>
      </div>

      <!-- 列表区 -->
      <div class="flex-1 overflow-y-auto p-5 bg-white/20 space-y-3 custom-scrollbar">
        <div 
          v-for="order in filteredOrders" 
          :key="order.dbId" 
          :class="[
            'p-4 rounded-2xl border transition-all flex flex-wrap items-center justify-between gap-4 shadow-2xs',
            order.status === 'REFUNDED' ? 'bg-slate-50/50 border-slate-200 opacity-60' : 'bg-white/90 border-slate-200/80 hover:bg-white'
          ]"
        >
          <div class="space-y-1">
            <div class="font-black text-sm text-slate-900 flex items-center gap-2 flex-wrap">
              <span :class="['font-mono', order.status === 'REFUNDED' ? 'text-slate-400 line-through' : 'text-accent']">{{ order.orderId }}</span>
              <span v-if="order.status === 'REFUNDED'" class="px-2 py-0.5 bg-rose-100 text-rose-700 text-[10px] font-black rounded border border-rose-200">{{ isZh ? '【已退货】' : isEs ? '【Devuelto】' : '【Refunded】' }}</span>
              <span>👤 {{ order.clientName }}</span>
            </div>
            <div class="text-xs text-slate-500 font-mono flex items-center gap-3">
              <span>{{ order.time }}</span>
              <span class="text-slate-400">|</span>
              <span>{{ isZh ? '操作员' : isEs ? 'Operador' : 'Operator' }}: <span class="font-bold text-slate-700">{{ order.operator || 'Admin' }}</span></span>
            </div>
          </div>
          
          <div class="flex items-center gap-6">
            <div class="text-right">
              <div :class="['text-sm font-black font-mono', order.status === 'REFUNDED' ? 'text-slate-400 line-through' : 'text-emerald-600']">$ {{ Number(order.totalUsd || 0).toFixed(2) }}</div>
              <div class="text-[10px] text-slate-500 font-bold uppercase">{{ getPaymentMethodLabel(order.paymentMethod) }}</div>
            </div>
            <div class="flex items-center gap-2">
              <button @click="$emit('preview', order)" class="px-3 py-1.5 border border-slate-300 text-slate-700 rounded-md text-xs font-bold hover:bg-slate-50 transition-colors cursor-pointer">{{ isZh ? '显示小票' : isEs ? 'Mostrar recibo' : 'Show Receipt' }}</button>
              <button @click="$emit('reprint', order)" class="px-3 py-1.5 border border-slate-300 text-slate-700 rounded-md text-xs font-bold hover:bg-slate-50 transition-colors cursor-pointer">{{ isZh ? '补打小票' : isEs ? 'Reimprimir' : 'Reprint' }}</button>
              <button v-if="order.status !== 'REFUNDED'" @click="openReturnModal(order.dbId)" class="px-3 py-1.5 border border-rose-600 text-rose-600 rounded-md text-xs font-bold hover:bg-rose-50 transition-colors cursor-pointer">{{ isZh ? '申请退货' : isEs ? 'Devolver' : 'Return' }}</button>
              <span v-else class="px-3 py-1.5 text-xs font-bold text-slate-400 bg-slate-100 border border-slate-200 rounded-md">{{ isZh ? '已退货' : isEs ? 'Devuelto' : 'Refunded' }}</span>
            </div>
          </div>
        </div>

        <div v-if="filteredOrders.length === 0" class="flex flex-col items-center justify-center py-20 text-slate-400">
          <span class="text-sm font-bold">{{ startDate ? `${startDate} ~ ${endDate} ${isZh ? '暂无历史销售记录' : isEs ? 'Sin registros de ventas' : 'No sales records'}` : (isZh ? '暂无历史销售记录' : isEs ? 'Sin registros de ventas' : 'No sales records') }}</span>
        </div>
      </div>

      <!-- 底部 -->
      <div class="p-5 border-t border-slate-200/60 bg-white/80 flex items-center justify-between shrink-0">
        <span class="text-xs text-slate-500 font-bold">{{ isZh ? '共找到' : isEs ? 'Encontrados' : 'Found' }} <strong class="text-slate-900">{{ filteredOrders.length }}</strong> {{ isZh ? '笔订单' : isEs ? 'pedidos' : 'orders' }}</span>
        <button @click="$emit('close')" class="px-6 py-2 bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-xl text-xs font-bold transition-colors cursor-pointer">{{ isZh ? '关闭' : isEs ? 'Cerrar' : 'Close' }}</button>
      </div>

    </div>
  </div>
</template>

<script setup>
const isZh = computed(() => currentLang.value === 'zh')
const isEs = computed(() => currentLang.value === 'es')

import { ref, computed } from 'vue'
import { History, Search } from 'lucide-vue-next';
import { useI18n } from '../../composables/useI18n'
import ConfirmDialog from '../ConfirmDialog.vue'

const props = defineProps({
  visible: Boolean,
  orders: Array
})
const emit = defineEmits(['close', 'reprint', 'return', 'preview'])

const { t, currentLang } = useI18n()

const tExt = computed(() => {
  const isZh = currentLang.value === 'zh'
  const isEs = currentLang.value === 'es'
  return {
    title: isZh ? '最近销售历史与退换货管理' : isEs ? 'Historial Reciente y Devoluciones' : 'Recent Sales & Returns',
    searchPlaceholder: isZh ? '输入订单编号 / 客户名称搜索...' : isEs ? 'Buscar por Nro. de Orden / Cliente...' : 'Search by Order No. / Client...',
    todayBtn: isZh ? '今日' : isEs ? 'Hoy' : 'Today',
    allBtn: isZh ? '全部历史' : isEs ? 'Todo el Historial' : 'All History',
    btnReprint: isZh ? '补打小票' : isEs ? 'Reimprimir' : 'Reprint',
    btnReturn: isZh ? '申请退货' : isEs ? 'Devolver' : 'Return',
    emptyDateMsg: isZh ? '暂无历史销售记录' : isEs ? 'Sin registros de ventas' : 'No sales records found',
    emptyAllMsg: isZh ? '暂无所有历史记录' : isEs ? 'No hay historial' : 'No history found',
    found: isZh ? '共找到' : isEs ? 'Encontrados' : 'Found',
    orders: isZh ? '笔订单' : isEs ? 'pedidos' : 'orders',
    btnClose: isZh ? '关闭' : isEs ? 'Cerrar' : 'Close',
    confirmReturnMsg: isZh ? '确认执行退货处理？该操作会自动将商品库存回滚至仓库。' : isEs ? '¿Confirmar devolución? El inventario se restaurará automáticamente.' : 'Confirm return? Inventory will be restored automatically.'
  }
})

// 支付方式翻译
const getPaymentMethodLabel = (method) => {
  if (!method) return '-'
  const isZh = currentLang.value === 'zh'
  const isEs = currentLang.value === 'es'
  const m = String(method).toUpperCase()
  if (m.includes('CASH_USD')) return isZh ? '现金 USD' : isEs ? 'Efectivo USD' : 'Cash USD'
  if (m.includes('CASH_BS')) return isZh ? '现金 Bs.' : isEs ? 'Efectivo Bs.' : 'Cash Bs.'
  if (m.includes('PAGO_MOVIL')) return isZh ? 'Pago Móvil' : isEs ? 'Pago Móvil' : 'Pago Móvil'
  if (m.includes('CARD_POS')) return isZh ? '刷卡 POS' : isEs ? 'Punto de Venta' : 'Card POS'
  if (m.includes('MIXTO') || m.includes('MIX')) return isZh ? '混合支付' : isEs ? 'Pago Mixto' : 'Mixed Pay'
  if (m.includes('ZELLE')) return 'Zelle'
  if (m.includes('TRANSFER')) return isZh ? '银行转账' : isEs ? 'Transferencia' : 'Transfer'
  return method
}

const todayStr = new Date().toLocaleDateString('en-CA')
const searchQuery = ref('')

// 退货确认状态
const returnModalVisible = ref(false)
const targetReturnId = ref(null)

const startDate = ref(new Date().toLocaleDateString('en-CA'))
const endDate = ref(new Date().toLocaleDateString('en-CA'))
const statusFilter = ref('ALL')

const setDateToday = () => {
  const today = new Date().toLocaleDateString('en-CA')
  startDate.value = today
  endDate.value = today
}
const setDateAll = () => {
  startDate.value = ''
  endDate.value = ''
}

const filteredOrders = computed(() => {
  let result = props.orders || []
  
  if (searchQuery.value) {
    const q = searchQuery.value.toUpperCase()
    result = result.filter(o => (o.orderId && o.orderId.toUpperCase().includes(q)) || (o.clientName && o.clientName.toUpperCase().includes(q)))
  }
  
  if (startDate.value) {
    result = result.filter(o => o.time && o.time.slice(0, 10) >= startDate.value)
  }
  if (endDate.value) {
    result = result.filter(o => o.time && o.time.slice(0, 10) <= endDate.value)
  }
  
  if (statusFilter.value === 'COMPLETED') {
    result = result.filter(o => o.status !== 'REFUNDED')
  } else if (statusFilter.value === 'REFUNDED') {
    result = result.filter(o => o.status === 'REFUNDED')
  }

  return result
})

const openReturnModal = (dbId) => {
  targetReturnId.value = dbId
  returnModalVisible.value = true
}

const executeReturn = () => {
  if (targetReturnId.value) {
    emit('return', targetReturnId.value)
  }
  returnModalVisible.value = false
  targetReturnId.value = null
}
import AppButton from '../ui/AppButton.vue'
</script>