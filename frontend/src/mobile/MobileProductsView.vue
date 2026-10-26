<template>
  <div class="min-h-full bg-slate-50 dark:bg-slate-950 pb-24 relative overflow-hidden">
    
    <div class="sticky top-0 z-10 bg-slate-50/90 dark:bg-slate-950/90 backdrop-blur-xl px-5 pt-6 pb-3 border-b border-slate-100 dark:border-slate-800/60">
      <h1 class="text-lg font-bold text-slate-800 dark:text-slate-100 mb-3">{{ isZh ? '库存产品' : isEs ? 'Productos en stock' : 'Products in Stock' }}</h1>
      <div class="relative">
        <Search :size="18" class="absolute left-3.5 top-3 text-slate-400" />
        <input v-model="searchQuery" type="text" placeholder="{{ isZh ? '搜索 OEM 或 配件名称...' : isEs ? 'Buscar OEM o nombre...' : 'Search OEM or name...' }}" class="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-sm outline-none focus:border-blue-500 dark:text-white transition-colors" />
      </div>
    </div>

    <div v-if="isLoading" class="px-5 py-20 text-center">
      <div class="inline-block w-8 h-8 rounded-full border-2 border-blue-500/30 border-t-blue-500 animate-spin"></div>
    </div>

    <div v-else class="px-5 mt-4 space-y-3">
      <div 
        v-for="part in filteredParts" 
        :key="part.id" 
        @click="openDetail(part)"
        class="bg-white dark:bg-slate-900 rounded-2xl p-4 border border-slate-100 dark:border-slate-800 shadow-sm active:scale-[0.98] transition-transform cursor-pointer"
      >
        <div class="flex justify-between items-start">
          <div class="flex-1 min-w-0 pr-3">
            <span class="text-[10px] font-bold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30 px-2 py-0.5 rounded">{{ part.brand || 'GENERAL' }}</span>
            <h3 class="font-bold text-sm text-slate-800 dark:text-slate-100 mt-2 truncate">{{ part.name }}</h3>
            <p class="text-xs font-mono text-slate-400 mt-0.5">{{ part.oem }}</p>
          </div>
          <div class="text-right shrink-0">
            <p class="text-[10px] font-bold text-slate-400 uppercase tracking-wider">{{ isZh ? '库存' : isEs ? 'Inventario' : 'Inventory' }}</p>
            <p class="text-xl font-black font-mono tabular-nums" :class="getStockClass(part.stock)">{{ part.stock }}</p>
          </div>
        </div>
        <div class="mt-3 pt-3 border-t border-slate-50 dark:border-slate-800/60 flex items-center justify-between text-xs">
          <div class="flex gap-4">
            <div><span class="text-slate-400">{{ isZh ? '售价' : isEs ? 'Precio de Venta' : 'Sale Price' }}</span><span class="font-bold text-slate-700 dark:text-slate-300 font-mono">${{ part.price.toFixed(2) }}</span></div>
          </div>
          <span class="text-[10px] text-slate-400 font-mono">{{ part.bin_location || '-' }}</span>
        </div>
      </div>

      <div v-if="filteredParts.length === 0" class="text-center py-20">
        <span class="text-4xl">📭</span>
        <p class="text-sm text-slate-400 mt-3">{{ isZh ? '没有找到相关产品' : isEs ? 'Sin productos relacionados' : 'No products found' }}</p>
      </div>
    </div>

    <button 
      @click="continuousScannerVisible = true"
      class="fixed bottom-[calc(5.5rem+env(safe-area-inset-bottom))] right-5 w-14 h-14 bg-emerald-600 text-white rounded-full shadow-lg shadow-emerald-500/40 flex items-center justify-center active:scale-95 transition-transform z-40"
    >
      <PackagePlus :size="26" />
    </button>

    <MobileScannerModal
      :visible="continuousScannerVisible"
      mode="continuous"
      @close="continuousScannerVisible = false"
      @submit="handleContinuousSubmit"
    />

    <!-- 成功 Toast -->
    <Transition name="fade">
      <div v-if="toastMsg" class="fixed top-20 left-1/2 -translate-x-1/2 z-[200] px-5 py-2.5 bg-emerald-600 text-white rounded-full text-sm font-bold shadow-lg whitespace-nowrap flex items-center gap-2">
        {{ toastMsg }}
      </div>
    </Transition>

    <div v-if="selectedPart" ref="panelRef" :style="swipeStyle" class="fixed inset-0 z-50 bg-slate-50 dark:bg-slate-950 flex flex-col">
      <header class="px-5 py-4 flex items-center justify-between border-b border-slate-100 dark:border-slate-800 bg-white dark:bg-slate-900 shrink-0">
        <button @click="selectedPart = null" class="p-2 -ml-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800">
          <ArrowLeft :size="20" class="text-slate-600 dark:text-slate-400" />
        </button>
        <h2 class="font-bold text-sm text-slate-800 dark:text-slate-100">{{ isZh ? '产品详情' : isEs ? 'Detalles del producto' : 'Product Details' }}</h2>
        <div class="w-8"></div>
      </header>

      <div class="flex-1 overflow-y-auto p-5 space-y-6">
        <div class="w-full aspect-square bg-white dark:bg-slate-900 rounded-3xl border border-slate-100 dark:border-slate-800 flex items-center justify-center overflow-hidden">
          <img v-if="selectedPart.image_url" :src="apiUrl(selectedPart.image_url)" class="w-full h-full object-cover" />
          <Package v-else :size="64" class="text-slate-200 dark:text-slate-700" />
        </div>

        <div>
          <div class="flex items-center gap-2 mb-2">
            <span class="text-xs font-bold text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30 px-2 py-0.5 rounded">{{ selectedPart.brand || 'GENERAL' }}</span>
            <span class="text-xs font-bold text-slate-500 bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded">{{ selectedPart.category || '未分类' }}</span>
          </div>
          <h1 class="text-xl font-black text-slate-800 dark:text-slate-100">{{ selectedPart.name }}</h1>
          <p class="text-sm font-mono text-slate-400 mt-1">{{ selectedPart.oem }}</p>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div class="bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-100 dark:border-slate-800">
            <p class="text-[10px] font-bold text-slate-400 uppercase">{{ isZh ? '库存数量' : isEs ? 'Cantidad en stock' : 'Stock Quantity' }}</p>
            <p class="text-2xl font-black font-mono mt-1" :class="getStockClass(selectedPart.stock)">{{ selectedPart.stock }}</p>
          </div>
          <div class="bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-100 dark:border-slate-800">
            <p class="text-[10px] font-bold text-slate-400 uppercase">{{ isZh ? '零售价 (USD)' : isEs ? 'Precio Venta (USD)' : 'Retail Price (USD)' }}</p>
            <p class="text-2xl font-black font-mono text-emerald-600 dark:text-emerald-400 mt-1">${{ selectedPart.price.toFixed(2) }}</p>
          </div>
          <div class="bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-100 dark:border-slate-800">
            <p class="text-[10px] font-bold text-slate-400 uppercase">{{ isZh ? '进货价 (USD)' : isEs ? 'Costo (USD)' : 'Cost Price (USD)' }}</p>
            <p class="text-2xl font-black font-mono text-slate-600 dark:text-slate-300 mt-1">${{ (selectedPart.cost_price || 0).toFixed(2) }}</p>
          </div>
          <div class="bg-white dark:bg-slate-900 p-4 rounded-2xl border border-slate-100 dark:border-slate-800">
            <p class="text-[10px] font-bold text-slate-400 uppercase">{{ isZh ? '货架位置' : isEs ? 'Ubicación' : 'Location' }}</p>
            <p class="text-lg font-black font-mono text-slate-600 dark:text-slate-300 mt-1">{{ selectedPart.bin_location || '-' }}</p>
          </div>
        </div>

        <div class="space-y-3 pt-2">
          <h3 class="text-[11px] font-bold text-slate-400 uppercase tracking-wider ml-1">{{ isZh ? '库存变动历史' : isEs ? 'Historial de inventario' : 'Inventory History' }}</h3>
          <div v-if="productHistory.length === 0" class="text-center py-6 text-xs text-slate-400 bg-white dark:bg-slate-900 rounded-xl border border-slate-100 dark:border-slate-800">{{ isZh ? '暂无历史变动' : isEs ? 'Sin cambios históricos' : 'No historical changes' }}</div>
          <div v-for="tx in productHistory" :key="tx.id" class="bg-white dark:bg-slate-900 rounded-xl p-3 border border-slate-100 dark:border-slate-800 flex justify-between items-center">
            <div>
              <p class="text-xs font-bold text-slate-700 dark:text-slate-300">{{ tx.type === 'IN' ? '采购入库' : '销售出库' }}</p>
              <p class="text-[10px] text-slate-400 font-mono mt-0.5">{{ tx.timestamp }}</p>
            </div>
            <p class="text-sm font-black font-mono" :class="tx.type === 'IN' ? 'text-emerald-500' : 'text-amber-500'">
              {{ tx.type === 'IN' ? '+' : '-' }}{{ tx.quantity }}
            </p>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Search, ArrowLeft, Package, ScanLine, PackagePlus } from 'lucide-vue-next'
import { apiFetch, apiUrl } from '../utils/api'
import { useSwipeBack } from '../composables/useSwipeBack'
import MobileScannerModal from './MobileScannerModal.vue'

const parts = ref([])
const searchQuery = ref('')
const isLoading = ref(true)
const selectedPart = ref(null)
const productHistory = ref([])
const continuousScannerVisible = ref(false)

const toastMsg = ref('')
const showToast = (msg) => {
  toastMsg.value = msg
  setTimeout(() => { toastMsg.value = '' }, 2000)
}

const handleContinuousSubmit = (payload) => {
  continuousScannerVisible.value = false
  refreshParts()
  
  // 计算总数并弹出提示
  const total = payload.reduce((s, p) => s + p.quantity, 0)
  showToast(`✅ 成功入库 ${total} 件商品`)
}

const refreshParts = async () => {
  isLoading.value = true
  try {
    const res = await apiFetch('/api/parts')
    if (res.ok) parts.value = await res.json()
  } finally {
    isLoading.value = false
  }
}

const filteredParts = computed(() => {
  if (!searchQuery.value) return parts.value
  const q = searchQuery.value.toLowerCase()
  return parts.value.filter(p => p.oem.toLowerCase().includes(q) || p.name.toLowerCase().includes(q))
})

const getStockClass = (stock) => {
  if (stock <= 5) return 'text-rose-600 dark:text-rose-400'
  if (stock <= 15) return 'text-amber-600 dark:text-amber-400'
  return 'text-emerald-600 dark:text-emerald-400'
}

const { panelRef, style: swipeStyle } = useSwipeBack(() => {
  selectedPart.value = null
})

const handleScanSuccess = (code) => {
  scannerVisible.value = false
  searchQuery.value = code
  if (filteredParts.value.length === 1) {
    openDetail(filteredParts.value[0])
  }
}

const openDetail = async (part) => {
  selectedPart.value = part
  productHistory.value = []
  try {
    const res = await apiFetch('/api/transactions?page=1&page_size=50')
    if (res.ok) {
      const data = await res.json()
      productHistory.value = (data.items || []).filter(tx => tx.part_oem === part.oem)
    }
  } catch (e) {}
}

// 扫码点击“查看详情”后触发
const handleScannedDetail = (part) => {
  scannerVisible.value = false
  openDetail(part) // 复用你原来的打开详情逻辑
}

onMounted(() => {
  refreshParts()
})
</script>
