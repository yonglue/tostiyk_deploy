<template>
  <Transition name="fade">
    <div v-if="visible" class="fixed inset-0 z-[100] bg-black/50 backdrop-blur-sm flex flex-col justify-end" @click.self="close">
      <Transition name="slide-up" appear>
        <div class="bg-slate-50 dark:bg-slate-900 w-full rounded-t-3xl overflow-hidden pb-safe shadow-2xl">
          
          <!-- 顶部把手 -->
          <div class="flex justify-center pt-3 pb-2">
            <div class="w-10 h-1 rounded-full bg-slate-300 dark:bg-slate-700"></div>
          </div>

          <!-- 头部信息 -->
          <div class="px-5 pb-4 border-b border-slate-200/50 dark:border-slate-800/50 text-center">
            <h3 class="font-bold text-lg text-slate-800 dark:text-slate-100">{{ isZh ? '极速收款' : isEs ? 'Cobro rápido' : 'Quick Collection' }}</h3>
            <p class="text-xs text-slate-500 mt-1">{{ isZh ? '当前欠款:' : isEs ? 'Deuda actual:' : 'Current debt:' }}<span class="font-mono font-bold text-rose-500">$ {{ formatMoney(clientDebt) }}</span></p>
          </div>

          <!-- 输入区 -->
          <div class="p-5">
            <label class="block text-[11px] font-bold text-slate-400 uppercase mb-2">{{ isZh ? '收款金额 (USD)' : isEs ? 'Monto a cobrar (USD)' : 'Amount to Collect (USD)' }}</label>
            <div class="relative flex items-center bg-white dark:bg-slate-950 border-2 rounded-2xl px-4 py-3 transition-colors"
                 :class="isOverpay ? 'border-rose-500' : 'border-blue-500/30 focus-within:border-blue-500'">
              <span class="text-xl font-black text-slate-400 mr-2">$</span>
              <!-- 🌟 原生唤起数字键盘 -->
              <input 
                ref="inputRef"
                v-model.number="amount" 
                type="number" 
                inputmode="decimal"
                step="0.01"
                min="0"
                :max="clientDebt"
                class="w-full bg-transparent text-3xl font-black font-mono text-slate-800 dark:text-white outline-none placeholder:text-slate-300"
                placeholder="0.00"
              />
              <!-- 快捷全额按钮 -->
              <button @click="amount = clientDebt" class="text-xs font-bold text-accent bg-accent/10 dark:bg-blue-900/30 px-2 py-1 rounded-md shrink-0">{{ isZh ? '全额' : isEs ? 'Monto total' : 'Full amount' }}</button>
            </div>
            <p v-if="isOverpay" class="text-[11px] font-bold text-rose-500 mt-2 flex items-center gap-1">{{ isZh ? '收款金额不能大于当前欠款' : isEs ? 'El monto no puede exceder la deuda' : 'Amount cannot exceed debt' }}</p>
          </div>

          <!-- 操作按钮 -->
          <div class="p-5 pt-0 flex gap-3">
            <button @click="close" class="flex-1 py-3.5 bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-bold rounded-xl active:scale-[0.98] transition-transform">{{ isZh ? '取消' : isEs ? 'Cancelar' : 'Cancel' }}</button>
            <button 
              @click="submit"
              :disabled="!isValid || isSubmitting"
              class="flex-[2] py-3.5 bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-bold rounded-xl shadow-sm active:scale-[0.98] transition-all disabled:opacity-50 disabled:active:scale-100 flex items-center justify-center gap-2"
            >
              <span v-if="isSubmitting" class="w-4 h-4 rounded-full border-2 border-white/30 border-t-white animate-spin"></span>
              <span v-else>{{ isZh ? '确认收款' : isEs ? 'Confirmar cobro' : 'Confirm Collection' }}</span>
            </button>
          </div>

        </div>
      </Transition>
    </div>
  </Transition>
</template>

<script setup>
import { AlertTriangle } from 'lucide-vue-next';

import { useI18n } from '../composables/useI18n'

const { currentLang } = useI18n()

const isZh = computed(() => currentLang.value === 'zh')
const isEs = computed(() => currentLang.value === 'es')


import { ref, computed, watch, nextTick } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  clientDebt: { type: Number, default: 0 },
  isSubmitting: { type: Boolean, default: false }
})

const emit = defineEmits(['close', 'submit'])

const amount = ref(null)
const inputRef = ref(null)

// 监听弹窗打开，自动聚焦输入框，重置金额
watch(() => props.visible, (val) => {
  if (val) {
    amount.value = null
    nextTick(() => inputRef.value?.focus())
  }
})

// 校验：金额必须大于 0 且不能超过欠款
const isValid = computed(() => amount.value > 0 && amount.value <= props.clientDebt)
const isOverpay = computed(() => amount.value > props.clientDebt)

const formatMoney = (n) => Number(n || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

const close = () => {
  if (props.isSubmitting) return
  emit('close')
}

const submit = () => {
  if (!isValid.value || props.isSubmitting) return
  emit('submit', amount.value)
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.slide-up-enter-active, .slide-up-leave-active { transition: transform 0.3s cubic-bezier(0.25, 1, 0.5, 1); }
.slide-up-enter-from, .slide-up-leave-to { transform: translateY(100%); }
</style>
