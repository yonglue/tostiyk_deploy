<!-- src/components/pos/PosFooter.vue -->
<script setup>
defineProps({
  t: { type: Object, required: true }
})
defineEmits(['focus-search', 'open-client', 'hold-order', 'clear-cart', 'delete-last', 'confirm-exit'])
</script>

<template>
  <footer class="absolute bottom-0 left-0 right-0 h-11 bg-surface backdrop-blur-xl border-t border-line px-3 flex items-center justify-between z-30 shadow-md">
    <div class="grid grid-cols-6 gap-2 w-full">
      <div @click="$emit('focus-search')" class="bg-surface-raised hover:bg-accent/10 border border-line hover:border-accent/50 rounded-lg px-2.5 py-1.5 flex items-center justify-between text-xs cursor-pointer transition-all shadow-sm">
        <span class="text-primary font-bold">{{ t.pos.keyFocus }} [/]</span>
        <span class="bg-accent/15 text-accent font-mono font-bold px-1.5 py-0.5 rounded text-[10px]">F4~F7</span>
      </div>
      <div @click="$emit('open-client')" class="bg-surface-raised hover:bg-accent/10 border border-line hover:border-accent/50 rounded-lg px-2.5 py-1.5 flex items-center justify-between text-xs cursor-pointer transition-all shadow-sm">
        <span class="text-primary font-bold">{{ t.pos.keyClient }}</span>
        <span class="bg-accent/15 text-accent font-mono font-bold px-1.5 py-0.5 rounded text-[10px]">Ctrl+F</span>
      </div>
      <div @click="$emit('hold-order')" class="bg-surface-raised hover:bg-amber-500/10 border border-line hover:border-amber-300 rounded-lg px-2.5 py-1.5 flex items-center justify-between text-xs cursor-pointer transition-all shadow-sm">
        <span class="text-primary font-bold">{{ t.pos.keyHold }}</span>
        <span class="bg-amber-500/15 text-amber-600 font-mono font-bold px-1.5 py-0.5 rounded text-[10px]">Ctrl+H</span>
      </div>
      <div @click="$emit('clear-cart')" class="bg-surface-raised hover:bg-rose-500/10 border border-line hover:border-rose-300 rounded-lg px-2.5 py-1.5 flex items-center justify-between text-xs cursor-pointer transition-all shadow-sm">
        <span class="text-primary font-bold">{{ t.pos.keyClear }}</span>
        <span class="bg-rose-500/15 text-danger font-mono font-bold px-1.5 py-0.5 rounded text-[10px]">Ctrl+B</span>
      </div>
      <div @click="$emit('delete-last')" class="bg-surface-raised hover:bg-rose-500/10 border border-line hover:border-rose-300 rounded-lg px-2.5 py-1.5 flex items-center justify-between text-xs cursor-pointer transition-all shadow-sm">
        <span class="text-primary font-bold">{{ t.pos.keyDeleteLast }}</span>
        <span class="bg-rose-500/15 text-danger font-mono font-bold px-1.5 py-0.5 rounded text-[10px]">Delete</span>
      </div>
      <div @click="$emit('confirm-exit')" class="bg-surface-raised hover:bg-surface-muted border border-line rounded-lg px-2.5 py-1.5 flex items-center justify-between text-xs cursor-pointer transition-all shadow-sm">
        <span class="text-primary font-bold">{{ t.pos.keyBack }}</span>
        <span class="bg-surface-muted text-secondary font-mono font-bold px-1.5 py-0.5 rounded text-[10px]">Esc</span>
      </div>
    </div>
  </footer>
</template>