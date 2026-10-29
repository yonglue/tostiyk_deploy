<!-- src/components/OfflineIndicator.vue -->
<!-- 顶栏离线队列指示器。不接管 POS 主流程，只做状态可视化 + 手动触发 flush。 -->
<template>
  <button
    type="button"
    :class="pillClass"
    :title="titleText"
    data-testid="offline-indicator"
    @click="onClick"
  >
    <component :is="iconEl" :size="14" :stroke-width="2.2" />
    <span v-if="label" class="text-xs font-bold">{{ label }}</span>
  </button>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from 'vue'
import { Wifi, WifiOff, RefreshCw } from 'lucide-vue-next'
import { useI18n } from '../composables/useI18n'
import { useOfflineQueue, enqueueToOffline } from '../composables/useOfflineQueue'
import { setOfflineEnqueue } from '../utils/api'

const { currentLang } = useI18n()
const isZh = computed(() => currentLang.value === 'zh')
const isEs = computed(() => currentLang.value === 'es')

const { isOnline, pendingCount, syncing, flush, init, destroy } = useOfflineQueue()

onMounted(() => {
  setOfflineEnqueue(enqueueToOffline)
  init()
})
onUnmounted(() => { destroy() })

const iconEl = computed(() => {
  if (syncing.value) return RefreshCw
  if (!isOnline.value) return WifiOff
  return Wifi
})

const pillClass = computed(() => {
  const base = 'flex items-center gap-1.5 h-8 px-2.5 rounded-lg text-xs font-bold transition-colors cursor-pointer select-none'
  if (syncing.value) return base + ' bg-accent/10 text-accent dark:bg-blue-900/30 dark:text-accent'
  if (!isOnline.value) return base + ' bg-rose-50 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400'
  if (pendingCount.value > 0) return base + ' bg-amber-50 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'
  return base + ' hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 dark:text-slate-400'
})

const label = computed(() => {
  if (syncing.value) return isZh.value ? '同步中' : isEs.value ? 'Sincronizando' : 'Syncing'
  if (!isOnline.value) {
    const n = pendingCount.value
    if (n > 0) return isZh.value ? `离线 ${n} 单` : isEs.value ? `Offline ${n}` : `Offline ${n}`
    return isZh.value ? '离线' : isEs.value ? 'Offline' : 'Offline'
  }
  if (pendingCount.value > 0) {
    return isZh.value ? `待同步 ${pendingCount.value}` : isEs.value ? `Pendiente ${pendingCount.value}` : `Pending ${pendingCount.value}`
  }
  return ''
})

const titleText = computed(() => {
  if (syncing.value) return isZh.value ? '正在同步离线队列' : 'Syncing offline queue'
  if (!isOnline.value) return isZh.value ? '网络断开，新订单将进入离线队列' : 'Offline: new orders will be queued'
  if (pendingCount.value > 0) return isZh.value ? `点击同步 ${pendingCount.value} 单` : `Click to sync ${pendingCount.value}`
  return isZh.value ? '已连接' : 'Online'
})

const onClick = async () => {
  if (!isOnline.value) return
  if (pendingCount.value > 0 && !syncing.value) {
    await flush()
  }
}
</script>
