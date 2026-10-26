// src/composables/useSwipeBack.js
import { ref, computed, watch, onUnmounted } from 'vue'

export function useSwipeBack(onClose) {
  const panelRef = ref(null)
  const translateX = ref(0)
  const isDragging = ref(false)
  
  let startX = 0
  let startY = 0
  let isHorizontal = false

  // 动态样式：拖拽时禁用 transition（跟手），松手时恢复 transition（回弹/滑出）
  const style = computed(() => ({
    transform: `translateX(${translateX.value}px)`,
    transition: isDragging.value ? 'none' : 'transform 0.3s cubic-bezier(0.25, 1, 0.5, 1)',
    boxShadow: translateX.value > 0 ? '-10px 0 30px rgba(0,0,0,0.1)' : 'none'
  }))

  const handleTouchStart = (e) => {
    const t = e.touches[0]
    // 只有从左侧 50px 边缘开始滑动才激活
    if (t.clientX > 50) return
    startX = t.clientX
    startY = t.clientY
    isDragging.value = true
    isHorizontal = false
  }

  const handleTouchMove = (e) => {
    if (!isDragging.value) return
    const t = e.touches[0]
    const dx = t.clientX - startX
    const dy = t.clientY - startY

    // 如果用户是上下滚动，直接放弃手势
    if (!isHorizontal && Math.abs(dy) > Math.abs(dx)) {
      isDragging.value = false
      return
    }

    // 向右滑动时跟手
    if (dx > 0) {
      isHorizontal = true
      // 乘以 0.8 添加阻尼感，越往右越难拉，像橡皮筋一样
      translateX.value = dx * 0.8
      // 阻止浏览器默认的滚动行为
      if (e.cancelable) e.preventDefault()
    }
  }

  const handleTouchEnd = () => {
    if (!isDragging.value) return
    isDragging.value = false
    // 超过 100px 松手 → 判定为关闭
    if (translateX.value > 100) {
      translateX.value = window.innerWidth // 完全滑出屏幕
      onClose() // 通知父组件销毁
      setTimeout(() => { translateX.value = 0 }, 300)
    } else {
      // 否则回弹归零
      translateX.value = 0
    }
  }

  // 监听 DOM 挂载，自动绑/解绑事件
  watch(panelRef, (el) => {
    if (el) {
      el.addEventListener('touchstart', handleTouchStart, { passive: true })
      el.addEventListener('touchmove', handleTouchMove, { passive: false })
      el.addEventListener('touchend', handleTouchEnd, { passive: true })
    }
  })

  onUnmounted(() => {
    if (panelRef.value) {
      panelRef.value.removeEventListener('touchstart', handleTouchStart)
      panelRef.value.removeEventListener('touchmove', handleTouchMove)
      panelRef.value.removeEventListener('touchend', handleTouchEnd)
    }
  })

  return { panelRef, style }
}
