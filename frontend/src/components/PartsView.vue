<!-- src/components/PartsView.vue -->
<template>
  <div class="space-y-6 max-w-11xl mx-auto pb-24">
    
    <!-- ==================== 第一层：页面大标题 ==================== -->
    <div class="flex flex-wrap items-center justify-between gap-4">
      <div>
        <h2 class="text-xl font-bold text-slate-800 flex items-center gap-2">
          <span></span> {{ t.inventory.title }}
        </h2>
        <p class="text-xs text-slate-500 mt-1">{{ isZh ? '管理汽车配件的入库、出库、定价及多图档案。' : isEs ? 'Gestión de entradas, salidas y precios.' : 'Manage stock in/out, pricing, and photos.' }}</p>
      </div>
    </div>

    <!-- ==================== 第二层：操作工具栏 ==================== -->
    <div class="bg-white p-4 md:p-6 rounded-2xl border border-slate-200/80 shadow-xs flex flex-wrap items-center justify-between gap-4">
      
      <!-- 左侧：搜索与筛选 -->
      <div class="flex items-center gap-3 flex-wrap w-full md:w-auto">
        <!-- 搜索框 -->
        <div class="w-full md:w-72">
          <BaseSearchInput 
            :model-value="searchQuery" 
            @update:model-value="$emit('update:searchQuery', $event)" 
            placeholder="搜索 OEM / 名称..." 
          />
        </div>

        <!-- 分类下拉 -->
        <div class="w-44">
          <BaseSelect 
            v-model="selectedCategory" 
            :options="[
              { label: tExt.allCategories, value: 'ALL' },
              ...categoriesList.filter(c => c !== 'ALL').map(c => ({ label: c, value: c }))
            ]" 
          />
        </div>

        <!-- 品牌下拉 -->
        <div class="w-44">
          <BaseSelect 
            :model-value="selectedBrand"
            @update:model-value="$emit('update:selectedBrand', $event)"
            :options="[
              { label: tExt.allBrands, value: 'ALL' },
              ...brandsList.filter(b => b !== 'ALL').map(b => ({ label: b, value: b }))
            ]" 
          />
        </div>
      </div> <!-- 👈 修复点：补上了左侧容器的闭合 -->

      <!-- 右侧：操作按钮 -->
      <div class="flex items-center gap-3 w-full md:w-auto justify-between md:justify-end">
        <button 
          v-if="selectedIds.length > 0" 
          @click="openBatchDeleteModal" 
          class="flex items-center gap-2 bg-rose-50 hover:bg-rose-100 text-rose-600 border border-rose-200/80 px-4 py-2.5 rounded-xl text-xs font-bold shadow-xs transition-all cursor-pointer"
        >
          <span>{{ tExt.batchDelete }} ({{ tExt.batchSelected }} {{ selectedIds.length }})</span>
        </button>

        <button
          @click="$emit('open-add-modal')"
          class="flex items-center justify-center gap-2 bg-accent hover:bg-accent-hover text-white px-5 py-2.5 rounded-xl font-bold text-sm shadow-sm transition-all cursor-pointer"
        >
          <Plus :size="16" />
          <span>{{ t.inventory.addBtn }}</span>
        </button>
      </div>
    </div>

    <!-- ==================== 第三层：数据表格 ==================== -->
    <div class="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[900px]">
          <thead>
            <tr class="bg-slate-50 dark:bg-slate-800/80 border-b border-slate-100 dark:border-slate-700 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
              <th class="py-2.5 px-3 w-12 text-center">
                <input type="checkbox" :checked="isAllSelected" @change="toggleSelectAll" class="rounded border-slate-300 text-accent focus:ring-0 w-4 h-4 cursor-pointer" />
              </th>
              <th class="py-2.5 px-3">{{ t.inventory.colImage }}</th>
              <th class="py-2.5 px-3">{{ t.inventory.colOem }}</th>
              <th class="py-2.5 px-3">{{ t.inventory.colName }}</th>
              <th class="py-2.5 px-3">📍 {{ t.inventory.colBin }}</th>
              <th class="py-2.5 px-3">{{ t.inventory.colStock }}</th>
              <th class="py-2.5 px-3">{{ t.inventory.colPriceUsd }}</th>
              <th class="py-2.5 px-3 text-amber-600">{{ t.inventory.costPrice }}</th>
              <th class="py-2.5 px-3 text-emerald-600">{{ t.inventory.profit }}</th>
              <th class="py-2.5 px-3 text-center">{{ t.common.actions }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr v-for="item in paginatedParts" :key="item.id || item.oem" class="hover:bg-accent/10/50 dark:hover:bg-blue-900/20 transition-colors cursor-pointer group border-b border-slate-100 dark:border-slate-800" @click="openDetailDrawer(item)">
              <td class="py-2.5 px-3 text-center" @click.stop>
                <input type="checkbox" :checked="selectedIds.includes(item.id)" @change="toggleSelect(item.id)" class="rounded border-slate-300 text-accent focus:ring-0 w-4 h-4 cursor-pointer" />
              </td>
              <td class="py-2.5 px-3" @click.stop>
                <div class="flex items-center gap-1.5">
                  <template v-if="parseImages(item.image_url).length > 0">
                    <div @click="$emit('open-gallery', parseImages(item.image_url), 0)" class="w-10 h-10 rounded-xl overflow-hidden border border-slate-200 cursor-pointer hover:scale-105 transition-transform shadow-2xs relative group/img">
                      <img :src="parseImages(item.image_url)[0].startsWith('http') ? parseImages(item.image_url)[0] : apiUrl(parseImages(item.image_url)[0])" class="w-full h-full object-cover" />
                      <div v-if="parseImages(item.image_url).length > 1" class="absolute bottom-0 right-0 bg-slate-900/70 text-white text-[8px] px-1 rounded-tl font-mono">+{{ parseImages(item.image_url).length - 1 }}</div>
                    </div>
                  </template>
                  <div v-else class="w-10 h-10 rounded-xl bg-slate-100 border border-slate-200 flex items-center justify-center text-slate-400 text-[10px] font-bold">{{ t.inventory.noImage }}</div>
                </div>
              </td>
              <td class="py-2.5 px-3 font-mono font-bold text-slate-800">{{ item.oem }}</td>
              <td class="py-2.5 px-3 font-medium text-slate-900">{{ item.name }}</td>
              <td class="py-2.5 px-3">
                <span class="inline-flex items-center gap-1 bg-emerald-50 text-emerald-700 px-2.5 py-1 rounded-lg text-xs font-semibold font-mono border border-emerald-200/60">📍 {{ item.bin_location || '—' }}</span>
              </td>
              <td class="py-2.5 px-3 font-bold" :class="item.stock <= 5 ? 'text-rose-600' : 'text-slate-800'">{{ item.stock }}</td>
              <td class="py-2.5 px-3 font-bold text-accent">$ {{ Number(item.price || 0).toFixed(2) }}</td>
              <td class="py-2.5 px-3 font-bold text-amber-600">$ {{ Number(item.cost_price || 0).toFixed(2) }}</td>
              <td class="py-2.5 px-3 font-black">
                <span :class="(item.price - (item.cost_price || 0)) > 0 ? 'text-emerald-600' : 'text-rose-500'">$ {{ Number((item.price || 0) - (item.cost_price || 0)).toFixed(2) }}</span>
              </td>
              <td class="py-2.5 px-3 text-center" @click.stop>
                <button @click="$emit('delete-part', item)" class="text-xs bg-rose-50 hover:bg-rose-100 text-rose-600 px-3 py-1 rounded-lg font-semibold transition-colors cursor-pointer">{{ t.common.delete }}</button>
              </td>
            </tr>
            <tr v-if="filteredParts.length === 0">
              <td colspan="10" class="py-16 text-center text-slate-400 text-sm">
                <span class="text-4xl block mb-3">📭</span>{{ tExt.emptyParts }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页 -->
      <div v-if="totalPages > 1" class="px-6 py-4 bg-slate-50 border-t border-slate-100 flex flex-wrap items-center justify-between gap-4 text-xs">
        <span class="text-slate-500 font-medium">
          {{ tExt.showing }} <strong class="text-slate-800">{{ (currentPage - 1) * pageSize + 1 }}</strong> {{ tExt.to }} <strong class="text-slate-800">{{ Math.min(currentPage * pageSize, filteredParts.length) }}</strong> {{ tExt.of }} <strong class="text-slate-800">{{ filteredParts.length }}</strong> {{ tExt.products }}
        </span>
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-1.5 bg-white border border-slate-200 rounded-xl px-2 py-1 shadow-2xs">
            <span class="text-slate-400 text-[11px]">{{ tExt.jumpTo }}</span>
            <input type="number" min="1" :max="totalPages" v-model.number="jumpPageInput" @keyup.enter="handleJumpPage" class="w-12 text-center font-mono font-bold text-accent bg-slate-50 rounded-lg py-1 outline-none border border-slate-200 focus:border-accent text-xs" />
            <span class="text-slate-400 text-[11px]">/ {{ totalPages }} {{ tExt.page }}</span>
            <button @click="handleJumpPage" class="bg-accent/10 hover:bg-blue-100 text-accent px-2.5 py-1 rounded-lg font-bold transition-colors cursor-pointer text-[11px]">{{ tExt.jumpBtn }}</button>
          </div>
          <div class="flex items-center gap-1.5">
            <button @click="currentPage--" :disabled="currentPage === 1" class="px-3 py-1.5 rounded-lg border border-slate-200 bg-white font-semibold text-slate-600 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-100 transition-colors cursor-pointer">{{ tExt.prevPage }}</button>
            <span class="px-3 py-1 font-mono font-bold text-slate-700">{{ currentPage }} / {{ totalPages }}</span>
            <button @click="currentPage++" :disabled="currentPage === totalPages" class="px-3 py-1.5 rounded-lg border border-slate-200 bg-white font-semibold text-slate-600 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-100 transition-colors cursor-pointer">{{ tExt.nextPage }}</button>
          </div>
        </div>
      </div>
    </div>

    <!-- ==================== 通用右侧 Drawer 详情/编辑 ==================== -->
    <SideDrawer :visible="detailDrawerVisible" :title="drawerMode === 'read' ? t.inventory.detailTitle : tExt.editTitle" :icon="drawerMode === 'read' ? '📋' : '✏️'" @close="closeDrawer">
      <template #header-actions>
        <template v-if="drawerMode === 'read'">
          <button @click="switchToEdit" class="text-xs bg-accent/10 hover:bg-blue-100 text-accent px-3 py-1.5 rounded-lg font-semibold transition-colors cursor-pointer">{{ t.common.edit }}</button>
          <button @click="onDeleteFromDrawer" class="text-xs bg-rose-50 hover:bg-rose-100 text-rose-600 px-3 py-1.5 rounded-lg font-semibold transition-colors cursor-pointer">{{ t.common.delete }}</button>
        </template>
      </template>

      <div class="p-6">
        <!-- 只读态 -->
        <div v-if="drawerMode === 'read'" class="space-y-5">
          <div v-if="parseImages(editingPart.image_url).length > 0" class="flex flex-wrap gap-2">
            <div v-for="(img, idx) in parseImages(editingPart.image_url)" :key="idx" @click="$emit('open-gallery', parseImages(editingPart.image_url), idx)" class="w-20 h-20 rounded-xl overflow-hidden border border-slate-200 cursor-pointer hover:scale-105 transition-transform">
              <img :src="img.startsWith('http') ? img : apiUrl(img)" class="w-full h-full object-cover" />
            </div>
          </div>
          <div v-else class="w-full h-24 rounded-xl bg-slate-50 border border-dashed border-slate-200 flex items-center justify-center text-slate-400 text-xs">{{ t.inventory.noImage }}</div>

          <div class="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ t.inventory.colOem }}</p>
              <p class="font-mono font-bold text-slate-800">{{ editingPart.oem }}</p>
            </div>
            <div>
              <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ t.inventory.colName }}</p>
              <p class="font-medium text-slate-900">{{ editingPart.name }}</p>
            </div>
            <div>
              <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ t.inventory.colStock }}</p>
              <p class="font-bold font-mono" :class="editingPart.stock <= 5 ? 'text-rose-600' : 'text-slate-800'">{{ editingPart.stock }}</p>
            </div>
            <div>
              <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ t.inventory.colBin }}</p>
              <p class="font-mono text-slate-800">{{ editingPart.bin_location || '—' }}</p>
            </div>
            <div>
              <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ t.inventory.colPriceUsd }}</p>
              <p class="font-bold text-accent">$ {{ Number(editingPart.price || 0).toFixed(2) }}</p>
            </div>
            <div>
              <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ t.inventory.costPrice }}</p>
              <p class="font-bold text-amber-600">$ {{ Number(editingPart.cost_price || 0).toFixed(2) }}</p>
            </div>
            <div>
              <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ t.inventory.profit }}</p>
              <p class="font-black" :class="(editingPart.price - (editingPart.cost_price || 0)) > 0 ? 'text-emerald-600' : 'text-rose-500'">$ {{ Number((editingPart.price || 0) - (editingPart.cost_price || 0)).toFixed(2) }}</p>
            </div>
            <div>
              <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ t.inventory.taxRate }}</p>
              <p class="font-bold text-slate-800">{{ editingPart.tax_rate === 0.16 ? t.inventory.tax16 : (editingPart.tax_rate === 0.08 ? t.inventory.tax8 : t.inventory.tax0) }}</p>
            </div>
            <div>
              <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ t.inventory.colCategory }}</p>
              <p class="text-slate-700">{{ editingPart.category || tExt.uncategorized }}</p>
            </div>
            <div>
              <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ t.inventory.colBrand }}</p>
              <p class="text-slate-700">{{ editingPart.brand || '—' }}</p>
            </div>
          </div>

          <div>
            <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">🔗 {{ tExt.crossRef }}</p>
            <p class="text-xs font-mono text-slate-600 bg-slate-50 rounded-xl p-3 whitespace-pre-wrap min-h-[48px]">{{ editingPart.cross_references || '—' }}</p>
          </div>
        </div>

        <!-- 编辑态 -->
        <div v-else class="space-y-4">
          <BaseInput v-model="editingPart.oem" label="OEM 编号 *" placeholder="输入 OEM..." />
          <BaseInput v-model="editingPart.name" label="配件名称 *" placeholder="输入配件名称..." />
          <BaseInput v-model="editingPart.category" label="分类" />
          <BaseInput v-model="editingPart.brand" label="品牌" />
          <BaseInput v-model.number="editingPart.stock" type="number" label="库存数量" />
          <BaseInput v-model.number="editingPart.price" type="number" label="零售价 ($)" />
          <BaseInput v-model.number="editingPart.cost_price" type="number" label="成本价 ($)" />
          
          <BaseSelect 
            v-model.number="editingPart.tax_rate" 
            label="税率"
            :options="[
              { label: '16% (标准)', value: 0.16 },
              { label: '8% (减免)', value: 0.08 },
              { label: '0% (免税)', value: 0 }
            ]" 
          />

          <BaseInput v-model="editingPart.bin_location" label="货架位" placeholder="例如 A-01" />
        </div>
      </div>

      <!-- 底部操作区 -->
      <template #footer>
        <div v-if="drawerMode === 'edit'" class="px-6 py-4 border-t border-slate-100 flex items-center justify-end gap-3">
          <button @click="switchToRead" class="px-5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-xl text-xs font-bold transition-colors cursor-pointer">{{ t.common.cancel }}</button>
          <button @click="saveEditedPart" class="px-6 py-2.5 bg-accent hover:bg-accent-hover text-white rounded-xl text-xs font-bold shadow-sm transition-all cursor-pointer">{{ tExt.saveChanges }}</button>
        </div>
      </template>
    </SideDrawer>

    <!-- 批量删除确认 -->
    <ConfirmDialog
      :visible="batchDeleteModalVisible"
      overlay-class="bg-slate-900/40"
      :title="tExt.batchDeleteTitle"
      :message="tExt.batchDeleteMsg"
      :cancel-text="t.common.cancel"
      :confirm-text="t.common.delete"
      @cancel="batchDeleteModalVisible = false"
      @confirm="confirmBatchDelete"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { Package, XCircle, Trash2, Plus } from 'lucide-vue-next';
import { useI18n } from '../composables/useI18n'
import { apiUrl, apiFetch } from '../utils/api'
import { useNotifications } from '../composables/useNotifications'
import ConfirmDialog from './ConfirmDialog.vue'
import SideDrawer from './SideDrawer.vue'
import BaseSearchInput from './ui/BaseSearchInput.vue'
import BaseInput from './ui/BaseInput.vue'
import BaseSelect from './ui/BaseSelect.vue'

const props = defineProps({
  partsList: Array,
  searchQuery: String,
  selectedBrand: String,
  brandsList: Array,
  bcvRate: Number
})

const emit = defineEmits(['open-add-modal', 'open-gallery', 'delete-part', 'refresh-data'])
const { t, currentLang } = useI18n()
const { showSuccessModal } = useNotifications()

const isZh = computed(() => currentLang.value === 'zh')
const isEs = computed(() => currentLang.value === 'es')

const tExt = computed(() => {
  const isZh = currentLang.value === 'zh'
  const isEs = currentLang.value === 'es'
  return {
    allBrands: isZh ? '全部品牌' : isEs ? 'Todas las Marcas' : 'All Brands',
    allCategories: isZh ? '全部分类' : isEs ? 'Todas las Categorías' : 'All Categories',
    uncategorized: isZh ? '未分类' : isEs ? 'Sin categoría' : 'Uncategorized',
    batchDelete: isZh ? '批量删除' : isEs ? 'Eliminar Lote' : 'Batch Delete',
    batchSelected: isZh ? '已选' : isEs ? 'seleccionados' : 'selected',
    emptyParts: isZh ? '没有找到符合条件的商品档案' : isEs ? 'No se encontraron repuestos' : 'No parts found',
    showing: isZh ? '显示第' : isEs ? 'Mostrando' : 'Showing',
    to: isZh ? '到' : isEs ? 'a' : 'to',
    of: isZh ? '条，共' : isEs ? 'de' : 'of',
    products: isZh ? '个商品' : isEs ? 'productos' : 'items',
    jumpTo: isZh ? '跳转到' : isEs ? 'Ir a' : 'Go to',
    page: isZh ? '页' : isEs ? 'Página' : 'Page',
    jumpBtn: isZh ? '跳转' : isEs ? 'Ir' : 'Go',
    prevPage: isZh ? '上一页' : isEs ? 'Anterior' : 'Prev',
    nextPage: isZh ? '下一页' : isEs ? 'Siguiente' : 'Next',
    editTitle: isZh ? '编辑配件档案' : isEs ? 'Editar Repuesto' : 'Edit Part',
    crossRef: isZh ? '交叉适配编号与备注' : isEs ? 'Referencias Cruzadas / Notas' : 'Cross-References / Notes',
    updateImages: isZh ? '更新实物多图 (可选)' : isEs ? 'Actualizar fotos (Opcional)' : 'Update photos (Optional)',
    saveChanges: isZh ? '保存修改' : isEs ? 'Guardar Cambios' : 'Save Changes',
    batchDeleteTitle: isZh ? '确认批量删除商品' : isEs ? 'Confirmar Eliminación en Lote' : 'Confirm Batch Delete',
    batchDeleteMsg: isZh ? `确定要批量删除选中的 ${selectedIds.value.length} 个商品档案吗？删除后不可恢复。` : isEs ? `¿Eliminar ${selectedIds.value.length} repuestos seleccionados? No se puede deshacer.` : `Delete ${selectedIds.value.length} selected parts? Cannot be undone.`,
  }
})

const pageSize = 10
const currentPage = ref(1)
const jumpPageInput = ref(1)
const selectedIds = ref([])
const batchDeleteModalVisible = ref(false)

const selectedCategory = ref('ALL')

const categoriesList = computed(() => {
  return [
    'ALL',
    ...Array.from(new Set(props.partsList.map(p => p.category || tExt.value.uncategorized)))
  ]
})

const detailDrawerVisible = ref(false)
const drawerMode = ref('read')

const editingPart = ref({ 
  id: null, oem: '', name: '', brand: '', category: '', stock: 0, 
  price: 0, cost_price: 0, tax_rate: 0.16, bin_location: '', cross_references: '', image_url: ''
})
const editFiles = ref([])

const parseImages = (imageUrlStr) => {
  if (!imageUrlStr) return []
  try {
    const parsed = JSON.parse(imageUrlStr)
    if (Array.isArray(parsed)) return parsed.slice(0, 5)
  } catch (e) {
    if (imageUrlStr.startsWith('http') || imageUrlStr.startsWith('/uploads/')) return [imageUrlStr]
  }
  return []
}

const filteredParts = computed(() => {
  const query = props.searchQuery ? props.searchQuery.trim().toLowerCase() : ''
  const cleanQuery = query.replace(/[^a-z0-9]/g, '')

  return props.partsList.filter(i => {
    const matchBrand = props.selectedBrand === 'ALL' || i.brand === props.selectedBrand
    const itemCat = i.category || tExt.value.uncategorized
    const matchCategory = selectedCategory.value === 'ALL' || itemCat === selectedCategory.value

    if (!query) return matchBrand && matchCategory

    const cleanOem = i.oem ? i.oem.toLowerCase().replace(/[^a-z0-9]/g, '') : ''
    const cleanName = i.name ? i.name.toLowerCase() : ''
    const cleanBrand = i.brand ? i.brand.toLowerCase() : ''
    const rawOem = i.oem ? i.oem.toLowerCase() : ''
    const rawName = i.name ? i.name.toLowerCase() : ''
    const rawCross = i.cross_references ? i.cross_references.toLowerCase() : ''

    const matchSearch = 
      cleanOem.includes(cleanQuery) || rawOem.includes(query) || 
      cleanName.includes(query) || rawName.includes(query) ||
      cleanBrand.includes(query) || rawCross.includes(query)

    return matchBrand && matchCategory && matchSearch
  })
})

const totalPages = computed(() => {
  return Math.ceil(filteredParts.value.length / pageSize) || 1
})

const paginatedParts = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredParts.value.slice(start, start + pageSize)
})

const handleJumpPage = () => {
  let target = parseInt(jumpPageInput.value)
  if (isNaN(target)) return
  if (target < 1) target = 1
  if (target > totalPages.value) target = totalPages.value
  currentPage.value = target
  jumpPageInput.value = target
}

watch([() => props.searchQuery, () => props.selectedBrand, selectedCategory], () => {
  currentPage.value = 1
  jumpPageInput.value = 1
  selectedIds.value = []
})

watch(currentPage, (val) => {
  jumpPageInput.value = val
})

const isAllSelected = computed(() => {
  if (paginatedParts.value.length === 0) return false
  return paginatedParts.value.every(item => selectedIds.value.includes(item.id))
})

const toggleSelectAll = (e) => {
  if (e.target.checked) {
    const currentIds = paginatedParts.value.map(i => i.id)
    selectedIds.value = Array.from(new Set([...selectedIds.value, ...currentIds]))
  } else {
    const currentIds = paginatedParts.value.map(i => i.id)
    selectedIds.value = selectedIds.value.filter(id => !currentIds.includes(id))
  }
}

const toggleSelect = (id) => {
  if (selectedIds.value.includes(id)) {
    selectedIds.value = selectedIds.value.filter(i => i !== id)
  } else {
    selectedIds.value.push(id)
  }
}

const openBatchDeleteModal = () => {
  if (selectedIds.value.length === 0) return
  batchDeleteModalVisible.value = true
}

const confirmBatchDelete = async () => {
  try {
    for (const id of selectedIds.value) {
      await apiFetch(`/api/parts/${id}`, { method: 'DELETE' })
    }
    batchDeleteModalVisible.value = false
    selectedIds.value = []
    showSuccessModal('' + t.value.common.success)
    emit('refresh-data')
  } catch (e) {
    batchDeleteModalVisible.value = false
    showSuccessModal('' + t.value.common.error)
  }
}

const openDetailDrawer = (item) => {
  editingPart.value = { 
    ...item, 
    cost_price: item.cost_price ?? 0,
    tax_rate: item.tax_rate ?? 0.16,
    bin_location: item.bin_location || '',
    cross_references: item.cross_references || '',
    image_url: item.image_url || ''
  }
  editFiles.value = []
  drawerMode.value = 'read'
  detailDrawerVisible.value = true
}

const switchToEdit = () => {
  drawerMode.value = 'edit'
}

const switchToRead = () => {
  const latest = props.partsList.find(p => p.id === editingPart.value.id)
  if (latest) {
    editingPart.value = {
      ...latest,
      cost_price: latest.cost_price ?? 0,
      tax_rate: latest.tax_rate ?? 0.16,
      bin_location: latest.bin_location || '',
      cross_references: latest.cross_references || '',
      image_url: latest.image_url || ''
    }
  }
  editFiles.value = []
  drawerMode.value = 'read'
}

const closeDrawer = () => {
  detailDrawerVisible.value = false
  editFiles.value = []
  drawerMode.value = 'read'
}

const onDeleteFromDrawer = () => {
  emit('delete-part', editingPart.value)
  closeDrawer()
}

const handleEditFileChange = (e) => {
  editFiles.value = Array.from(e.target.files).slice(0, 5)
}

const saveEditedPart = async () => {
  try {
    const formData = new FormData()
    formData.append('oem', editingPart.value.oem)
    formData.append('name', editingPart.value.name)
    formData.append('brand', editingPart.value.brand || 'GENERAL')
    formData.append('category', editingPart.value.category || tExt.value.uncategorized)
    formData.append('stock', editingPart.value.stock ?? 0)
    formData.append('price', editingPart.value.price ?? 0.0)
    formData.append('cost_price', editingPart.value.cost_price ?? 0.0)
    formData.append('tax_rate', editingPart.value.tax_rate ?? 0.16)
    formData.append('bin_location', editingPart.value.bin_location || '')
    formData.append('cross_references', editingPart.value.cross_references || '')

    editFiles.value.forEach(f => formData.append('files', f))

    const res = await apiFetch(`/api/parts/${editingPart.value.id}`, {
      method: 'PUT',
      body: formData
    })

    if (res.ok) {
      editFiles.value = []
      drawerMode.value = 'read'
      showSuccessModal('✨ ' + t.value.common.success)
      emit('refresh-data')
    } else {
      const err = await res.json()
      showSuccessModal(`${t.value.common.error}: ${err.detail || 'Unknown'}`)
    }
  } catch (e) {
    console.error(e)
    showSuccessModal('' + t.value.common.error)
  }
}

const handleKeydown = (e) => {
  if (!detailDrawerVisible.value && !batchDeleteModalVisible.value) return
  if (e.key === 'Escape') {
    if (detailDrawerVisible.value) {
      if (drawerMode.value === 'edit') {
        switchToRead()
      } else {
        closeDrawer()
      }
    }
    if (batchDeleteModalVisible.value) {
      batchDeleteModalVisible.value = false
    }
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>