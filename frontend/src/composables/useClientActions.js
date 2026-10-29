import { ref } from 'vue'
import { apiFetch } from '../utils/api'
import { useNotifications } from './useNotifications'
import { useInventory } from './useInventory'
import { useI18n } from './useI18n'

// 接收一个回调函数
export function useClientActions(onRefresh) { 
  const { showSuccessModal } = useNotifications()
  const { fetchClients } = useInventory()
  const { t, currentLang } = useI18n()

  const clientDialogVisible = ref(false)
  const deleteClientModalVisible = ref(false)
  const targetClient = ref(null)
  
  const newClient = ref({ 
    name: '', 
    store_name: '', 
    phone: '', 
    address: '', 
    rif_or_cedula: '', 
    client_type: 'Regular', 
    notes: '',
    credit_limit: 500 // 🌟 确保有这个默认值
  })

  const getToastMsg = (key) => {
    const isZh = currentLang.value === 'zh'
    const isEs = currentLang.value === 'es'
    const msgs = {
      toastClientAdded: isZh ? '新客户档案创建成功！' : isEs ? '¡Cliente creado con éxito!' : 'Client created successfully!',
      toastClientDeleted: isZh ? '客户档案已成功删除！' : isEs ? '¡Cliente eliminado con éxito!' : 'Client deleted successfully!',
      toastErrorUnknown: isZh ? '未知错误' : isEs ? 'Error desconocido' : 'Unknown error',
      toastServerError: isZh ? '服务器连接异常！' : isEs ? '¡Error de conexión al servidor!' : 'Server connection error!'
    }
    return msgs[key] || key
  }

  const handleAddClient = async () => {
    if (!newClient.value.name?.trim()) {
      return showSuccessModal('❌ ' + (currentLang.value === 'zh' ? '请输入客户名称' : 'Ingrese nombre del cliente'))
    }
    
    try {
      const res = await apiFetch('/api/clients', {
        method: 'POST',
        body: JSON.stringify(newClient.value)
      })
      
      if (res.ok) {
        clientDialogVisible.value = false
        // 重置表单
        newClient.value = { name: '', store_name: '', phone: '', address: '', rif_or_cedula: '', client_type: 'Regular', notes: '', credit_limit: 500 }
        fetchClients()
        
        // 🌟 关键修复：通知 App.vue 刷新全局客户列表
        if (onRefresh) onRefresh() 
        
        showSuccessModal('✨ ' + getToastMsg('toastClientAdded'))
      } else {
        const err = await res.json().catch(() => ({}))
        const errorMsg = typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail || getToastMsg('toastErrorUnknown'))
        showSuccessModal(`❌ ${currentLang.value === 'zh' ? '新建失败' : 'Error'}: ${errorMsg}`) 
      }
    } catch (e) {
      console.error(e)
      showSuccessModal('❌ ' + getToastMsg('toastServerError'))
    }
  }

  const openDeleteClientModal = (c) => {
    targetClient.value = c
    deleteClientModalVisible.value = true
  }

  const confirmDeleteClient = async () => {
    if (!targetClient.value) return
    try {
      const res = await apiFetch(`/api/clients/${targetClient.value.id}`, { method: 'DELETE' })
      if (res.ok) {
        deleteClientModalVisible.value = false
        targetClient.value = null
        fetchClients()
        
        // 🌟 同样通知外层刷新
        if (onRefresh) onRefresh() 
        
        showSuccessModal('🗑️ ' + getToastMsg('toastClientDeleted'))
      } else {
        const err = await res.json()
        deleteClientModalVisible.value = false
        showSuccessModal(`❌ ${t.value.common.error}: ${err.detail || getToastMsg('toastErrorUnknown')}`)
      }
    } catch (e) {
      console.error(e)
      deleteClientModalVisible.value = false
      showSuccessModal('❌ ' + getToastMsg('toastServerError'))
    }
  }

  return {
    clientDialogVisible, deleteClientModalVisible, targetClient, newClient,
    handleAddClient, openDeleteClientModal, confirmDeleteClient
  }
}