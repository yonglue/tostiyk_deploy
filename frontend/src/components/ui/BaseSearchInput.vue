<!-- src/components/ui/BaseSearchInput.vue -->
<script setup>
import { ref, watch, onUnmounted } from 'vue'
import BaseInput from './BaseInput.vue'

const props = defineProps({
  modelValue:  { type: String, default: '' },
  placeholder: { type: String, default: 'Search...' },
  debounce:    { type: Number, default: 200 },
})
const emit = defineEmits(['update:modelValue', 'search'])

let timer = null
const inner = ref(props.modelValue)
watch(() => props.modelValue, (v) => { inner.value = v })

watch(inner, (v) => {
  if (timer) clearTimeout(timer)
  timer = setTimeout(() => {
    emit('update:modelValue', v)
    emit('search', v)
  }, props.debounce)
})

function clear() {
  inner.value = ''
  emit('update:modelValue', '')
  emit('search', '')
}
function onEnter() {
  if (timer) clearTimeout(timer)
  emit('update:modelValue', inner.value)
  emit('search', inner.value)
}
onUnmounted(() => { if (timer) clearTimeout(timer) })
</script>

<template>
  <BaseInput
    v-model="inner"
    :placeholder="placeholder"
    :disabled="$attrs.disabled"
    prefix-icon
    type="search"
    @enter="onEnter"
  >
    <template #icon>
      <svg class="w-4 h-4" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5">
        <circle cx="9" cy="9" r="6" />
        <path d="m14 14 3 3" stroke-linecap="round" />
      </svg>
    </template>
    <template #suffix>
      <button
        v-if="inner"
        type="button"
        class="text-muted hover:text-primary cursor-pointer p-0.5"
        aria-label="Clear"
        @click="clear"
      >✕</button>
    </template>
  </BaseInput>
</template>