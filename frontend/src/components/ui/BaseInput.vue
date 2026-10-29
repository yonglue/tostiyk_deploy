<!-- src/components/ui/BaseInput.vue -->
<script setup>
import { computed, useAttrs } from 'vue'

defineOptions({ inheritAttrs: false })

const props = defineProps({
  modelValue: { type: [String, Number], default: '' },
  label:       { type: String, default: '' },
  error:       { type: String, default: '' },
  hint:        { type: String, default: '' },
  type:        { type: String, default: 'text' },
  size:        { type: String, default: 'md' },        // sm | md | lg
  disabled:    { type: Boolean, default: false },
  readonly:    { type: Boolean, default: false },
  prefixIcon:  { type: Boolean, default: false },      // true → 左侧留 40px 给图标
})
const emit = defineEmits(['update:modelValue', 'enter', 'blur', 'focus'])
const attrs = useAttrs()

const sizeClass = computed(
  () => ({ sm: 'text-xs', md: 'text-sm', lg: 'text-base' }[props.size] || 'text-sm')
)

function onInput(e) { emit('update:modelValue', e.target.value) }
</script>

<template>
  <div class="flex flex-col gap-1.5 w-full">
    <label v-if="label" class="text-xs font-semibold text-secondary">{{ label }}</label>

    <div class="relative w-full">
      <div v-if="prefixIcon" class="absolute left-3 top-1/2 -translate-y-1/2 text-muted pointer-events-none z-10">
        <slot name="icon" />
      </div>

      <input
        :value="modelValue"
        :type="type"
        :disabled="disabled"
        :readonly="readonly"
        v-bind="attrs"
        :class="[
          'w-full transition-colors',
          sizeClass,
          prefixIcon ? '!pl-10' : '',
          error ? 'input-error' : '',
        ]"
        @input="onInput"
        @keydown.enter="$emit('enter', $event)"
        @blur="$emit('blur', $event)"
        @focus="$emit('focus', $event)"
      />

      <div v-if="$slots.suffix" class="absolute right-3 top-1/2 -translate-y-1/2 text-muted z-10">
        <slot name="suffix" />
      </div>
    </div>

    <span v-if="error" class="text-xs text-danger">{{ error }}</span>
    <span v-else-if="hint" class="text-xs text-muted">{{ hint }}</span>
  </div>
</template>