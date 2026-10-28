<template>
  <div class="flex-1 overflow-y-auto p-2.5">
    <table data-testid="cart-table" class="w-full text-left border-collapse">
      <thead>
        <tr class="border-b-2 border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 text-xs font-extrabold uppercase bg-slate-100 dark:bg-slate-800/50">
          <th class="py-3 px-3">{{ tExt.cartOem }}</th>
          <th class="py-3 px-3">{{ tExt.cartName }}</th>
          <th class="py-3 px-3 text-right">{{ tExt.cartPrice }}</th>
          <th class="py-3 px-3 text-center">{{ tExt.cartQty }}</th>
          <th class="py-3 px-3 text-right">{{ tExt.cartSubtotal }}</th>
          <th class="py-3 px-3 text-center">{{ tExt.cartAction }}</th>
        </tr>
      </thead>
      <tbody class="text-sm font-medium">
        <tr 
          v-for="(item, index) in cartItems" 
          :key="item.oem" 
          @click="$emit('select-item', index)"
          :class="[
            selectedCartIndex === index ? 'bg-blue-50 dark:bg-blue-900/30 border-l-4 border-l-blue-500' : (index % 2 === 0 ? 'bg-white dark:bg-slate-800/80' : 'bg-slate-50 dark:bg-slate-900/70 border-l-4 border-l-transparent'),
            'border-b border-slate-200 dark:border-slate-700/70 hover:bg-blue-50/50 transition-all shadow-2xs cursor-pointer'
          ]"
        >
          <td class="py-3 px-3 font-mono font-black text-blue-600 text-sm">{{ item.oem }}</td>
          <td class="py-3 px-3 text-slate-900 dark:text-white font-bold">{{ item.name }}</td>
          <td class="py-3 px-3 text-right font-mono text-slate-700 dark:text-slate-300 font-bold">
            <div>${{ item.price.toFixed(2) }}</div>
            <div class="text-xs text-slate-400 font-normal">Bs. {{ (item.price * bcvRate).toFixed(2) }}</div>
          </td>
          <td class="py-3 px-3 text-center" @click.stop>
            <!-- 数量加减器 -->
            <div class="inline-flex items-center h-8 border border-slate-300 dark:border-slate-600 rounded-md overflow-hidden bg-white dark:bg-slate-800 shadow-sm focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-blue-500">
              <button @click="item.quantity > 1 ? (item.quantity--, $emit('update-qty', index, item.quantity)) : null" class="w-8 h-full flex items-center justify-center text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 hover:text-red-500 transition-colors font-bold text-lg select-none cursor-pointer">-</button>
              <input 
                v-model="itemInputQuantities[index]" 
                @focus="$event.target.select()"
                @blur="$emit('apply-qty', index)"
                @keydown.enter="$emit('apply-qty', index)"
                type="text" 
                class="w-10 h-full text-center bg-transparent text-slate-900 dark:text-white text-sm font-mono outline-none font-black border-x border-slate-200 dark:border-slate-700" 
              />
              <button @click="item.quantity++; itemInputQuantities[index] = item.quantity; $emit('update-qty', index, item.quantity)" class="w-8 h-full flex items-center justify-center text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 hover:text-emerald-500 transition-colors font-bold text-lg select-none cursor-pointer">+</button>
            </div>
          </td>
          <td class="py-3 px-3 text-right font-mono font-black text-emerald-600">
            <div>${{ (item.price * item.quantity).toFixed(2) }}</div>
            <div class="text-xs text-emerald-700/80 font-normal">Bs. {{ (item.price * item.quantity * bcvRate).toFixed(2) }}</div>
          </td>
          <td class="py-3 px-3 text-center" @click.stop>
            <button @click="$emit('remove-item', index)" class="text-rose-600 text-xs font-bold px-2.5 py-1 bg-rose-500/10 hover:bg-rose-500/20 rounded-lg transition-all cursor-pointer shadow-2xs">X</button>
          </td>
        </tr>
        <tr v-if="cartItems.length === 0">
          <td colspan="6" class="text-center py-20 text-slate-400 text-sm font-bold">
            <div class="flex flex-col items-center gap-2 text-slate-400">
              <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="opacity-20 mb-2"><circle cx="8" cy="21" r="1"/><circle cx="19" cy="21" r="1"/><path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"/></svg>
              {{ tExt.cartEmpty }}
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
defineProps({
  cartItems: { type: Array, required: true },
  itemInputQuantities: { type: Object, required: true },
  selectedCartIndex: { type: Number, required: true },
  bcvRate: { type: Number, required: true },
  tExt: { type: Object, required: true }
})

defineEmits(['select-item', 'update-qty', 'apply-qty', 'remove-item'])
</script>
