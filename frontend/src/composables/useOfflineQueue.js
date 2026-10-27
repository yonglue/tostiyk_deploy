/**
 * 离线队列 composable。
 *
 * 4.3.1 阶段仅暴露 API，不自动挂载 online/offline 监听，不影响现有主流程。
 * 4.3.2 的 OfflineIndicator.vue 会在 onMounted 里调 init()，onUnmounted 里调 destroy()。
 */
import { ref } from 'vue'
import {
  putOrder, getAllOrders, deleteOrder, getOrderCount,
  putMeta, getMeta,
} from '../offline/db'
import { apiFetch } from '../utils/api'

function _newLocalId() {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID()
  }
  return `local-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`
}

export function useOfflineQueue() {
  const isOnline = ref(typeof navigator === 'undefined' ? true : navigator.onLine)
  const pendingCount = ref(0)
  const syncing = ref(false)
  const lastSyncAt = ref(null)
  const lastError = ref('')

  let _onlineHandler = null
  let _offlineHandler = null

  async function refreshCount() {
    try {
      pendingCount.value = await getOrderCount()
      const last = await getMeta('last_sync_at')
      if (last && !lastSyncAt.value) lastSyncAt.value = last
    } catch (e) {
      // 无 IndexedDB 环境（如极端权限）静默失败
    }
  }

  async function enqueue(payload) {
    const localId = payload.local_id || _newLocalId()
    const item = {
      ...payload,
      local_id: localId,
      // 幂等键：优先用调用方传入的，否则复用 local_id（保证同步时前后端一致）
      request_id: payload.request_id || localId,
      enqueued_at: payload.enqueued_at || new Date().toISOString(),
    }
    await putOrder(item)
    await refreshCount()
    return item
  }

  async function flush() {
    if (syncing.value) return { attempted: 0, synced: 0, failed: 0, aborted: true }
    syncing.value = true
    lastError.value = ''
    let attempted = 0, synced = 0, failed = 0, aborted = false
    try {
      const all = await getAllOrders()
      all.sort((a, b) => String(a.enqueued_at || '').localeCompare(String(b.enqueued_at || '')))
      for (const order of all) {
        attempted++
        try {
          const res = await apiFetch('/api/pos/orders', {
            method: 'POST',
            body: JSON.stringify(order),
          })
          if (res.ok) {
            await deleteOrder(order.local_id)
            synced++
          } else if (res.status >= 400 && res.status < 500) {
            // 4xx：业务校验失败，禁止重试（否则每次都 4xx），保留并中止本轮
            failed++
            aborted = true
            const err = await res.json().catch(() => ({}))
            lastError.value = err.detail || `HTTP ${res.status}`
            break
          } else {
            // 5xx：服务端临时错误，中止本轮，下轮重试
            failed++
            aborted = true
            lastError.value = `HTTP ${res.status}`
            break
          }
        } catch (e) {
          // 网络错误，中止本轮
          failed++
          aborted = true
          lastError.value = String(e)
          break
        }
      }
      if (synced > 0) {
        lastSyncAt.value = new Date().toISOString()
        try { await putMeta('last_sync_at', lastSyncAt.value) } catch (e) {}
      }
      return { attempted, synced, failed, aborted }
    } finally {
      syncing.value = false
      await refreshCount()
    }
  }

  function init() {
    refreshCount()
    if (typeof window !== 'undefined') {
      _onlineHandler = () => { isOnline.value = true; flush() }
      _offlineHandler = () => { isOnline.value = false }
      window.addEventListener('online', _onlineHandler)
      window.addEventListener('offline', _offlineHandler)
    }
  }

  function destroy() {
    if (typeof window !== 'undefined') {
      if (_onlineHandler) window.removeEventListener('online', _onlineHandler)
      if (_offlineHandler) window.removeEventListener('offline', _offlineHandler)
      _onlineHandler = null
      _offlineHandler = null
    }
  }

  return {
    isOnline, pendingCount, syncing, lastSyncAt, lastError,
    enqueue, flush, refreshCount, init, destroy,
  }
}
