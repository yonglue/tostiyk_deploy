<template>
  <div v-if="visible" class="fixed inset-0 z-[999] bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 animate-in fade-in duration-200">
    <div class="bg-white dark:bg-slate-800 rounded-3xl shadow-2xl w-full max-w-sm overflow-hidden animate-in zoom-in-95 duration-200 border border-slate-200/80 dark:border-slate-700">
      <div class="p-6">
        <div class="w-14 h-14 bg-rose-100 dark:bg-rose-900/30 text-rose-600 dark:text-rose-400 rounded-full flex items-center justify-center mx-auto mb-4 animate-bounce">
          <svg xmlns="http://www.w3.org/2000/svg" class="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <h3 class="text-xl font-black text-center text-slate-800 dark:text-white mb-2">超出信用额度</h3>
        <p class="text-xs text-center text-slate-500 dark:text-slate-400 mb-6 leading-relaxed px-2">
          {{ errorMsg }}
        </p>
        
        <div class="relative mb-6">
          <input 
            v-model="pin" 
            type="password" 
            placeholder="请输入店长安全 PIN 码"
            class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3.5 text-center tracking-[0.3em] font-mono text-lg text-slate-800 dark:text-white outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all placeholder:tracking-normal placeholder:font-sans placeholder:text-sm placeholder:text-slate-400"
            @keyup.enter="confirm"
          />
        </div>
        
        <div class="flex gap-3">
          <button @click="close" class="flex-1 py-3 rounded-xl font-bold text-slate-600 bg-slate-100 hover:bg-slate-200 transition-colors cursor-pointer">取消</button>
          <button @click="confirm" class="flex-1 py-3 rounded-xl font-bold text-white bg-blue-600 hover:bg-blue-700 shadow-lg shadow-blue-500/30 transition-all active:scale-95 cursor-pointer">授权放行</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  visible: Boolean,
  errorMsg: String
})

const emit = defineEmits(['close', 'submit'])
const pin = ref('')

const close = () => {
  pin.value = ''
  emit('close')
}

const confirm = () => {
  if (!pin.value) return
  emit('submit', pin.value)
  pin.value = ''
}
</script>