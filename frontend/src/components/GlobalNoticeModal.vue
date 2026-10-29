<!-- src/components/GlobalNoticeModal.vue -->
<script setup>
import BaseModal from './ui/BaseModal.vue'

defineProps({
  visible: { type: Boolean, default: false },
  message: { type: String, default: '' },
  isErrorMessage: { type: Boolean, default: false }
})
defineEmits(['close'])
</script>

<template>
  <BaseModal 
    :visible="visible" 
    size="sm" 
    :closable="false"
    @close="$emit('close')"
  >
    <div class="px-6 py-10 flex flex-col items-center text-center gap-5">
      <div 
        :class="[
          'w-16 h-16 rounded-2xl flex items-center justify-center text-3xl',
          isErrorMessage ? 'bg-rose-50 dark:bg-rose-900/30 text-rose-500' : 'bg-accent/10 dark:bg-blue-900/30 text-blue-500'
        ]"
      >
        <span v-if="isErrorMessage">✕</span>
        <span v-else>✓</span>
      </div>
      <div>
        <h3 
          class="font-extrabold text-lg mb-2"
          :class="isErrorMessage ? 'text-rose-500' : 'text-primary'"
        >
          {{ isErrorMessage ? '操作拦截 / 提示' : '操作成功' }}
        </h3>
        <p class="text-secondary text-sm leading-relaxed whitespace-pre-wrap">{{ message }}</p>
      </div>
    </div>
    
    <template #footer>
      <div class="flex justify-center w-full pb-2">
        <button 
          @click="$emit('close')" 
          :class="[
            'w-full py-3 rounded-xl text-sm font-bold text-white transition-colors cursor-pointer',
            isErrorMessage ? 'bg-danger hover:bg-red-600' : 'bg-accent hover:bg-accent-hover'
          ]"
        >
          确定
        </button>
      </div>
    </template>
  </BaseModal>
</template>