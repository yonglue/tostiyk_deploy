<!-- src/components/pos/PosPaymentPanel.vue -->
<script setup>
import { ref } from 'vue'
import { CreditCard, Banknote, Zap, RefreshCw, DollarSign } from 'lucide-vue-next';
import { fmtPrimary, fmtBsChannel, fmtUsdChannel } from '../../utils/pos/format'

const props = defineProps({
  cartItems: { type: Array, required: true },
  bcvRate: { type: Number, default: 1 },
  paymentSplit: { type: Object, required: true },
  primaryCurrency: { type: String, default: 'USD' },
  totalBaseUsd: { type: Number, required: true },
  totalTaxUsd: { type: Number, required: true },
  totalUsd: { type: Number, required: true },
  totalPaidUsd: { type: Number, required: true },
  balanceRemaining: { type: Number, required: true },
  isFullyPaid: { type: Boolean, required: true },
  isSubmitting: { type: Boolean, default: false },
  isProcessingCheckout: { type: Boolean, default: false },
  t: { type: Object, required: true },
  tExt: { type: Object, required: true },
  paymentReference: { type: String, default: '' }
})
const emit = defineEmits(['update:primaryCurrency', 'checkout', 'update:reference'])

// 暴露给父组件的 refs，用于 F4-F7 快捷键聚焦
const cardPosInputRef = ref(null)
const pagoMovilInputRef = ref(null)
const cashBsInputRef = ref(null)
const cashUsdInputRef = ref(null)
const referenceInputRef = ref(null)

defineExpose({
  cardPosInputRef, pagoMovilInputRef, cashBsInputRef, cashUsdInputRef, referenceInputRef
})

const toggleCurrency = () => {
  emit('update:primaryCurrency', props.primaryCurrency === 'USD' ? 'BS' : 'USD')
}
</script>

<template>
  <div class="w-[410px] flex flex-col bg-surface backdrop-blur-xl rounded-xl border border-line shadow-lg shrink-0 overflow-hidden transition-all">
    <div class="flex flex-col h-full w-full">
      <div class="flex-1 overflow-y-auto p-3.5 space-y-3">
        <div class="flex items-center justify-between border-b border-line pb-2">
          <h3 class="font-bold text-xs text-primary uppercase tracking-wider"><CreditCard :size="18" class="inline-block align-middle mr-1 text-slate-500" /> {{ t.pos.payPanelTitle }}</h3>
          <button 
            @click="toggleCurrency" 
            type="button"
            class="bg-accent/10 hover:bg-accent/20 text-accent border border-accent/20 px-2.5 py-1 rounded-lg text-xs font-bold font-mono transition-all cursor-pointer shadow-sm flex items-center gap-1"
          >
            <span><RefreshCw :size="18" class="inline-block align-middle mr-1 text-slate-500" /> {{ t.pos.mainCurrency }}: {{ primaryCurrency === 'USD' ? 'USD ($)' : 'Bs.' }}</span>
          </button>
        </div>

        <div class="space-y-2.5 text-sm">
          <!-- 1. Card POS [F4] -->
          <div @click="$emit('focus-channel', 'cardPos')" class="bg-surface-raised p-2.5 rounded-xl border border-line transition-all duration-200 flex items-center justify-between shadow-sm cursor-pointer hover:border-accent hover:shadow-md focus-within:ring-2 focus-within:ring-accent focus-within:border-accent">
            <div class="flex-1">
              <span class="font-bold text-primary flex items-center gap-1.5 text-[13px]"><CreditCard :size="16" class="text-muted shrink-0" /> {{ t.pos.payCardPos }} <span class="text-[10px] text-accent font-mono">[F4]</span></span>
              <span class="text-xs text-success font-mono font-bold block mt-0.5">{{ fmtBsChannel(paymentSplit.cardPos, bcvRate, primaryCurrency) }}</span>
            </div>
            <div class="flex items-center gap-1.5">
              <span class="text-muted font-bold text-xs">Bs.</span>
              <div class="w-32 bg-surface border border-line rounded-lg px-3 py-1.5 shadow-inner focus-within:ring-2 focus-within:ring-success">
                <input ref="cardPosInputRef" v-model.number="paymentSplit.cardPos" type="number" step="10" placeholder="0" class="w-full bg-transparent text-right font-mono font-black text-primary outline-none text-xl no-spinner" />
              </div>
            </div>
          </div>

          <!-- 2. Pago Móvil [F5] -->
          <div @click="$emit('focus-channel', 'pagoMovil')" class="bg-surface-raised p-2.5 rounded-xl border border-line transition-all duration-200 flex items-center justify-between shadow-sm cursor-pointer hover:border-accent hover:shadow-md focus-within:ring-2 focus-within:ring-accent focus-within:border-accent">
            <div class="flex-1">
              <span class="font-bold text-primary flex items-center gap-1.5 text-[13px]"><Zap :size="16" class="text-muted shrink-0" /> {{ t.pos.payPagoMovil }} <span class="text-[10px] text-accent font-mono">[F5]</span></span>
              <span class="text-xs text-success font-mono font-bold block mt-0.5">{{ fmtBsChannel(paymentSplit.pagoMovil, bcvRate, primaryCurrency) }}</span>
            </div>
            <div class="flex items-center gap-1.5">
              <span class="text-muted font-bold text-xs">Bs.</span>
              <div class="w-32 bg-surface border border-line rounded-lg px-3 py-1.5 shadow-inner focus-within:ring-2 focus-within:ring-success">
                <input ref="pagoMovilInputRef" v-model.number="paymentSplit.pagoMovil" type="number" step="10" placeholder="0" class="w-full bg-transparent text-right font-mono font-black text-primary outline-none text-xl no-spinner" />
              </div>
            </div>
          </div>

          <!-- 3. Efectivo Bs. [F6] -->
          <div @click="$emit('focus-channel', 'cashBs')" class="bg-surface-raised p-2.5 rounded-xl border border-line transition-all duration-200 flex items-center justify-between shadow-sm cursor-pointer hover:border-accent hover:shadow-md focus-within:ring-2 focus-within:ring-accent focus-within:border-accent">
            <div class="flex-1">
              <span class="font-bold text-primary flex items-center gap-1.5 text-[13px]"><Banknote :size="16" class="text-muted shrink-0" /> {{ t.pos.payCashBs }} <span class="text-[10px] text-accent font-mono">[F6]</span></span>
              <span class="text-xs text-success font-mono font-bold block mt-0.5">{{ fmtBsChannel(paymentSplit.cashBs, bcvRate, primaryCurrency) }}</span>
            </div>
            <div class="flex items-center gap-1.5">
              <span class="text-muted font-bold text-xs">Bs.</span>
              <div class="w-32 bg-surface border border-line rounded-lg px-3 py-1.5 shadow-inner focus-within:ring-2 focus-within:ring-success">
                <input ref="cashBsInputRef" v-model.number="paymentSplit.cashBs" type="number" step="10" placeholder="0" class="w-full bg-transparent text-right font-mono font-black text-primary outline-none text-xl no-spinner" />
              </div>
            </div>
          </div>

          <!-- 4. Cash USD [F7] -->
          <div @click="$emit('focus-channel', 'cashUsd')" class="bg-surface-raised p-2.5 rounded-xl border border-line transition-all duration-200 flex items-center justify-between shadow-sm cursor-pointer hover:border-accent hover:shadow-md focus-within:ring-2 focus-within:ring-accent focus-within:border-accent">
            <div class="flex-1">
              <span class="font-bold text-primary flex items-center gap-1.5 text-[13px]"><DollarSign :size="16" class="text-muted shrink-0" /> {{ t.pos.payCashUsd }} <span class="text-[10px] text-accent font-mono">[F7]</span></span>
              <span class="text-xs text-success font-mono font-bold block mt-0.5">{{ fmtUsdChannel(paymentSplit.cashUsd, bcvRate, primaryCurrency) }}</span>
            </div>
            <div class="flex items-center gap-1.5">
              <span class="text-muted font-bold text-xs">$</span>
              <div class="w-32 bg-surface border border-line rounded-lg px-3 py-1.5 shadow-inner focus-within:ring-2 focus-within:ring-success">
                <input ref="cashUsdInputRef" data-testid="pay-cash-usd" v-model.number="paymentSplit.cashUsd" type="number" step="0.5" placeholder="0" class="w-full bg-transparent text-right font-mono font-black text-primary outline-none text-xl no-spinner" />
              </div>
            </div>
          </div>
        </div>

        <!-- 回执号码 -->
        <div class="flex items-center gap-2 bg-surface-raised border border-line rounded-xl px-3 py-2 shadow-sm transition-all focus-within:ring-2 focus-within:ring-accent">
          <span class="w-1/3 text-xs font-black text-secondary shrink-0 truncate">{{ t.pos.refLabel }}:</span>
          <input ref="referenceInputRef" :value="paymentReference" @input="$emit('update:reference', $event.target.value)" type="text" :placeholder="t.pos.refPlaceholder" class="w-2/3 bg-transparent text-xs font-bold text-primary outline-none font-mono placeholder-muted" />
        </div>

        <!-- 底部应付、已付、找零汇总区 -->
        <div class="space-y-2.5 pt-2 border-t border-line">
          <div class="flex justify-between items-start text-sm font-bold text-secondary">
            <span class="font-bold pt-0.5">{{ t.pos.baseImponible }}:</span>
            <div class="text-right">
              <div class="font-mono text-primary font-extrabold text-sm">{{ fmtPrimary(totalBaseUsd, bcvRate, primaryCurrency) }}</div>
            </div>
          </div>

          <div class="flex justify-between items-start text-sm font-bold text-secondary">
            <span class="font-bold pt-0.5">{{ t.pos.ivaTax }}:</span>
            <div class="text-right">
              <div class="font-mono text-primary font-extrabold text-sm">{{ fmtPrimary(totalTaxUsd, bcvRate, primaryCurrency) }}</div>
            </div>
          </div>

          <div class="flex justify-between items-start text-sm font-bold">
            <span class="font-extrabold text-primary pt-0.5">{{ t.pos.totalPayable }}:</span>
            <div class="text-right">
              <div class="font-mono text-primary text-base font-black">{{ fmtPrimary(totalUsd, bcvRate, primaryCurrency) }}</div>
            </div>
          </div>

          <div class="flex justify-between items-start text-sm font-bold">
            <span class="font-extrabold text-primary pt-0.5">{{ t.pos.totalPaid }}:</span>
            <div class="text-right">
              <div class="font-mono text-success text-base font-black">{{ fmtPrimary(totalPaidUsd, bcvRate, primaryCurrency) }}</div>
            </div>
          </div>

          <div class="pt-2 border-t border-line flex justify-between items-start">
            <span class="text-base font-black pt-0.5" :class="balanceRemaining > 0 ? 'text-danger' : 'text-success'">
              {{ balanceRemaining > 0 ? '🔴 ' + t.pos.balanceDue + ':' : '🟢 ' + t.pos.changeDue + ':' }}
            </span>
            <div class="text-right">
              <div class="text-3xl font-black font-mono leading-tight" :class="balanceRemaining > 0 ? 'text-danger' : 'text-success'">
                {{ fmtPrimary(Math.abs(balanceRemaining), bcvRate, primaryCurrency) }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="p-3 bg-surface border-t border-line shrink-0">
        <button
          data-testid="pos-checkout-btn"  
          @click="$emit('checkout')"
          :disabled="!isFullyPaid || cartItems.length === 0 || isProcessingCheckout"
          class="w-full h-14 bg-success hover:bg-success/90 disabled:bg-surface-muted disabled:text-muted text-white rounded-lg font-black text-base shadow-lg shadow-success/20 transition-all cursor-pointer flex items-center justify-center active:scale-[0.98]"
        >
          <span>{{ isSubmitting ? '...' : t.pos.checkoutBtn || '结账' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>