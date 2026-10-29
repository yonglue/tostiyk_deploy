<template>
  <div 
    v-if="visible" 
    class="fixed inset-0 z-[100] bg-black flex flex-col" 
    :class="{ 'transition-transform duration-300 ease-out': !isDragging }"
    :style="{ transform: `translateX(${dragX}px)` }"
    @touchstart="handleTouchStart" 
    @touchmove="handleTouchMove" 
    @touchend="handleTouchEnd"
  >
    <!-- 顶部状态栏 -->
    <header class="absolute top-0 left-0 right-0 z-20 px-5 py-4 flex items-center justify-between pt-safe bg-gradient-to-b from-black/80 to-transparent">
      <button @click="closeScanner" class="p-2 rounded-full bg-white/10 text-white backdrop-blur-md">
        <X :size="24" />
      </button>
      <h2 class="font-bold text-sm text-white">
        {{ mode === 'continuous' ? '连续扫码入库' : '扫描配件条码' }}
      </h2>
      <button
        v-if="mode === 'continuous'"
        @click="cartOpen = true"
        class="relative p-2 rounded-full bg-white/10 text-white backdrop-blur-md"
      >
        <ShoppingCart :size="22" />
        <span v-if="totalQty > 0" class="absolute -top-1 -right-1 min-w-[20px] h-5 px-1 bg-accent rounded-full text-[10px] font-bold flex items-center justify-center">
          {{ totalQty }}
        </span>
      </button>
      <div v-else class="w-10"></div>
    </header>

    <!-- 摄像头画面 -->
    <div class="flex-1 relative flex flex-col items-center justify-center overflow-hidden bg-slate-900">
      <video v-show="!hasCameraError && isCameraReady" ref="videoRef" autoplay playsinline muted class="absolute inset-0 w-full h-full object-cover"></video>

      <div v-if="hasCameraError" class="absolute inset-0 flex flex-col items-center justify-center bg-slate-900 text-white p-6 text-center z-10">
        <div class="w-16 h-16 bg-rose-500/20 rounded-full flex items-center justify-center mb-4">
          <XCircle :size="32" class="text-rose-500" />
        </div>
        <h3 class="font-bold text-lg mb-2">无法开启摄像头</h3>
        <p class="text-xs text-slate-400 mb-6">当前环境不支持（如非 HTTPS 或权限被拒），请使用下方的手动输入。</p>
        <button @click="cameraInput?.click()" class="px-6 py-3 bg-accent rounded-xl font-bold text-sm">拍照扫码</button>
      </div>

      <div v-show="isCameraReady && !hasCameraError" class="absolute inset-0 pointer-events-none flex flex-col items-center justify-center">
        <div class="w-64 h-64 border border-white/20 rounded-3xl relative shadow-[0_0_0_9999px_rgba(0,0,0,0.7)] overflow-hidden">
          <div class="absolute -top-0.5 -left-0.5 w-8 h-8 border-t-4 border-l-4 border-blue-500 rounded-tl-3xl"></div>
          <div class="absolute -top-0.5 -right-0.5 w-8 h-8 border-t-4 border-r-4 border-blue-500 rounded-tr-3xl"></div>
          <div class="absolute -bottom-0.5 -left-0.5 w-8 h-8 border-b-4 border-l-4 border-blue-500 rounded-bl-3xl"></div>
          <div class="absolute -bottom-0.5 -right-0.5 w-8 h-8 border-b-4 border-r-4 border-blue-500 rounded-br-3xl"></div>
          <div class="absolute top-0 left-0 w-full h-1 bg-accent/100 shadow-[0_0_15px_3px_rgba(59,130,246,0.8)] animate-[scan_2.5s_ease-in-out_infinite]"></div>
        </div>
        <p class="text-white/60 text-xs mt-6 tracking-widest">将条码放入框内</p>
      </div>
    </div>

    <!-- 顶部 toast -->
    <Transition name="fade">
      <div v-if="toastMsg" class="absolute top-24 left-1/2 -translate-x-1/2 z-30 px-4 py-2 bg-emerald-600 text-white rounded-full text-xs font-bold shadow-lg whitespace-nowrap">
        {{ toastMsg }}
      </div>
    </Transition>

    <!-- 底部操作区 -->
    <footer class="absolute bottom-0 left-0 right-0 z-20 pb-safe bg-gradient-to-t from-black via-black/80 to-transparent pt-12 pb-8 flex justify-between px-16">
      <!-- 相册选择 (左下) -->
      <button @click="fileInput?.click()" class="flex flex-col items-center gap-2 text-white">
        <div class="w-12 h-12 rounded-full bg-slate-700/80 backdrop-blur border border-slate-600 shadow-lg flex items-center justify-center active:scale-95 transition-transform">
          <ImageIcon :size="20" />
        </div>
        <span class="text-[10px] opacity-80">相册</span>
      </button>

      <!-- 手电筒 (右下) -->
      <button v-if="hasTorch" @click="toggleTorch" class="flex flex-col items-center gap-2 text-white">
        <div :class="['w-12 h-12 rounded-full border shadow-lg flex items-center justify-center active:scale-95 transition-all', isTorchOn ? 'bg-amber-400 border-amber-300 text-slate-900 shadow-amber-500/50' : 'bg-slate-700/80 border-slate-600 backdrop-blur']">
          <Zap :size="20" :class="isTorchOn ? 'fill-current' : ''" />
        </div>
        <span class="text-[10px] opacity-80">手电筒</span>
      </button>
      
      <!-- 隐藏的 file input -->
      <input type="file" accept="image/*" class="hidden" ref="fileInput" @change="handleImageUpload" />
      <input type="file" accept="image/*" capture="environment" ref="cameraInput" @change="handleImageUpload" style="position:fixed;left:-9999px;top:-9999px;width:1px;height:1px;opacity:0;" />
    </footer>

    <canvas ref="canvasRef" class="hidden"></canvas>

    <!-- 结果面板（single 模式 / 多匹配时使用） -->
    <Transition name="slide-up">
      <div v-if="showResult" class="fixed inset-0 z-[110] bg-black/60 backdrop-blur-sm flex flex-col justify-end" @click.self="resetResult">
         <div class="bg-slate-50 dark:bg-slate-900 w-full rounded-t-3xl overflow-hidden pb-safe shadow-2xl p-5">
            <h3 v-if="selectedItem" class="font-bold text-lg text-center mb-4">已找到：{{ selectedItem.name }}</h3>
            <h3 v-else-if="matchedItems.length === 0" class="font-bold text-lg text-center mb-4">未找到匹配商品</h3>
            <h3 v-else class="font-bold text-lg text-center mb-4">匹配到多个商品，请选择</h3>

            <div v-if="mode === 'continuous' && matchedItems.length > 1" class="max-h-64 overflow-y-auto space-y-2 mb-4">
              <button v-for="p in matchedItems" :key="p.id" @click="pickItem(p)" class="w-full p-3 bg-white dark:bg-slate-800 rounded-xl text-left border border-slate-200 dark:border-slate-700 active:scale-[0.98] transition-transform">
                <p class="font-bold text-sm text-slate-800 dark:text-slate-100">{{ p.name }}</p>
                <p class="text-xs text-slate-400 font-mono">{{ p.oem }} · 库存 {{ p.stock }}</p>
              </button>
            </div>

            <button @click="resetResult" class="w-full py-3.5 bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-bold rounded-xl">继续扫码</button>
         </div>
      </div>
    </Transition>

    <!-- 提交成功全屏遮罩 -->
    <Transition name="fade">
      <div v-if="showSuccessOverlay" class="fixed inset-0 z-[200] bg-slate-900/90 backdrop-blur-md flex flex-col items-center justify-center">
        <div class="w-24 h-24 bg-emerald-500 rounded-full flex items-center justify-center mb-6 animate-bounce shadow-sm">
          <Check :size="48" class="text-white" />
        </div>
        <h2 class="text-2xl font-black text-white mb-2">入库成功</h2>
        <p class="text-emerald-400 font-bold">数据已安全同步</p>
      </div>
    </Transition>

    <!-- 购物车抽屉（连续模式专用） -->
    <Transition name="slide-up">
      <div v-if="cartOpen" class="fixed inset-0 z-[110] bg-black/60 backdrop-blur-sm flex flex-col justify-end" @click.self="cartOpen = false">
        <div class="bg-slate-50 dark:bg-slate-900 w-full rounded-t-3xl overflow-hidden pb-safe shadow-2xl max-h-[80vh] flex flex-col">
          <div class="p-5 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between shrink-0">
            <h3 class="font-bold text-lg text-slate-800 dark:text-slate-100">入库清单（{{ cartItems.length }} 项 / {{ totalQty }} 件）</h3>
            <button @click="cartOpen = false" class="p-1 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800">
              <X :size="20" class="text-slate-400" />
            </button>
          </div>

          <div class="flex-1 overflow-y-auto p-4 space-y-2">
            <div v-if="cartItems.length === 0" class="text-center py-12 text-slate-400 text-sm">
              还没有商品，继续扫码添加
            </div>
            <div v-for="(item, idx) in cartItems" :key="item.part.id" class="bg-white dark:bg-slate-800 rounded-xl p-3 border border-slate-200 dark:border-slate-700 flex items-center gap-2">
              <div class="flex-1 min-w-0">
                <p class="font-bold text-sm text-slate-800 dark:text-slate-100 truncate">{{ item.part.name }}</p>
                <p class="text-xs text-slate-400 font-mono truncate">{{ item.part.oem }}</p>
              </div>
              <div class="flex items-center gap-1 bg-slate-100 dark:bg-slate-900 rounded-lg p-0.5">
                <button @click="changeQty(idx, -1)" class="w-7 h-7 rounded-md bg-white dark:bg-slate-700 text-slate-700 dark:text-slate-200 font-bold">−</button>
                <input v-model.number="item.quantity" type="number" min="1" class="w-10 text-center text-sm font-bold bg-transparent outline-none dark:text-white" />
                <button @click="changeQty(idx, 1)" class="w-7 h-7 rounded-md bg-white dark:bg-slate-700 text-slate-700 dark:text-slate-200 font-bold">+</button>
              </div>
              <button @click="removeItem(idx)" class="p-2 rounded-lg text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-900/30">
                <Trash2 :size="16" />
              </button>
            </div>
          </div>

          <div class="p-4 border-t border-slate-200 dark:border-slate-800 flex gap-3 shrink-0">
            <button @click="clearCart" :disabled="cartItems.length === 0" class="px-4 py-3 bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-bold rounded-xl disabled:opacity-40">清空</button>
            <button @click="submitCart" :disabled="cartItems.length === 0 || isSubmitting" class="flex-1 py-3 bg-accent text-white font-bold rounded-xl disabled:opacity-40 active:scale-[0.98] transition-transform">
              {{ isSubmitting ? '提交中...' : `提交入库（${totalQty} 件）` }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted, watch, nextTick } from 'vue'
import { Check, ShoppingCart, Image as ImageIcon, XCircle, Camera, X, Trash2, Zap } from 'lucide-vue-next';
import jsQR from 'jsqr'
import { apiFetch } from '../utils/api'

const props = defineProps({
  visible: { type: Boolean, default: false },
  mode: { type: String, default: 'single' }, // 'single' | 'continuous'
})
const emit = defineEmits(['close', 'view-detail', 'submit'])

const videoRef = ref(null)
const canvasRef = ref(null)
const hasCameraError = ref(false)
const isCameraReady = ref(false)

let stream = null
let animationFrameId = null
const showResult = ref(false)
const lastScannedCode = ref('')
const matchedItems = ref([])
const selectedItem = ref(null)
const allParts = ref([])

// ─── 连续模式新增状态 ───
const cartItems = ref([])          // [{ part, quantity }]
const cartOpen = ref(false)
const toastMsg = ref('')
let toastTimer = null
let lastScanTime = 0               // 冷却时间戳，避免同帧重复识别

const totalQty = computed(() =>
  cartItems.value.reduce((sum, i) => sum + (Number(i.quantity) || 0), 0)
)

const showToast = (msg) => {
  toastMsg.value = msg
  if (toastTimer) clearTimeout(toastTimer)
  toastTimer = setTimeout(() => { toastMsg.value = '' }, 1500)
}

// ─── 原逻辑：预加载商品 ───
const preloadParts = async () => {
  if (allParts.value.length > 0) return
  try {
    const res = await apiFetch('/api/parts')
    if (res.ok) allParts.value = await res.json()
  } catch (e) {}
}

const startScanner = async () => {
  hasCameraError.value = false
  isCameraReady.value = false

  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    hasCameraError.value = true
    return
  }

  try {
    stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } }
    })

    await nextTick()
    if (videoRef.value) {
      videoRef.value.srcObject = stream
      videoRef.value.setAttribute('playsinline', 'true')
      videoRef.value.setAttribute('muted', 'true')
      await videoRef.value.play()

      isCameraReady.value = true
      
      // 探测是否支持手电筒
      const track = stream.getVideoTracks()[0]
      const caps = track.getCapabilities?.()
      if (caps && caps.torch) {
        hasTorch.value = true
      }
      
      await preloadParts()
      requestAnimationFrame(tick)
    }
  } catch (err) {
    console.warn('自动开启摄像头失败:', err)
    hasCameraError.value = true
  }
}

const tick = () => {
  if (!videoRef.value || !canvasRef.value || showResult.value || hasCameraError.value || !isCameraReady.value) {
    animationFrameId = requestAnimationFrame(tick)
    return
  }
  const video = videoRef.value
  const canvas = canvasRef.value
  if (video.readyState === video.HAVE_ENOUGH_DATA) {
    canvas.height = video.videoHeight
    canvas.width = video.videoWidth
    const ctx = canvas.getContext('2d', { willReadFrequently: true })
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
    const code = jsQR(imageData.data, imageData.width, imageData.height, { inversionAttempts: "dontInvert" })
    if (code && code.data) handleScanSuccess(code.data)
  }
  animationFrameId = requestAnimationFrame(tick)
}

// ─── 扫码成功：核心分流 ───
const handleScanSuccess = (code) => {
  if (!code) return

  // 连续模式：900ms 冷却，防止同一码被多帧重复识别
  const now = Date.now()
  if (props.mode === 'continuous' && now - lastScanTime < 900) return
  lastScanTime = now

  // 声音 + 震动（保持原样）
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)()
    const osc = ctx.createOscillator()
    const gain = ctx.createGain()
    osc.connect(gain)
    gain.connect(ctx.destination)
    osc.type = 'sine'
    osc.frequency.value = 1200
    gain.gain.setValueAtTime(0.1, ctx.currentTime)
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.1)
    osc.start()
    osc.stop(ctx.currentTime + 0.1)
  } catch (e) {}
  if (navigator.vibrate) navigator.vibrate(100)

  lastScannedCode.value = code
  const searchStr = code.toLowerCase()
  const matches = allParts.value.filter(p =>
    (p.oem && p.oem.toLowerCase().includes(searchStr)) ||
    (p.name && p.name.toLowerCase().includes(searchStr)) ||
    (p.cross_references && p.cross_references.toLowerCase().includes(searchStr))
  )
  matchedItems.value = matches

  if (props.mode === 'continuous') {
    if (matches.length === 1) {
      addToCart(matches[0])
      // 不弹结果面板，继续扫
    } else if (matches.length === 0) {
      showToast(`未找到: ${code}`)
    } else {
      // 多匹配：让用户选
      selectedItem.value = null
      showResult.value = true
    }
  } else {
    // single 模式：完全保持原行为
    selectedItem.value = matches.length === 1 ? matches[0] : null
    showResult.value = true
  }
}

// ─── 连续模式：购物车操作 ───
const addToCart = (part) => {
  const existing = cartItems.value.find(i => i.part.id === part.id)
  if (existing) {
    existing.quantity += 1
  } else {
    cartItems.value.push({ part, quantity: 1 })
  }
  showToast(`+1 ${part.name}`)
}

const pickItem = (p) => {
  addToCart(p)
  resetResult()
}

const changeQty = (idx, delta) => {
  const item = cartItems.value[idx]
  const next = (Number(item.quantity) || 0) + delta
  if (next < 1) return
  item.quantity = next
}

const removeItem = (idx) => cartItems.value.splice(idx, 1)
const clearCart = () => { cartItems.value = [] }

const isSubmitting = ref(false)
const showSuccessOverlay = ref(false)
const fileInput = ref(null)
const cameraInput = ref(null)

// 手势滑动返回 (原生 DOM 操作，锁定 60/120fps)
const modalRef = ref(null)
let isDragging = false
let touchStartX = 0
let touchStartY = 0

const handleTouchStart = (e) => {
  if (cartOpen.value || showResult.value || showSuccessOverlay.value) return
  touchStartX = e.touches[0].clientX
  touchStartY = e.touches[0].clientY
  isDragging = false
  
  if (modalRef.value) {
    // 滑动开始时，强制关闭 transition
    modalRef.value.style.transition = 'none'
  }
}

const handleTouchMove = (e) => {
  if (cartOpen.value || showResult.value || showSuccessOverlay.value) return
  if (!e.touches || !e.touches[0] || !modalRef.value) return
  
  const diffX = e.touches[0].clientX - touchStartX
  const diffY = Math.abs(e.touches[0].clientY - touchStartY)
  
  if (diffX > 10 && diffX > diffY) {
    isDragging = true
    // 直接操作原生 DOM，绕过 Vue 响应式，解决掉帧！
    modalRef.value.style.transform = `translateX(${diffX * 0.85}px)`
  }
}

const handleTouchEnd = (e) => {
  if (!isDragging || !modalRef.value) {
    return
  }
  
  isDragging = false
  const threshold = window.innerWidth * 0.3 
  // 获取当前手指离开时的 X 偏移
  const currentX = e.changedTouches[0].clientX - touchStartX
  
  // 加上过渡动画
  modalRef.value.style.transition = 'transform 0.3s cubic-bezier(0.25, 1, 0.5, 1)'
  
  if (currentX > threshold) {
    // 滑出屏幕
    modalRef.value.style.transform = `translateX(100vw)`
    setTimeout(() => {
      closeScanner()
    }, 300)
  } else {
    // 弹回原位
    modalRef.value.style.transform = 'translateX(0px)'
  }
}

// 手电筒控制
const isTorchOn = ref(false)
const hasTorch = ref(false)
const toggleTorch = async () => {
  if (!stream) return
  const track = stream.getVideoTracks()[0]
  try {
    isTorchOn.value = !isTorchOn.value
    await track.applyConstraints({ advanced: [{ torch: isTorchOn.value }] })
  } catch (err) {
    console.warn('手电筒切换失败', err)
    isTorchOn.value = false
  }
}

const submitCart = async () => {
  if (cartItems.value.length === 0 || isSubmitting.value) return
  
  isSubmitting.value = true
  
  const payload = cartItems.value.map(i => ({
    part_id: i.part.id,
    quantity: Number(i.quantity),
  }))

  try {
    const res = await apiFetch('/api/inventory/stock-in', {
      method: 'POST',
      body: JSON.stringify({ items: payload })
    })
    
    if (res.ok) {
      showSuccessOverlay.value = true
      cartOpen.value = false
      
      // 延迟 1 秒让用户看到成功反馈，再触发关闭和刷新
      setTimeout(() => {
        showSuccessOverlay.value = false
        emit('submit', cartItems.value.map(i => ({
          name: i.part.name,
          oem: i.part.oem,
          quantity: Number(i.quantity)
        })))
        cartItems.value = []
        emit('close')
      }, 1000)
    } else {
      const err = await res.json()
      alert(`入库失败: ${err.detail || '未知错误'}`)
    }
  } catch (e) {
    alert('网络异常，请重试')
  } finally {
    isSubmitting.value = false
  }
}

// ─── 手动输入 / 重置 / 关闭 ───
const handleImageUpload = (e) => {
  const file = e.target.files?.[0]
  if (!file) return
  
  const reader = new FileReader()
  reader.onload = (event) => {
    const img = new Image()
    img.onload = () => {
      if (!canvasRef.value) return
      canvasRef.value.width = img.width
      canvasRef.value.height = img.height
      const ctx = canvasRef.value.getContext('2d')
      ctx.drawImage(img, 0, 0)
      const imageData = ctx.getImageData(0, 0, img.width, img.height)
      const code = jsQR(imageData.data, imageData.width, imageData.height, { inversionAttempts: "attemptBoth" })
      
      if (code && code.data) {
        handleScanSuccess(code.data)
      } else {
        alert('未能识别图片中的条码，请确保图片清晰且包含完整条码')
      }
      // 重置 input 允许再次选择同一张图
      e.target.value = ''
    }
    img.src = event.target.result
  }
  reader.readAsDataURL(file)
}

const resetResult = () => {
  showResult.value = false
  matchedItems.value = []
  selectedItem.value = null
}

const closeScanner = async () => {
  resetResult()
  cartOpen.value = false
  isCameraReady.value = false
  hasCameraError.value = false
  if (animationFrameId) cancelAnimationFrame(animationFrameId)
  if (stream) {
    stream.getTracks().forEach(track => track.stop())
    stream = null
  }
  isTorchOn.value = false
  hasTorch.value = false
  emit('close')
}

watch(() => props.visible, (val) => {
  if (val) {
    // 每次打开清空队列，避免上次残留
    cartItems.value = []
    lastScanTime = 0
    startScanner()
  } else {
    closeScanner()
  }
})

onUnmounted(() => closeScanner())
</script>

<style>
@keyframes scan {
  0% { top: 0; }
  50% { top: 100%; }
  100% { top: 0; }
}
.slide-up-enter-active, .slide-leave-active { transition: transform 0.3s cubic-bezier(0.25, 1, 0.5, 1); }
.slide-up-enter-from, .slide-leave-to { transform: translateY(100%); }
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>