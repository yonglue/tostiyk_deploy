<!-- src/components/pos/PosRecallModal.vue -->
<script setup>
import BaseModal from '../ui/BaseModal.vue'

defineProps({
  visible: { type: Boolean, default: false },
  heldOrders: { type: Array, default: () => [] },
  t: { type: Object, required: true },
  tExt: { type: Object, required: true }
})
defineEmits(['update:visible', 'recall', 'delete'])
</script>

<template>
  <BaseModal 
    :visible="visible" 
    :title="tExt.recallTitle + ' (' + heldOrders.length + ')'" 
    size="lg"
    @update:visible="$emit('update:visible', $event)"
  >
    <div class="p-5 space-y-3 flex flex-col min-h-[400px]">
      <div v-for="order in heldOrders" :key="order.id" class="p-4 rounded-xl border border-line bg-surface-raised hover:bg-surface-muted transition-all flex items-center justify-between shadow-sm">
        <div class="space-y-1">
          <div class="font-bold text-sm text-primary flex items-center gap-2">
            <span class="font-mono text-accent font-black">{{ order.hold_no }}</span>
            <span class="text-secondary">{{ order.client_name || 'Cliente General' }}</span>
          </div>
          <div class="text-xs text-muted font-mono">{{ tExt.recallTime }} {{ order.timestamp }}</div>
        </div>
        <div class="flex items-center gap-4">
          <span class="text-base font-mono font-black text-primary">${{ (order.total_amount || 0).toFixed(2) }}</span>
          <button @click="$emit('recall', order)" class="px-4 py-2 bg-accent hover:bg-accent-hover text-white rounded-lg text-xs font-bold transition-all cursor-pointer shadow-sm">{{ tExt.recallBtn }}</button>
          <button @click="$emit('delete', order.id)" class="px-3.5 py-2 bg-rose-50 hover:bg-rose-100 text-danger border border-rose-200 rounded-lg text-xs font-bold transition-all cursor-pointer">{{ tExt.recallVoid }}</button>
        </div>
      </div>
      
      <div v-if="heldOrders.length === 0" class="flex-1 flex flex-col items-center justify-center py-20 text-muted text-xs font-bold">
        <span class="text-4xl mb-2">📭</span>
        <span>{{ tExt.recallEmpty }}</span>
      </div>
    </div>
    
    <template #footer>
      <div class="flex items-center justify-between w-full">
        <span class="text-xs text-secondary font-mono font-bold">
          {{ tExt.recallFound }}: <strong class="text-primary">{{ heldOrders.length }}</strong>
        </span>
        <button @click="$emit('update:visible', false)" class="px-6 py-2 bg-surface-muted hover:bg-line text-secondary rounded-xl text-xs font-bold transition-colors cursor-pointer">
          {{ t.common.cancel }}
        </button>
      </div>
    </template>
  </BaseModal>
</template>