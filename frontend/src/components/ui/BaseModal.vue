<!-- src/components/ui/BaseModal.vue -->
<script setup>
import {
  DialogRoot, DialogPortal, DialogOverlay, DialogContent,
  DialogTitle, DialogDescription, DialogClose,
} from 'reka-ui'
import { computed } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  title: { type: String, default: '' },
  size: { type: String, default: 'md' },          // sm | md | lg | xl
  closable: { type: Boolean, default: true },
})
const emit = defineEmits(['update:visible', 'close'])

const sizeClass = computed(
  () => ({ sm: 'max-w-sm', md: 'max-w-lg', lg: 'max-w-2xl', xl: 'max-w-4xl' }[props.size] || 'max-w-lg')
)

function setOpen(v) {
  emit('update:visible', v)
  if (!v) emit('close')
}
</script>

<template>
  <DialogRoot :open="visible" @update:open="setOpen">
    <DialogPortal>
      <DialogOverlay class="fixed inset-0 z-[100] erp-modal-overlay" />
      <DialogContent
        :class="[
          'fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-[101]',
          'w-[calc(100vw-2rem)] max-h-[90vh] flex flex-col',
          'bg-surface text-primary rounded-xl border border-line shadow-2xl erp-modal-content',
          sizeClass,
        ]"
      >
        <header
          v-if="title || $slots.header"
          class="flex items-center justify-between gap-4 px-6 py-4 border-b border-line shrink-0"
        >
          <slot name="header">
            <DialogTitle class="font-extrabold text-base">{{ title }}</DialogTitle>
          </slot>
          <DialogClose
            v-if="closable"
            class="text-muted hover:text-secondary text-lg font-bold p-1 cursor-pointer"
            aria-label="Close"
          >✕</DialogClose>
        </header>

        <DialogDescription class="sr-only">{{ title || 'Dialog' }}</DialogDescription>

        <div class="overflow-y-auto flex-1">
          <slot />
        </div>

        <footer v-if="$slots.footer" class="px-6 py-4 border-t border-line shrink-0">
          <slot name="footer" />
        </footer>
      </DialogContent>
    </DialogPortal>
  </DialogRoot>
</template>