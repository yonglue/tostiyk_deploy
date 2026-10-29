<!-- src/components/pos/PosShiftReportModal.vue -->
<script setup>
import { CreditCard, Zap, Lock, DollarSign } from 'lucide-vue-next';

import { computed, ref, watch } from 'vue'
import BaseModal from '../ui/BaseModal.vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  shiftStats: { type: Object, required: true },
  bcvRate: { type: Number, default: 1 },
  t: { type: Object, required: true },
  tExt: { type: Object, required: true }
})
const emit = defineEmits(['update:visible', 'submit'])

// 内部状态
const actualCounts = ref({ cardPos: 0, pagoMovil: 0, cashBs: 0, cashUsd: 0 })
const handoverNotes = ref('')

// 每次打开弹窗时，默认填入系统统计的预期值
watch(() => props.visible, (val) => {
  if (val && props.shiftStats) {
    actualCounts.value = {
      cardPos: Number((props.shiftStats.cardPos.amount * props.bcvRate).toFixed(2)),
      pagoMovil: Number((props.shiftStats.pagoMovil.amount * props.bcvRate).toFixed(2)),
      cashBs: Number((props.shiftStats.cashBs.amount * props.bcvRate).toFixed(2)),
      cashUsd: props.shiftStats.cashUsd.amount
    }
    handoverNotes.value = ''
  }
})

// 差异计算
const cardPosDiff = computed(() => Number(((actualCounts.value.cardPos || 0) - (props.shiftStats.cardPos.amount * props.bcvRate)).toFixed(2)))
const pagoMovilDiff = computed(() => Number(((actualCounts.value.pagoMovil || 0) - (props.shiftStats.pagoMovil.amount * props.bcvRate)).toFixed(2)))
const cashBsDiff = computed(() => Number(((actualCounts.value.cashBs || 0) - (props.shiftStats.cashBs.amount * props.bcvRate)).toFixed(2)))
const cashUsdDiff = computed(() => Number(((actualCounts.value.cashUsd || 0) - props.shiftStats.cashUsd.amount).toFixed(2)))
const totalUsdDiff = computed(() => {
  const rate = props.bcvRate || 1
  return Number(((cardPosDiff.value / rate) + (pagoMovilDiff.value / rate) + (cashBsDiff.value / rate) + cashUsdDiff.value).toFixed(2))
})

const submit = () => {
  emit('submit', { actualCounts: actualCounts.value, notes: handoverNotes.value })
}
</script>

<template>
  <BaseModal 
    :visible="visible" 
    :title="'📊 ' + tExt.shiftTitle" 
    size="xl"
    @update:visible="$emit('update:visible', $event)"
  >
    <div class="p-6 space-y-6 text-sm">
      <!-- 1. 系统统计 -->
      <div class="bg-surface-raised p-5 rounded-xl border border-line space-y-3 shadow-sm font-mono">
        <div class="text-xs font-black text-muted uppercase tracking-wider border-b border-line pb-2 flex justify-between">
          <span>{{ tExt.shiftSystemTitle }}</span>
          <span class="text-[10px] text-success">{{ tExt.shiftTodayOnly }}</span>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
          <div class="bg-surface p-3.5 rounded-lg border border-line">
            <span class="text-secondary block mb-1"><CreditCard :size="18" class="inline-block align-middle mr-1 text-slate-500" /> {{ t.pos.payCardPos }}:</span>
            <span class="font-black text-accent text-sm">Bs. {{ (shiftStats.cardPos.amount * bcvRate).toFixed(2) }}</span>
          </div>
          <div class="bg-surface p-3.5 rounded-lg border border-line">
            <span class="text-secondary block mb-1"><Zap :size="18" class="inline-block align-middle mr-1 text-slate-500" /> {{ t.pos.payPagoMovil }}:</span>
            <span class="font-black text-accent text-sm">Bs. {{ (shiftStats.pagoMovil.amount * bcvRate).toFixed(2) }}</span>
          </div>
          <div class="bg-surface p-3.5 rounded-lg border border-line">
            <span class="text-secondary block mb-1">🇻🇪 {{ t.pos.payCashBs }}:</span>
            <span class="font-black text-success text-sm">Bs. {{ (shiftStats.cashBs.amount * bcvRate).toFixed(2) }}</span>
          </div>
          <div class="bg-surface p-3.5 rounded-lg border border-line">
            <span class="text-secondary block mb-1"><DollarSign :size="18" class="inline-block align-middle mr-1 text-slate-500" /> {{ t.pos.payCashUsd }}:</span>
            <span class="font-black text-primary text-sm">${{ shiftStats.cashUsd.amount.toFixed(2) }}</span>
          </div>
        </div>
        <div class="pt-2 border-t border-line flex justify-between items-center text-sm font-black">
          <span class="text-primary">{{ tExt.shiftTotalRevenue }} (USD):</span>
          <span class="text-success text-lg">${{ shiftStats.totalUsd.toFixed(2) }}</span>
        </div>
      </div>

      <!-- 2. 实盘录入 -->
      <div class="bg-accent/10/50 dark:bg-blue-900/10 p-5 rounded-xl border border-blue-200/50 dark:border-blue-900/30 space-y-4 font-mono shadow-sm">
        <div class="text-xs font-black text-accent uppercase tracking-wider border-b border-blue-200/50 pb-2 flex justify-between items-center">
          <span>{{ tExt.shiftActualTitle }}</span>
          <span class="text-[11px] font-normal text-secondary">{{ tExt.shiftActualDesc }}</span>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="bg-surface p-4 rounded-xl border border-line space-y-2">
            <label class="block text-xs font-bold text-primary"><CreditCard :size="18" class="inline-block align-middle mr-1 text-slate-500" /> {{ t.pos.payCardPos }} (Bs.):</label>
            <div class="flex items-center gap-2">
              <span class="text-muted font-bold text-base">Bs.</span>
              <input v-model.number="actualCounts.cardPos" type="number" step="10" class="w-full bg-surface-raised border border-line rounded-lg px-3.5 py-2 text-right font-mono text-base outline-none focus:border-accent text-primary" />
            </div>
            <div class="text-xs text-right font-bold pt-1" :class="cardPosDiff >= 0 ? 'text-success' : 'text-danger'">{{ tExt.shiftDiff }}: {{ cardPosDiff >= 0 ? '+' : '' }}Bs. {{ cardPosDiff.toFixed(2) }}</div>
          </div>
          <div class="bg-surface p-4 rounded-xl border border-line space-y-2">
            <label class="block text-xs font-bold text-primary"><Zap :size="18" class="inline-block align-middle mr-1 text-slate-500" /> {{ t.pos.payPagoMovil }} (Bs.):</label>
            <div class="flex items-center gap-2">
              <span class="text-muted font-bold text-base">Bs.</span>
              <input v-model.number="actualCounts.pagoMovil" type="number" step="10" class="w-full bg-surface-raised border border-line rounded-lg px-3.5 py-2 text-right font-mono text-base outline-none focus:border-accent text-primary" />
            </div>
            <div class="text-xs text-right font-bold pt-1" :class="pagoMovilDiff >= 0 ? 'text-success' : 'text-danger'">{{ tExt.shiftDiff }}: {{ pagoMovilDiff >= 0 ? '+' : '' }}Bs. {{ pagoMovilDiff.toFixed(2) }}</div>
          </div>
          <div class="bg-surface p-4 rounded-xl border border-line space-y-2">
            <label class="block text-xs font-bold text-primary">🇻🇪 {{ t.pos.payCashBs }} (Bs.):</label>
            <div class="flex items-center gap-2">
              <span class="text-muted font-bold text-base">Bs.</span>
              <input v-model.number="actualCounts.cashBs" type="number" step="10" class="w-full bg-surface-raised border border-line rounded-lg px-3.5 py-2 text-right font-mono text-base outline-none focus:border-accent text-primary" />
            </div>
            <div class="text-xs text-right font-bold pt-1" :class="cashBsDiff >= 0 ? 'text-success' : 'text-danger'">{{ tExt.shiftDiff }}: {{ cashBsDiff >= 0 ? '+' : '' }}Bs. {{ cashBsDiff.toFixed(2) }}</div>
          </div>
          <div class="bg-surface p-4 rounded-xl border border-line space-y-2">
            <label class="block text-xs font-bold text-primary"><DollarSign :size="18" class="inline-block align-middle mr-1 text-slate-500" /> {{ t.pos.payCashUsd }} (USD):</label>
            <div class="flex items-center gap-2">
              <span class="text-muted font-bold text-base">$</span>
              <input v-model.number="actualCounts.cashUsd" type="number" step="0.5" class="w-full bg-surface-raised border border-line rounded-lg px-3.5 py-2 text-right font-mono text-base outline-none focus:border-accent text-primary" />
            </div>
            <div class="text-xs text-right font-bold pt-1" :class="cashUsdDiff >= 0 ? 'text-success' : 'text-danger'">{{ tExt.shiftDiff }}: {{ cashUsdDiff >= 0 ? '+' : '' }}${{ cashUsdDiff.toFixed(2) }}</div>
          </div>
        </div>
        <div class="pt-3 border-t border-blue-200/50 flex justify-between items-center text-sm">
          <span class="font-extrabold text-primary">{{ tExt.shiftTotalDiff }}:</span>
          <span :class="totalUsdDiff >= 0 ? 'text-success' : 'text-danger'" class="font-black font-mono text-lg">{{ totalUsdDiff >= 0 ? '+' : '' }}${{ totalUsdDiff.toFixed(2) }}</span>
        </div>
      </div>

      <div v-if="totalUsdDiff !== 0" class="space-y-2">
        <label class="block font-bold text-secondary uppercase text-xs">{{ tExt.shiftNotes }}</label>
        <input v-model="handoverNotes" type="text" :placeholder="tExt.shiftNotesPlace" class="w-full bg-surface-raised border border-line rounded-xl px-4 py-3 text-sm outline-none focus:border-accent font-bold text-primary shadow-sm" />
      </div>
    </div>
    
    <template #footer>
      <div class="flex items-center justify-between w-full">
        <button @click="$emit('update:visible', false)" class="px-6 py-2.5 bg-surface-muted hover:bg-line text-secondary rounded-xl text-xs font-bold transition-colors cursor-pointer">{{ t.common.cancel }}</button>
        <button @click="submit" class="px-7 py-3 bg-accent hover:bg-accent-hover text-white rounded-xl text-xs font-black shadow-lg shadow-accent/30 transition-all cursor-pointer"><Lock :size="18" class="inline-block align-middle mr-1 text-slate-500" /> {{ tExt.shiftConfirm }}</button>
      </div>
    </template>
  </BaseModal>
</template>