<!-- src/components/ConfirmDialog.vue -->
<script setup>
import { AlertTriangle } from 'lucide-vue-next';

import BaseModal from './ui/BaseModal.vue'

defineProps({
  visible: { type: Boolean, default: false },
  title: { type: String, default: 'Confirm' },
  message: { type: String, default: 'Are you sure?' },
  icon: { type: String, default: '<AlertTriangle :size="18" class="inline-block align-middle mr-1 text-slate-500" />' },
  cancelText: { type: String, default: 'Cancel' },
  confirmText: { type: String, default: 'Confirm' },
  // 保留原 API 以兼容旧调用，但在 BaseModal 中由统一 token 驱动，故忽略
  overlayClass: { type: String, default: '' }, 
  isDanger: { type: Boolean, default: true }
})
defineEmits(['cancel', 'confirm'])
</script>

<template>
  <BaseModal 
    :visible="visible" 
    :title="title" 
    size="sm" 
    :closable="false"
    @close="$emit('cancel')"
  >
    <div class="px-6 py-8 flex flex-col items-center text-center gap-4">
      <span v-if="icon" class="text-4xl">{{ icon }}</span>
      <p class="text-primary font-medium text-sm leading-relaxed whitespace-pre-wrap">{{ message }}</p>
    </div>
    
    <template #footer>
      <div class="flex justify-end gap-3 w-full">
        <button 
          @click="$emit('cancel')" 
          class="px-5 py-2.5 bg-surface-muted hover:bg-surface-raised text-secondary rounded-xl text-sm font-bold transition-colors cursor-pointer"
        >
          {{ cancelText }}
        </button>
        <button 
          @click="$emit('confirm')" 
          :class="[
            'px-5 py-2.5 text-white rounded-xl text-sm font-bold transition-colors cursor-pointer',
            isDanger ? 'bg-danger hover:bg-red-600' : 'bg-accent hover:bg-accent-hover'
          ]"
        >
          {{ confirmText }}
        </button>
      </div>
    </template>
  </BaseModal>
</template>