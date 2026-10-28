<template>
  <div class="flex flex-col h-full bg-white dark:bg-slate-900 rounded-xl shadow-sm border border-slate-200 dark:border-slate-800 overflow-hidden shrink-0">
    <!-- 头部：切换主货币 -->
    <div class="p-3 border-b border-slate-200 dark:border-slate-800 flex justify-between items-center bg-slate-50 dark:bg-slate-800/50">
      <h3 class="font-black text-sm text-slate-800 dark:text-slate-200 flex items-center gap-2">
        {{ isZh ? '多通道组合支付' : isEs ? 'Pago Combinado' : 'Split Payment' }}
      </h3>
      <button
        @click="$emit('toggle-currency')"
        class="px-3 py-1 rounded border border-slate-300 dark:border-slate-600 hover:bg-white dark:hover:bg-slate-700 text-xs font-bold transition-colors cursor-pointer text-slate-700 dark:text-slate-300"
      >
        {{ t.pos.mainCurrency }}: {{ primaryCurrency === 'USD' ? 'USD ($)' : 'Bs.' }}
      </button>
    </div>

    <div class="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
      <!-- 1. Card POS [F4] -->
      <div @click="$emit('focus-channel', 'cardPos')" class="bg-white dark:bg-slate-800/90 p-2.5 rounded-xl border border-slate-200 dark:border-slate-700/80 transition-all duration-200 flex items-center justify-between shadow-2xs cursor-pointer hover:border-blue-300 hover:shadow-md focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-blue-500 focus-within:shadow-md">
        <div class="flex-1">
          <span class="font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5 text-[13px]"><CreditCard :size="16" class="text-slate-400 dark:text-slate-500 shrink-0" /> {{ t.pos.payCardPos }} <span class="text-[10px] text-blue-600 font-mono">[F4]</span></span>
          <span class="text-xs text-emerald-600 font-mono font-bold block mt-0.5">{{ primaryCurrency === 'USD' ? `≈ $${((Number(paymentSplit.cardPos) || 0) / (bcvRate || 1)).toFixed(2)}` : `Bs. ${(Number(paymentSplit.cardPos) || 0).toFixed(2)}` }}</span>
        </div>
        <div class="flex items-center gap-1.5">
          <span class="text-slate-400 font-bold text-xs">Bs.</span>
          <div class="w-32 bg-slate-100 dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg px-3 py-1.5 shadow-inner focus-within:ring-2 focus-within:ring-emerald-500 focus-within:border-emerald-500 transition-all">
            <input ref="cardPosInputRef" v-model.number="paymentSplit.cardPos" type="number" step="10" placeholder="0" class="w-full bg-transparent text-right font-mono font-black text-slate-900 dark:text-white outline-none text-xl no-spinner" />
          </div>
        </div>
      </div>

      <!-- 2. Pago Móvil [F5] -->
      <div @click="$emit('focus-channel', 'pagoMovil')" class="bg-white dark:bg-slate-800/90 p-2.5 rounded-xl border border-slate-200 dark:border-slate-700/80 transition-all duration-200 flex items-center justify-between shadow-2xs cursor-pointer hover:border-blue-300 hover:shadow-md focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-blue-500 focus-within:shadow-md">
        <div class="flex-1">
          <span class="font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5 text-[13px]"><Zap :size="16" class="text-slate-400 dark:text-slate-500 shrink-0" /> {{ t.pos.payPagoMovil }} <span class="text-[10px] text-blue-600 font-mono">[F5]</span></span>
          <span class="text-xs text-emerald-600 font-mono font-bold block mt-0.5">{{ primaryCurrency === 'USD' ? `≈ $${((Number(paymentSplit.pagoMovil) || 0) / (bcvRate || 1)).toFixed(2)}` : `Bs. ${(Number(paymentSplit.pagoMovil) || 0).toFixed(2)}` }}</span>
        </div>
        <div class="flex items-center gap-1.5">
          <span class="text-slate-400 font-bold text-xs">Bs.</span>
          <div class="w-32 bg-slate-100 dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg px-3 py-1.5 shadow-inner focus-within:ring-2 focus-within:ring-emerald-500 focus-within:border-emerald-500 transition-all">
            <input ref="pagoMovilInputRef" v-model.number="paymentSplit.pagoMovil" type="number" step="10" placeholder="0" class="w-full bg-transparent text-right font-mono font-black text-slate-900 dark:text-white outline-none text-xl no-spinner" />
          </div>
        </div>
      </div>

      <!-- 3. Efectivo Bs. [F6] -->
      <div @click="$emit('focus-channel', 'cashBs')" class="bg-white dark:bg-slate-800/90 p-2.5 rounded-xl border border-slate-200 dark:border-slate-700/80 transition-all duration-200 flex items-center justify-between shadow-2xs cursor-pointer hover:border-blue-300 hover:shadow-md focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-blue-500 focus-within:shadow-md">
        <div class="flex-1">
          <span class="font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5 text-[13px]"><Banknote :size="16" class="text-slate-400 dark:text-slate-500 shrink-0" /> {{ t.pos.payCashBs }} <span class="text-[10px] text-blue-600 font-mono">[F6]</span></span>
          <span class="text-xs text-emerald-600 font-mono font-bold block mt-0.5">{{ primaryCurrency === 'USD' ? `≈ $${((Number(paymentSplit.cashBs) || 0) / (bcvRate || 1)).toFixed(2)}` : `Bs. ${(Number(paymentSplit.cashBs) || 0).toFixed(2)}` }}</span>
        </div>
        <div class="flex items-center gap-1.5">
          <span class="text-slate-400 font-bold text-xs">Bs.</span>
          <div class="w-32 bg-slate-100 dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg px-3 py-1.5 shadow-inner focus-within:ring-2 focus-within:ring-emerald-500 focus-within:border-emerald-500 transition-all">
            <input ref="cashBsInputRef" v-model.number="paymentSplit.cashBs" type="number" step="10" placeholder="0" class="w-full bg-transparent text-right font-mono font-black text-slate-900 dark:text-white outline-none text-xl no-spinner" />
          </div>
        </div>
      </div>

      <!-- 4. Cash USD [F7] -->
      <div @click="$emit('focus-channel', 'cashUsd')" class="bg-white dark:bg-slate-800/90 p-2.5 rounded-xl border border-slate-200 dark:border-slate-700/80 transition-all duration-200 flex items-center justify-between shadow-2xs cursor-pointer hover:border-blue-300 hover:shadow-md focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-blue-500 focus-within:shadow-md">
        <div class="flex-1">
          <span class="font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5 text-[13px]"><DollarSign :size="16" class="text-slate-400 dark:text-slate-500 shrink-0" /> {{ t.pos.payCashUsd }} <span class="text-[10px] text-blue-600 font-mono">[F7]</span></span>
          <span class="text-xs text-emerald-600 font-mono font-bold block mt-0.5">{{ primaryCurrency === 'USD' ? `≈ Bs. ${((Number(paymentSplit.cashUsd) || 0) * bcvRate).toFixed(2)}` : `≈ $${(Number(paymentSplit.cashUsd) || 0).toFixed(2)}` }}</span>
        </div>
        <div class="flex items-center gap-1.5">
          <span class="text-slate-400 font-bold text-xs">$</span>
          <div class="w-32 bg-slate-100 dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-lg px-3 py-1.5 shadow-inner focus-within:ring-2 focus-within:ring-emerald-500 focus-within:border-emerald-500 transition-all">
            <input data-testid="pay-cash-usd" ref="cashUsdInputRef" v-model.number="paymentSplit.cashUsd" type="number" step="0.5" placeholder="0" class="w-full bg-transparent text-right font-mono font-black text-slate-900 dark:text-white outline-none text-xl no-spinner" />
          </div>
        </div>
      </div>

      <!-- 回执号码 -->
      <div class="flex items-center gap-2 bg-white dark:bg-slate-800/90 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 shadow-2xs transition-all focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-blue-500 mt-2">
        <span class="w-1/3 text-xs font-black text-slate-600 dark:text-slate-400 shrink-0 truncate">{{ t.pos.refLabel }}:</span>
        <input ref="referenceInputRef" v-model="paymentReference" type="text" :placeholder="t.pos.refPlaceholder" class="w-2/3 bg-transparent text-xs font-bold text-slate-900 dark:text-white outline-none font-mono placeholder-slate-400" />
      </div>

      <!-- 底部应付、已付、找零汇总区 -->
      <div class="space-y-2.5 pt-3 mt-2 border-t border-slate-200 dark:border-slate-700/60">
        <div class="flex justify-between items-start text-sm font-bold text-slate-600 dark:text-slate-400">
          <span class="font-bold pt-0.5">{{ t.pos.baseImponible }}:</span>
          <div class="text-right">
            <div class="font-mono text-slate-800 dark:text-slate-200 font-extrabold text-sm">{{ primaryCurrency === 'USD' ? `$${totalBaseUsd.toFixed(2)}` : `Bs. ${(totalBaseUsd * bcvRate).toFixed(2)}` }}</div>
          </div>
        </div>

        <div class="flex justify-between items-start text-sm font-bold text-slate-600 dark:text-slate-400">
          <span class="font-bold pt-0.5">{{ t.pos.ivaTax }}:</span>
          <div class="text-right">
            <div class="font-mono text-slate-800 dark:text-slate-200 font-extrabold text-sm">{{ primaryCurrency === 'USD' ? `$${totalTaxUsd.toFixed(2)}` : `Bs. ${(totalTaxUsd * bcvRate).toFixed(2)}` }}</div>
          </div>
        </div>

        <div class="flex justify-between items-start text-sm font-bold text-slate-700 dark:text-slate-300">
          <span class="font-extrabold text-slate-800 dark:text-slate-200 pt-0.5">{{ t.pos.totalPayable }}:</span>
          <div class="text-right">
            <div class="font-mono text-slate-900 dark:text-white text-base font-black">{{ primaryCurrency === 'USD' ? `$${totalUsd.toFixed(2)}` : `Bs. ${(totalUsd * bcvRate).toFixed(2)}` }}</div>
          </div>
        </div>

        <div class="flex justify-between items-start text-sm font-bold text-slate-700 dark:text-slate-300">
          <span class="font-extrabold text-slate-800 dark:text-slate-200 pt-0.5">{{ t.pos.totalPaid }}:</span>
          <div class="text-right">
            <div class="font-mono text-emerald-600 text-base font-black">{{ primaryCurrency === 'USD' ? `$${totalPaidUsd.toFixed(2)}` : `Bs. ${(totalPaidUsd * bcvRate).toFixed(2)}` }}</div>
          </div>
        </div>

        <div :class="balanceRemaining > 0 ? 'bg-rose-50 border-rose-200 dark:bg-rose-900/20 dark:border-rose-800' : 'bg-emerald-50 border-emerald-200 dark:bg-emerald-900/20 dark:border-emerald-800'" class="mt-3 p-3.5 rounded-xl border shadow-sm flex justify-between items-center transition-colors duration-300">
          <span class="text-sm font-black uppercase tracking-wider" :class="balanceRemaining > 0 ? 'text-rose-700 dark:text-rose-400' : 'text-emerald-700 dark:text-emerald-400'">
            {{ balanceRemaining > 0 ? t.pos.balanceDue : t.pos.changeDue }}
          </span>
          <div class="text-right">
            <div class="text-3xl font-black font-mono leading-none tracking-tight" :class="balanceRemaining > 0 ? 'text-rose-600 dark:text-rose-400' : 'text-emerald-600 dark:text-emerald-400'">
              {{ primaryCurrency === 'USD' ? `$${Math.abs(balanceRemaining).toFixed(2)}` : `Bs. ${(Math.abs(balanceRemaining) * bcvRate).toFixed(2)}` }}
            </div>
            <div v-if="primaryCurrency !== 'USD'" class="text-xs font-bold font-mono text-slate-500 mt-1">
              ≈ ${{ Math.abs(balanceRemaining).toFixed(2) }}
            </div>
            <div v-else class="text-xs font-bold font-mono text-slate-500 mt-1">
              ≈ Bs. {{ (Math.abs(balanceRemaining) * bcvRate).toFixed(2) }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, defineModel } from 'vue'
import { CreditCard, Zap, Banknote, DollarSign } from 'lucide-vue-next'

const paymentSplit = defineModel('paymentSplit', { type: Object, required: true })
const paymentReference = defineModel('paymentReference', { type: String, required: true })
const primaryCurrency = defineModel('primaryCurrency', { type: String, required: true })

const props = defineProps({
  bcvRate: { type: Number, required: true },
  totalBaseUsd: { type: Number, required: true },
  totalTaxUsd: { type: Number, required: true },
  totalUsd: { type: Number, required: true },
  totalPaidUsd: { type: Number, required: true },
  balanceRemaining: { type: Number, required: true },
  isZh: { type: Boolean, required: true },
  isEs: { type: Boolean, required: true },
  t: { type: Object, required: true }
})

defineEmits(['toggle-currency', 'focus-channel'])

// 暴露内部的 input refs 给父组件，确保 F4-F7 快捷键依然有效
const cardPosInputRef = ref(null)
const pagoMovilInputRef = ref(null)
const cashBsInputRef = ref(null)
const cashUsdInputRef = ref(null)
const referenceInputRef = ref(null)

defineExpose({
  cardPosInputRef,
  pagoMovilInputRef,
  cashBsInputRef,
  cashUsdInputRef,
  referenceInputRef
})
</script>
