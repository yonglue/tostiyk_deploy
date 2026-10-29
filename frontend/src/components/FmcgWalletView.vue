<!-- src/components/FmcgWalletView.vue -->
<template>
  <div class="space-y-6 max-w-7xl mx-auto pb-24">
    <div class="flex flex-wrap items-center justify-between gap-4">
      <div>
        <h2 class="text-xl font-bold text-slate-800 dark:text-slate-200 flex items-center gap-2">
          <span>💰</span> {{ title }}
        </h2>
        <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">{{ subtitle }}</p>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-5 gap-6">
      <div class="lg:col-span-3 space-y-4">
        <div class="bg-white dark:bg-slate-800 p-4 md:p-6 rounded-2xl border border-slate-200/80 dark:border-slate-700 shadow-xs">
          <div class="flex flex-wrap items-end gap-3">
            <div class="flex-1 min-w-[200px]">
              <label class="block text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1">{{ phoneLabel }}</label>
              <input v-model="queryPhone" @keyup.enter="doQuery" type="text" :placeholder="phonePlaceholder"
                class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-sm rounded-xl px-4 py-2.5 outline-none focus:border-accent font-bold dark:text-white" />
            </div>
            <div class="w-40">
              <label class="block text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1">{{ currencyLabel }}</label>
              <select v-model="queryCurrency"
                class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-sm rounded-xl px-4 py-2.5 outline-none focus:border-accent font-bold dark:text-white">
                <option value="USD">USD</option>
                <option value="VES">VES</option>
                <option value="USDT">USDT</option>
              </select>
            </div>
            <button @click="doQuery" :disabled="queryLoading" data-testid="fmcg-wallet-search"
              class="px-5 py-2.5 rounded-xl bg-accent hover:bg-accent-hover disabled:opacity-50 text-white text-sm font-bold shadow-md shadow-blue-500/20 transition-all">
              {{ queryLoading ? loadingLabel : searchLabel }}
            </button>
          </div>
        </div>

        <div v-if="wallet" data-testid="fmcg-wallet-balance-card" class="bg-gradient-to-br from-blue-600 to-blue-700 text-white p-6 rounded-2xl shadow-lg">
          <div class="flex items-start justify-between">
            <div>
              <div class="text-[11px] font-bold uppercase tracking-wider text-blue-100">{{ balanceLabel }}</div>
              <div class="text-4xl font-bold font-mono mt-2">{{ wallet.balance }} <span class="text-lg opacity-70">{{ wallet.currency }}</span></div>
              <div class="text-xs text-blue-100 mt-2">{{ wallet.phone }}</div>
            </div>
            <div class="text-3xl">👛</div>
          </div>
        </div>

        <div v-else-if="queryDone" data-testid="fmcg-wallet-empty" class="bg-white dark:bg-slate-800 p-6 rounded-2xl border border-amber-200 dark:border-amber-800 text-amber-700 dark:text-amber-400 text-sm">
          {{ notFoundLabel }}
        </div>

        <div v-if="wallet && wallet.recent_ledger && wallet.recent_ledger.length > 0" class="bg-white dark:bg-slate-800 rounded-2xl border border-slate-200/80 dark:border-slate-700 shadow-xs overflow-hidden">
          <div class="px-6 py-4 border-b border-slate-100 dark:border-slate-700">
            <h3 class="text-sm font-bold text-slate-700 dark:text-slate-200">{{ ledgerLabel }}</h3>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse min-w-[600px]">
              <thead>
                <tr class="bg-slate-50 dark:bg-slate-900 border-b border-slate-100 dark:border-slate-700 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                  <th class="py-3 px-4">{{ timeLabel }}</th>
                  <th class="py-3 px-4">{{ typeLabel }}</th>
                  <th class="py-3 px-4 text-right">{{ amountLabel }}</th>
                  <th class="py-3 px-4 text-right">{{ afterLabel }}</th>
                  <th class="py-3 px-4">{{ refLabel }}</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100 dark:divide-slate-700">
                <tr v-for="row in wallet.recent_ledger" :key="row.id" class="text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-900/50">
                  <td class="py-3 px-4 text-xs font-mono">{{ formatTime(row.created_at) }}</td>
                  <td class="py-3 px-4">
                    <span :class="row.tx_type === 'credit' ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'" class="font-bold text-xs">
                      {{ row.tx_type === 'credit' ? 'IN' : 'OUT' }}
                    </span>
                  </td>
                  <td class="py-3 px-4 text-right font-mono font-bold" :class="row.tx_type === 'credit' ? 'text-emerald-600' : 'text-rose-600'">{{ row.amount }}</td>
                  <td class="py-3 px-4 text-right font-mono text-xs">{{ row.balance_after }}</td>
                  <td class="py-3 px-4 text-xs">{{ row.ref_type }}<span v-if="row.ref_id" class="opacity-60"> / {{ row.ref_id }}</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div class="lg:col-span-2">
        <div class="bg-white dark:bg-slate-800 p-6 rounded-2xl border border-slate-200/80 dark:border-slate-700 shadow-xs space-y-4">
          <h3 class="text-sm font-bold text-slate-700 dark:text-slate-200 flex items-center gap-2">
            <span>➕</span> {{ creditTitle }}
          </h3>
          <div class="space-y-3">
            <div>
              <label class="block text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1">{{ phoneLabel }}</label>
              <input v-model="form.phone" type="text" :placeholder="phonePlaceholder"
                class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-sm rounded-xl px-4 py-2.5 outline-none focus:border-accent font-bold dark:text-white" />
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1">{{ amountLabel }}</label>
                <input v-model="form.amount" type="number" step="0.0001" min="0.0001"
                  class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-sm rounded-xl px-4 py-2.5 outline-none focus:border-accent font-mono font-bold dark:text-white" />
              </div>
              <div>
                <label class="block text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1">{{ currencyLabel }}</label>
                <select v-model="form.currency"
                  class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-sm rounded-xl px-4 py-2.5 outline-none focus:border-accent font-bold dark:text-white">
                  <option value="USD">USD</option>
                  <option value="VES">VES</option>
                  <option value="USDT">USDT</option>
                </select>
              </div>
            </div>
            <div>
              <label class="block text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1">{{ refTypeLabel }}</label>
              <input v-model="form.ref_type" type="text" :placeholder="refTypePlaceholder"
                class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-sm rounded-xl px-4 py-2.5 outline-none focus:border-accent font-bold dark:text-white" />
            </div>
            <div>
              <label class="block text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1">{{ refIdLabel }}</label>
              <input v-model="form.ref_id" type="text" :placeholder="refIdPlaceholder"
                class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-sm rounded-xl px-4 py-2.5 outline-none focus:border-accent font-bold dark:text-white" />
            </div>
            <div>
              <label class="block text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-1">{{ noteLabel }}</label>
              <input v-model="form.note" type="text" :placeholder="notePlaceholder"
                class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-sm rounded-xl px-4 py-2.5 outline-none focus:border-accent font-bold dark:text-white" />
            </div>
            <button @click="doCredit" :disabled="creditLoading" data-testid="fmcg-wallet-credit"
              class="w-full px-5 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white text-sm font-bold shadow-md shadow-emerald-500/20 transition-all">
              {{ creditLoading ? loadingLabel : creditBtnLabel }}
            </button>
            <div v-if="creditResult" class="text-xs text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-900/30 rounded-lg p-3">
              ✓ {{ creditResult }}
            </div>
            <div v-if="creditError" class="text-xs text-rose-700 dark:text-rose-400 bg-rose-50 dark:bg-rose-900/30 rounded-lg p-3">
              {{ creditError }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useI18n } from '../composables/useI18n'
import { apiFetch } from '../utils/api'

const { currentLang } = useI18n()
const isZh = computed(() => currentLang.value === 'zh')
const isEs = computed(() => currentLang.value === 'es')

const title = computed(() => isZh.value ? '找零钱包' : isEs.value ? 'Monedero' : 'Change Wallet')
const subtitle = computed(() => isZh.value ? '客户零钱余额管理，下次消费可抵扣。' : isEs.value ? 'Gestión del saldo a favor del cliente.' : 'Customer change balance management.')
const phoneLabel = computed(() => isZh.value ? '手机号' : isEs.value ? 'Teléfono' : 'Phone')
const phonePlaceholder = computed(() => isZh.value ? '例如：0414-123-4567' : isEs.value ? 'Ej: 0414-123-4567' : 'e.g. 0414-123-4567')
const currencyLabel = computed(() => isZh.value ? '币种' : isEs.value ? 'Moneda' : 'Currency')
const searchLabel = computed(() => isZh.value ? '查询' : isEs.value ? 'Buscar' : 'Search')
const loadingLabel = computed(() => isZh.value ? '处理中...' : isEs.value ? 'Cargando...' : 'Loading...')
const balanceLabel = computed(() => isZh.value ? '当前余额' : isEs.value ? 'Saldo Actual' : 'Current Balance')
const notFoundLabel = computed(() => isZh.value ? '未找到该钱包。可在右侧入账一笔建立。' : isEs.value ? 'Wallet no encontrada. Crea una con un ingreso.' : 'Wallet not found. Create one with a credit.')
const ledgerLabel = computed(() => isZh.value ? '最近流水' : isEs.value ? 'Movimientos Recientes' : 'Recent Ledger')
const timeLabel = computed(() => isZh.value ? '时间' : isEs.value ? 'Hora' : 'Time')
const typeLabel = computed(() => isZh.value ? '类型' : isEs.value ? 'Tipo' : 'Type')
const amountLabel = computed(() => isZh.value ? '金额' : isEs.value ? 'Monto' : 'Amount')
const afterLabel = computed(() => isZh.value ? '结余' : isEs.value ? 'Saldo' : 'After')
const refLabel = computed(() => isZh.value ? '关联' : isEs.value ? 'Ref' : 'Ref')
const creditTitle = computed(() => isZh.value ? '手动入账' : isEs.value ? 'Ingreso Manual' : 'Manual Credit')
const refTypeLabel = computed(() => isZh.value ? '业务类型' : isEs.value ? 'Tipo Negocio' : 'Ref Type')
const refTypePlaceholder = computed(() => isZh.value ? '如 manual / change_short' : isEs.value ? 'ej manual / change_short' : 'e.g. manual / change_short')
const refIdLabel = computed(() => isZh.value ? '业务编号' : isEs.value ? 'ID Negocio' : 'Ref ID')
const refIdPlaceholder = computed(() => isZh.value ? '可空，用于幂等' : isEs.value ? 'Opcional, para idempotencia' : 'Optional, for idempotency')
const noteLabel = computed(() => isZh.value ? '备注' : isEs.value ? 'Nota' : 'Note')
const notePlaceholder = computed(() => isZh.value ? '可选' : isEs.value ? 'Opcional' : 'Optional')
const creditBtnLabel = computed(() => isZh.value ? '确认入账' : isEs.value ? 'Confirmar Ingreso' : 'Confirm Credit')

const queryPhone = ref('')
const queryCurrency = ref('USD')
const queryLoading = ref(false)
const queryDone = ref(false)
const wallet = ref(null)

const form = reactive({ phone: '', amount: '', currency: 'USD', ref_type: 'manual', ref_id: '', note: '' })
const creditLoading = ref(false)
const creditResult = ref('')
const creditError = ref('')

const formatTime = (iso) => {
  if (!iso) return '-'
  try {
    return new Date(iso).toLocaleString(isZh.value ? 'zh-CN' : isEs.value ? 'es-VE' : 'en-US', { hour12: false })
  } catch { return iso }
}

const doQuery = async () => {
  const phone = queryPhone.value.trim()
  if (!phone) { wallet.value = null; queryDone.value = false; return }
  queryLoading.value = true
  try {
    const res = await apiFetch(`/api/fmcg/wallets/${encodeURIComponent(phone)}?currency=${encodeURIComponent(queryCurrency.value)}`)
    if (res.ok) {
      wallet.value = await res.json()
      queryDone.value = true
    } else if (res.status === 404) {
      wallet.value = null
      queryDone.value = true
    } else {
      const err = await res.json().catch(() => ({}))
      creditError.value = err.detail || `HTTP ${res.status}`
      wallet.value = null
    }
  } catch (e) {
    creditError.value = String(e)
  } finally {
    queryLoading.value = false
  }
}

const doCredit = async () => {
  creditResult.value = ''
  creditError.value = ''
  const amount = String(form.amount || '').trim()
  if (!form.phone || !amount) {
    creditError.value = isZh.value ? '手机号和金额必填' : isEs.value ? 'Teléfono y monto requeridos' : 'Phone and amount required'
    return
  }
  creditLoading.value = true
  try {
    const res = await apiFetch('/api/fmcg/wallets/credit', {
      method: 'POST',
      body: JSON.stringify({
        phone: form.phone.trim(),
        currency: form.currency,
        amount,
        ref_type: form.ref_type || 'manual',
        ref_id: form.ref_id || null,
        note: form.note || null,
      }),
    })
    if (res.ok) {
      const body = await res.json()
      creditResult.value = `+${body.amount} -> ${body.balance_after} (${form.currency})`
      if (queryPhone.value.trim() === form.phone.trim() && queryCurrency.value === form.currency) {
        await doQuery()
      }
    } else {
      const err = await res.json().catch(() => ({}))
      creditError.value = err.detail || `HTTP ${res.status}`
    }
  } catch (e) {
    creditError.value = String(e)
  } finally {
    creditLoading.value = false
  }
}
</script>
