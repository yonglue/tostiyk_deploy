<!-- src/components/InventoryAuditView.vue -->
<template>
  <div class="space-y-6 max-w-11xl mx-auto pb-24">
    
    <!-- ==================== 第一层：页面大标题与 Tab 切换 ==================== -->
    <div class="flex flex-wrap items-center justify-between gap-4">
      <div>
        <h2 class="text-xl font-bold text-slate-800 dark:text-slate-200 flex items-center gap-2">
          <span>📋</span>{{ isZh ? '库存盘点（实体清点）' : isEs ? 'Auditoría (Conteo)' : 'Audit (Count)' }}</h2>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">{{ isZh ? '请录入实际清点的数量。留空的商品将被系统忽略，不参与本次盘点。' : isEs ? 'Ingrese cantidad real. Vacíos ignorados.' : 'Enter actual count. Blanks ignored.' }}</p>
      </div>

      <!-- Tab 切换 -->
      <div class="flex bg-slate-200/60 dark:bg-slate-800 p-1 rounded-xl shrink-0">
        <button 
          @click="activeTab = 'audit'"
          :class="activeTab === 'audit' ? 'bg-white dark:bg-slate-700 text-blue-600 dark:text-blue-400 shadow-sm' : 'text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200'"
          class="px-4 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer"
        >{{ isZh ? '盘点操作' : isEs ? 'Operación' : 'Operation' }}</button>
        <button 
          @click="activeTab = 'history'; fetchHistory()"
          :class="activeTab === 'history' ? 'bg-white dark:bg-slate-700 text-blue-600 dark:text-blue-400 shadow-sm' : 'text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200'"
          class="px-4 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer"
        >{{ isZh ? '历史盘点记录' : isEs ? 'Historial' : 'History' }}</button>
      </div>
    </div>

    <!-- ==================== 第二层：操作工具栏（根据 Tab 切换） ==================== -->
    <div class="bg-white dark:bg-slate-800 p-4 md:p-6 rounded-2xl border border-slate-200/80 dark:border-slate-700 shadow-xs flex flex-wrap items-center justify-between gap-4">
      
      <!-- 盘点操作 Tab 的工具栏 -->
      <template v-if="activeTab === 'audit'">
        <!-- 左侧：实时盈亏统计 -->
        <div class="flex items-center gap-4 bg-slate-50 dark:bg-slate-900 px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700">
          <div class="text-center">
            <div class="text-[10px] text-slate-400 dark:text-slate-500 font-bold uppercase tracking-wider">{{ isZh ? '盘盈 (资产增加)' : isEs ? 'Sobrante (Ganancia)' : 'Surplus (Gain)' }}</div>
            <div class="text-sm font-black text-emerald-600 dark:text-emerald-400 font-mono">+ ${{ totalProfitAmount.toFixed(2) }}</div>
          </div>
          <div class="w-px h-6 bg-slate-300 dark:bg-slate-600"></div>
          <div class="text-center">
            <div class="text-[10px] text-slate-400 dark:text-slate-500 font-bold uppercase tracking-wider">{{ isZh ? '盘亏 (资产损失)' : isEs ? 'Faltante (Pérdida)' : 'Shortage (Loss)' }}</div>
            <div class="text-sm font-black text-rose-600 dark:text-rose-400 font-mono">- ${{ totalLossAmount.toFixed(2) }}</div>
          </div>
        </div>

        <!-- 右侧：搜索与操作按钮 -->
        <div class="flex items-center gap-3 flex-wrap">
          <div class="relative w-full sm:w-64">
            <Search class="absolute left-3.5 top-3 text-slate-400 dark:text-slate-500" :size="16" />
            <input 
              v-model="searchQuery" 
              type="text" 
              :placeholder="isZh ? '搜索 OEM 或 配件名称...' : isEs ? 'Buscar OEM o nombre...' : 'Search OEM or name...'" 
              class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-sm rounded-xl pl-10 pr-4 py-2.5 outline-none focus:border-blue-500 dark:text-white"
            />
          </div>
          
          <button 
            @click="exportAuditDiff" 
            :disabled="hasNoChanges"
            class="bg-emerald-50 dark:bg-emerald-900/30 hover:bg-emerald-100 disabled:bg-slate-100 dark:disabled:bg-slate-800 disabled:text-slate-400 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800 px-5 py-2.5 rounded-xl font-bold transition-all cursor-pointer flex items-center gap-2"
          >
            <span>📥</span>{{ isZh ? '导出差异表' : isEs ? 'Exportar diferencias' : 'Export diffs' }}</button>

          <button 
            @click="submitAudit" 
            :disabled="hasNoChanges || isSubmitting"
            class="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 dark:disabled:bg-slate-700 text-white px-6 py-2.5 rounded-xl font-bold shadow-md shadow-blue-500/20 transition-all cursor-pointer flex items-center gap-2"
          >
            <span>💾</span> {{ isSubmitting ? '提交中...' : '提交盘点结果' }}
          </button>
        </div>
      </template>

      <!-- 历史记录 Tab 的工具栏 -->
      <template v-if="activeTab === 'history'">
        <div>
          <h3 class="font-bold text-slate-800 dark:text-slate-200">{{ isZh ? '历史盘点单据' : isEs ? 'Docs Historial' : 'History Docs' }}</h3>
          <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">{{ isZh ? '系统自动汇总的盘点盈亏流水（来源：进销存系统）' : isEs ? 'Flujo automático de inventario' : 'Auto inventory ledger' }}</p>
        </div>
        <button @click="fetchHistory" class="px-4 py-2 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 rounded-xl text-xs font-bold text-slate-600 dark:text-slate-300 transition-colors cursor-pointer flex items-center gap-1.5">{{ isZh ? '🔄 刷新记录' : isEs ? '🔄 Actualizar' : '🔄 Refresh Records' }}</button>
      </template>

    </div>

    <!-- ==================== 第三层：数据主体区 ==================== -->
    
    <!-- 盘点明细表 -->
    <div v-if="activeTab === 'audit'" class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200/80 dark:border-slate-700 shadow-xs overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[900px]">
          <thead>
            <tr class="bg-slate-50 dark:bg-slate-900 border-b border-slate-100 dark:border-slate-700 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              <th class="py-4 px-6">{{ isZh ? '商品信息' : isEs ? 'Info Producto' : 'Product Info' }}</th>
              <th class="py-4 px-6 text-center">{{ isZh ? '系统库存' : isEs ? 'Stock Sistema' : 'System Stock' }}</th>
              <th class="py-4 px-6 text-center">{{ isZh ? '实盘数量' : isEs ? 'Cant. Real' : 'Physical Count' }}</th>
              <th class="py-4 px-6 text-center">{{ isZh ? '盈亏差异' : isEs ? 'Diferencia' : 'Difference' }}</th>
              <th class="py-4 px-6">{{ isZh ? '差异原因 (选填)' : isEs ? 'Motivo (opcional)' : 'Reason (optional)' }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 dark:divide-slate-700 text-sm">
            <tr v-for="item in paginatedParts" :key="item.id" class="hover:bg-blue-50/30 dark:hover:bg-slate-700/50 transition-colors">
              <td class="py-4 px-6">
                <div class="font-bold text-slate-800 dark:text-slate-200">{{ item.name }}</div>
                <div class="text-xs font-mono text-blue-600 dark:text-blue-400 mt-1">{{ item.oem }} <span class="text-slate-400 dark:text-slate-500 ml-1">| {{ item.brand }}</span></div>
                <div class="text-[10px] text-slate-400 dark:text-slate-500 mt-0.5">进价: ${{ (item.cost_price || 0).toFixed(2) }}</div>
              </td>
              <td class="py-4 px-6 text-center font-mono font-bold text-slate-500 dark:text-slate-400">
                {{ item.stock }}
              </td>
              <td class="py-4 px-6 text-center">
                <input 
                  v-model.number="auditForm[item.id]" 
                  type="number" 
                  min="0"
                  :placeholder="isZh ? '未盘' : isEs ? 'No auditado' : 'Not audited'"
                  class="w-24 text-center bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-600 rounded-lg px-3 py-2 font-mono font-black text-slate-900 dark:text-white outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 placeholder:text-slate-300 dark:placeholder:text-slate-600"
                />
              </td>
              <td class="py-4 px-6 text-center font-mono font-black">
                <span v-if="auditForm[item.id] === null || auditForm[item.id] === ''" class="text-slate-300 dark:text-slate-600">-</span>
                <span v-else-if="getDiff(item) === 0" class="text-slate-400 dark:text-slate-500">0</span>
                <span v-else-if="getDiff(item) > 0" class="text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-900/30 px-2 py-0.5 rounded border border-emerald-100 dark:border-emerald-800">+{{ getDiff(item) }}</span>
                <span v-else class="text-rose-600 dark:text-rose-400 bg-rose-50 dark:bg-rose-900/30 px-2 py-0.5 rounded border border-rose-100 dark:border-rose-800">{{ getDiff(item) }}</span>
              </td>
              <td class="py-4 px-6">
                <input 
                  v-model="reasons[item.id]" 
                  type="text" 
                  :placeholder="isZh ? '例如：破损、丢失...' : isEs ? 'Ej: Dañado, perdido...' : 'Ex: Damaged, lost...'"
                  class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg px-3 py-2 text-xs outline-none focus:border-blue-500 dark:text-white disabled:opacity-50 dark:disabled:bg-slate-800"
                  :disabled="auditForm[item.id] === null || auditForm[item.id] === '' || getDiff(item) === 0"
                />
              </td>
            </tr>
            <tr v-if="paginatedParts.length === 0">
              <td colspan="5" class="py-16 text-center text-slate-400 dark:text-slate-500 text-sm font-bold"><ClipboardList :size="40" class="mx-auto text-slate-300 dark:text-slate-600 mb-3" stroke-width="1.5" />{{ isZh ? '没有找到符合条件的商品' : isEs ? 'Sin productos coincidentes' : 'No matching products' }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 🌟 新增：分页组件 -->
      <div v-if="totalPages > 1" class="px-6 py-4 bg-slate-50 dark:bg-slate-900 border-t border-slate-100 dark:border-slate-700 flex flex-wrap items-center justify-between gap-4 text-xs">
        <span class="text-slate-500 dark:text-slate-400 font-medium">
          显示第 <strong class="text-slate-800 dark:text-slate-200">{{ (currentPage - 1) * pageSize + 1 }}</strong> 到 <strong class="text-slate-800 dark:text-slate-200">{{ Math.min(currentPage * pageSize, filteredParts.length) }}</strong> 条，共 <strong class="text-slate-800 dark:text-slate-200">{{ filteredParts.length }}</strong>{{ isZh ? '个商品' : isEs ? 'Productos' : 'Products' }}</span>
        
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-1.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-600 rounded-xl px-2 py-1 shadow-2xs">
            <span class="text-slate-400 text-[11px]">{{ isZh ? '跳转到' : isEs ? 'Ir a' : 'Go to' }}</span>
            <input 
              type="number" 
              min="1" 
              :max="totalPages" 
              v-model.number="jumpPageInput" 
              @keyup.enter="handleJumpPage"
              class="w-12 text-center font-mono font-bold text-blue-600 dark:text-blue-400 bg-slate-50 dark:bg-slate-900 rounded-lg py-1 outline-none border border-slate-200 dark:border-slate-600 focus:border-blue-500 text-xs" 
            />
            <span class="text-slate-400 text-[11px]">/ {{ totalPages }} 页</span>
            <button 
              @click="handleJumpPage" 
              class="bg-blue-50 dark:bg-blue-900/30 hover:bg-blue-100 dark:hover:bg-blue-800 text-blue-600 dark:text-blue-400 px-2.5 py-1 rounded-lg font-bold transition-colors cursor-pointer text-[11px]"
            >{{ isZh ? '跳转' : isEs ? 'Ir' : 'Go' }}</button>
          </div>

          <div class="flex items-center gap-1.5">
            <button 
              @click="currentPage--" 
              :disabled="currentPage === 1"
              class="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 font-semibold text-slate-600 dark:text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors cursor-pointer"
            >{{ isZh ? '上一页' : isEs ? 'Anterior' : 'Prev' }}</button>
            <span class="px-3 py-1 font-mono font-bold text-slate-700 dark:text-slate-300">
              {{ currentPage }} / {{ totalPages }}
            </span>
            <button 
              @click="currentPage++" 
              :disabled="currentPage === totalPages"
              class="px-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-800 font-semibold text-slate-600 dark:text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors cursor-pointer"
            >{{ isZh ? '下一页' : isEs ? 'Siguiente' : 'Next' }}</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 历史盘点表 -->
    <div v-if="activeTab === 'history'" class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200/80 dark:border-slate-700 shadow-xs overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[800px]">
          <thead>
            <tr class="bg-slate-50 dark:bg-slate-900 border-b border-slate-100 dark:border-slate-700 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              <th class="py-4 px-6">{{ isZh ? '盘点时间 / 批次 / 经办人' : isEs ? 'Fecha / Lote / Op.' : 'Time / Batch / Op.' }}</th>
              <th class="py-4 px-6">{{ isZh ? '商品信息' : isEs ? 'Info Producto' : 'Product Info' }}</th>
              <th class="py-4 px-6 text-center">{{ isZh ? '变动类型' : isEs ? 'Tipo Cambio' : 'Change Type' }}</th>
              <th class="py-4 px-6 text-center">{{ isZh ? '变动数量' : isEs ? 'Cant. Cambio' : 'Change Qty' }}</th>
              <th class="py-4 px-6 text-right">{{ isZh ? '按进价折算金额' : isEs ? 'Monto al costo' : 'Amount at cost' }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 dark:divide-slate-700 text-sm">
            <tr v-if="isFetchingHistory" class="text-center">
              <td colspan="5" class="py-10 text-slate-400 text-xs">{{ isZh ? '加载中...' : isEs ? 'Cargando...' : 'Loading...' }}</td>
            </tr>
            <tr v-else-if="historyList.length === 0" class="text-center">
              <td colspan="5" class="py-16 text-slate-400 text-xs font-bold"><ClipboardList :size="40" class="mx-auto text-slate-300 dark:text-slate-600 mb-3" stroke-width="1.5" />{{ isZh ? '暂无历史盘点记录' : isEs ? 'Sin historial de inventario' : 'No inventory history' }}</td>
            </tr>
            <tr v-for="tx in historyList" :key="tx.id" class="hover:bg-blue-50/30 dark:hover:bg-slate-700/50 transition-colors">
              <td class="py-4 px-6">
                <div class="font-mono text-xs text-slate-600 dark:text-slate-400">{{ tx.timestamp }}</div>
                <div class="text-[10px] text-blue-600 dark:text-blue-400 font-bold mt-1">批次: {{ parseTxInfo(tx.customer_or_supplier).batch }}</div>
                <div class="text-[10px] text-slate-500 dark:text-slate-400 mt-0.5">经办: {{ parseTxInfo(tx.customer_or_supplier).operator }}</div>
              </td>
              <td class="py-4 px-6">
                <div class="font-bold text-slate-800 dark:text-slate-200">{{ tx.part_name }}</div>
                <div class="text-xs font-mono text-slate-400 dark:text-slate-500 mt-0.5">{{ tx.part_oem }}</div>
              </td>
              <td class="py-4 px-6 text-center">
                <span v-if="tx.type === 'IN'" class="bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800 px-2.5 py-1 rounded-md text-xs font-bold">{{ isZh ? '盘盈 (IN)' : isEs ? 'Sobrante (IN)' : 'Surplus (IN)' }}</span>
                <span v-else class="bg-rose-50 dark:bg-rose-900/30 text-rose-700 dark:text-rose-400 border border-rose-200 dark:border-rose-800 px-2.5 py-1 rounded-md text-xs font-bold">{{ isZh ? '盘亏 (OUT)' : isEs ? 'Faltante (OUT)' : 'Shortage (OUT)' }}</span>
              </td>
              <td class="py-4 px-6 text-center font-mono font-black" :class="tx.type === 'IN' ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'">
                {{ tx.type === 'IN' ? '+' : '-' }}{{ tx.quantity }}
              </td>
              <td class="py-4 px-6 text-right font-mono font-bold text-slate-700 dark:text-slate-300">
                $ {{ Number(tx.total_amount || 0).toFixed(2) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<script setup>
import { useI18n } from '../composables/useI18n'

const { currentLang } = useI18n()

const isZh = computed(() => currentLang.value === 'zh')
const isEs = computed(() => currentLang.value === 'es')


import { ref, computed, onMounted, reactive, watch } from 'vue'
import { Search, ClipboardList } from 'lucide-vue-next'
import { apiFetch } from '../utils/api'
import { useNotifications } from '../composables/useNotifications'

const { showSuccessModal } = useNotifications()

const activeTab = ref('audit')
const parts = ref([])
const searchQuery = ref('')
const isSubmitting = ref(false)

// 🌟 分页状态
const currentPage = ref(1)
const pageSize = 10
const jumpPageInput = ref(1)

const auditForm = reactive({})
const reasons = reactive({})

const fetchParts = async () => {
  try {
    const res = await apiFetch('/api/parts')
    if (res.ok) {
      parts.value = await res.json()
      parts.value.forEach(p => {
        auditForm[p.id] = null
        reasons[p.id] = ''
      })
    }
  } catch (e) { console.error(e) }
}

const filteredParts = computed(() => {
  if (!searchQuery.value) return parts.value
  const q = searchQuery.value.toLowerCase()
  return parts.value.filter(p => 
    p.oem.toLowerCase().includes(q) || 
    p.name.toLowerCase().includes(q)
  )
})

// 🌟 分页计算属性
const totalPages = computed(() => {
  return Math.ceil(filteredParts.value.length / pageSize) || 1
})

const paginatedParts = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredParts.value.slice(start, start + pageSize)
})

// 🌟 跳转处理
const handleJumpPage = () => {
  let target = parseInt(jumpPageInput.value)
  if (isNaN(target)) return
  if (target < 1) target = 1
  if (target > totalPages.value) target = totalPages.value
  currentPage.value = target
  jumpPageInput.value = target
}

// 🌟 监听搜索和页码变化
watch(searchQuery, () => {
  currentPage.value = 1
  jumpPageInput.value = 1
})

watch(currentPage, (val) => {
  jumpPageInput.value = val
})

const getDiff = (item) => {
  const rawVal = auditForm[item.id]
  if (rawVal === null || rawVal === undefined || rawVal === '') return 0
  const actual = Number(rawVal)
  return isNaN(actual) ? 0 : actual - item.stock
}

const totalProfitAmount = computed(() => {
  return parts.value.reduce((sum, p) => {
    const diff = getDiff(p)
    return diff > 0 ? sum + (diff * (p.cost_price || 0)) : sum
  }, 0)
})

const totalLossAmount = computed(() => {
  return parts.value.reduce((sum, p) => {
    const diff = getDiff(p)
    return diff < 0 ? sum + (Math.abs(diff) * (p.cost_price || 0)) : sum
  }, 0)
})

const hasNoChanges = computed(() => {
  return parts.value.every(p => {
    const rawVal = auditForm[p.id]
    if (rawVal === null || rawVal === undefined || rawVal === '') return true
    return getDiff(p) === 0
  })
})

const submitAudit = async () => {
  if (hasNoChanges.value) return
  
  const diffItems = parts.value
    .filter(p => {
      const rawVal = auditForm[p.id]
      if (rawVal === null || rawVal === undefined || rawVal === '') return false
      return getDiff(p) !== 0
    })
    .map(p => ({
      part_id: p.id,
      actual_stock: Number(auditForm[p.id]),
      reason: reasons[p.id] || ''
    }))

  if (diffItems.length === 0) {
    showSuccessModal('⚠️ 没有需要提交的盘点差异')
    return
  }

  isSubmitting.value = true
  try {
    const res = await apiFetch('/api/inventory/audit', {
      method: 'POST',
      body: JSON.stringify({ items: diffItems })
    })
    
    if (res.ok) {
      const data = await res.json()
      showSuccessModal(`✅ ${data.message}`)
      fetchParts()
      if (activeTab.value === 'history') fetchHistory()
    } else {
      const err = await res.json()
      showSuccessModal(`❌ 盘点提交失败: ${err.detail}`)
    }
  } catch (e) {
    showSuccessModal('❌ 网络异常')
  } finally {
    isSubmitting.value = false
  }
}

// ==================== 🌟 导出盘点差异 CSV ====================
const exportAuditDiff = () => {
  const diffItems = parts.value.filter(p => {
    const rawVal = auditForm[p.id]
    if (rawVal === null || rawVal === undefined || rawVal === '') return false
    return getDiff(p) !== 0
  })

  if (diffItems.length === 0) {
    showSuccessModal('⚠️ 当前没有盘点差异可以导出')
    return
  }

  let csvContent = "\uFEFF" 
  csvContent += "OEM 编号,配件名称,适配品牌,系统库存,实盘数量,盈亏差异,进价 (USD),差异金额 (USD),差异原因\r\n"

  diffItems.forEach(item => {
    const diff = getDiff(item)
    const cost = Number(item.cost_price) || 0
    const amount = Math.abs(diff) * cost
    const reason = reasons[item.id] || '未填写'

    const row = [
      `"${item.oem}"`,
      `"${item.name}"`,
      `"${item.brand || ''}"`,
      item.stock,
      auditForm[item.id],
      diff > 0 ? `+${diff}` : diff,
      cost.toFixed(2),
      amount.toFixed(2),
      `"${reason}"`
    ].join(",")
    
    csvContent += row + "\r\n"
  })

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement("a")
  link.href = url
  
  const now = new Date()
  const dateStr = now.toISOString().slice(0, 10)
  const timeStr = now.toTimeString().slice(0, 5).replace(':', '')
  link.download = `盘点差异_${dateStr}_${timeStr}.csv`
  
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

// ==================== 🌟 历史盘点数据 ====================
const historyList = ref([])
const isFetchingHistory = ref(false)

const fetchHistory = async () => {
  isFetchingHistory.value = true
  try {
    const res = await apiFetch('/api/transactions')
    if (res.ok) {
      const data = await res.json()
      // 🌟 兼容后端分页结构 {items: [...]}
      const allTxs = Array.isArray(data) ? data : (data.items || [])
      historyList.value = allTxs.filter(tx => tx.customer_or_supplier?.includes('库存盘点调整'))
    }
  } catch (e) {
    console.error(e)
    showSuccessModal('❌ 获取盘点历史失败')
  } finally {
    isFetchingHistory.value = false
  }
}

const parseTxInfo = (infoStr) => {
  if (!infoStr) return { batch: '-', operator: '-' }
  const parts = infoStr.split('|')
  if (parts.length >= 3) {
    return { batch: parts[1], operator: parts[2] }
  }
  return { batch: '历史记录', operator: '-' }
}

onMounted(() => {
  fetchParts()
  fetchHistory() 
})
</script>