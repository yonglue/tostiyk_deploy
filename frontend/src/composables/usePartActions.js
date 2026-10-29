import { ref } from 'vue'
import { apiFetch } from '../utils/api'
import { useNotifications } from './useNotifications'
import { useInventory } from './useInventory'

export function usePartActions() {
  const { showSuccessModal } = useNotifications()
  const { fetchParts, fetchDashboardStats } = useInventory()

  const dialogVisible = ref(false)
  const deletePartModalVisible = ref(false)
  const targetPartForDelete = ref(null)
  const selectedFiles = ref([])
  
  const newPart = ref({ 
    oem: '', name: '', brand: '', category: '', 
    stock: 10, price: 15.00, cost_price: 10.00, 
    tax_rate: 0.16, bin_location: 'Estante A-1', cross_references: '' 
  })

  const handleFileChange = (e) => { 
    selectedFiles.value = Array.from(e.target.files).slice(0, 5) 
  }

  const handleAddPart = async (tExt, t) => {
    if (!newPart.value.oem || !newPart.value.name) {
      showSuccessModal('❌ 请填写商品编号和名称')
      return
    }
    
    const formData = new FormData()
    formData.append('oem', newPart.value.oem || '')
    formData.append('name', newPart.value.name || '')
    formData.append('brand', newPart.value.brand || 'GENERAL')
    formData.append('category', newPart.value.category || 'Uncategorized')
    formData.append('stock', newPart.value.stock ?? 0)
    formData.append('price', newPart.value.price ?? 0.0)
    formData.append('cost_price', newPart.value.cost_price ?? 0.0)
    formData.append('tax_rate', newPart.value.tax_rate ?? 0.16)
    formData.append('bin_location', newPart.value.bin_location || 'Estante A-1')
    formData.append('cross_references', newPart.value.cross_references || '')
    selectedFiles.value.forEach(f => formData.append('files', f))
    
    try {
      const res = await apiFetch('/api/parts', { method: 'POST', body: formData })
      if (res.ok) {
        dialogVisible.value = false
        newPart.value = { oem: '', name: '', brand: '', category: '', stock: 10, price: 15.00, cost_price: 10.00, tax_rate: 0.16, bin_location: 'Estante A-1', cross_references: '' }
        selectedFiles.value = []
        fetchParts()
        fetchDashboardStats()
        showSuccessModal('✨ 商品创建成功！')
      } else {
        // 🌟 防御性修复：直接从后端读取报错，不再依赖 t 变量，防止崩溃
        const err = await res.json().catch(() => ({}))
        const errorMsg = err.detail || '该商品编号已存在或数据不合法'
        showSuccessModal(`❌ 保存失败: ${typeof errorMsg === 'string' ? errorMsg : '数据格式错误'}`)
      }
    } catch (e) {
      console.error(e)
      showSuccessModal('❌ 网络异常或服务器连接失败')
    }
  }

  const openDeletePartModal = (part) => {
    targetPartForDelete.value = part
    deletePartModalVisible.value = true
  }

  const confirmDeletePart = async () => {
    if (!targetPartForDelete.value) return
    try {
      const res = await apiFetch(`/api/parts/${targetPartForDelete.value.id}`, { method: 'DELETE' })
      if (res.ok) {
        deletePartModalVisible.value = false
        targetPartForDelete.value = null
        fetchParts()
        fetchDashboardStats()
      }
    } catch (e) { console.error(e) }
  }

  return {
    dialogVisible, deletePartModalVisible, targetPartForDelete, newPart, selectedFiles,
    handleFileChange, handleAddPart, openDeletePartModal, confirmDeletePart
  }
}