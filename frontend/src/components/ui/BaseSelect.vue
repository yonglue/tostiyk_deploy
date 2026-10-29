<!-- src/components/ui/BaseSelect.vue -->
<script setup>
import { ref, computed, watch, onUnmounted, nextTick } from 'vue'

const props = defineProps({
  modelValue:  { type: [String, Number, null], default: null },
  options:     { type: Array, default: () => [] },   // [{ label, value, disabled? }]
  label:       { type: String, default: '' },        // 👈 新增 label
  placeholder: { type: String, default: 'Select...' },
  searchable:  { type: Boolean, default: false },
  disabled:    { type: Boolean, default: false },
  size:        { type: String, default: 'md' },       // sm | md | lg
  clearable:   { type: Boolean, default: false },
})
const emit = defineEmits(['update:modelValue', 'change'])

const open  = ref(false)
const query = ref('')
const hi    = ref(0)
const triggerRef = ref(null)
const panelRef   = ref(null)
const searchRef  = ref(null)

const sizeClass = computed(
  () => ({ sm: 'text-xs py-1', md: 'text-sm py-2', lg: 'text-base py-2.5' }[props.size] || 'text-sm py-2')
)

const filtered = computed(() => {
  if (!props.searchable || !query.value) return props.options
  const q = query.value.toLowerCase()
  return props.options.filter(o => String(o.label).toLowerCase().includes(q))
})

const selectedLabel = computed(() => {
  const opt = props.options.find(o => o.value === props.modelValue)
  return opt ? opt.label : ''
})

function toggle() {
  if (props.disabled) return
  open.value = !open.value
}
function select(opt) {
  if (opt.disabled) return
  emit('update:modelValue', opt.value)
  emit('change', opt.value)
  open.value = false
  query.value = ''
}
function clear(e) {
  e.stopPropagation()
  emit('update:modelValue', null)
  emit('change', null)
}
function onKeydown(e) {
  if (!open.value) {
    if (['Enter', ' ', 'ArrowDown'].includes(e.key)) {
      e.preventDefault(); open.value = true
    }
    return
  }
  if (e.key === 'Escape') { open.value = false; return }
  if (e.key === 'ArrowDown') {
    e.preventDefault(); hi.value = Math.min(hi.value + 1, filtered.value.length - 1)
  } else if (e.key === 'ArrowUp') {
    e.preventDefault(); hi.value = Math.max(hi.value - 1, 0)
  } else if (e.key === 'Enter') {
    e.preventDefault()
    const opt = filtered.value[hi.value]
    if (opt) select(opt)
  }
}
function onClickOutside(e) {
  if (triggerRef.value?.contains(e.target)) return
  if (panelRef.value?.contains(e.target)) return
  open.value = false
}

watch(open, async (v) => {
  if (v) {
    hi.value = Math.max(0, filtered.value.findIndex(o => o.value === props.modelValue))
    await nextTick()
    if (props.searchable && searchRef.value) searchRef.value.focus()
    document.addEventListener('mousedown', onClickOutside)
  } else {
    document.removeEventListener('mousedown', onClickOutside)
  }
})

onUnmounted(() => { document.removeEventListener('mousedown', onClickOutside) })
</script>

<template>
  <div class="flex flex-col gap-1.5 w-full">
    <label v-if="label" class="text-xs font-semibold text-secondary">{{ label }}</label>

    <div class="relative w-full">
      <button
        ref="triggerRef"
        type="button"
        :disabled="disabled"
        :class="[
          'w-full flex items-center justify-between gap-2 text-left',
          'bg-surface-raised border border-line rounded-md px-3',
          'text-primary outline-none transition-colors',
          'focus:border-accent disabled:opacity-50 cursor-pointer',
          sizeClass,
        ]"
        @click="toggle"
        @keydown="onKeydown"
      >
        <span :class="selectedLabel ? 'text-primary' : 'text-muted'" class="truncate">
          {{ selectedLabel || placeholder }}
        </span>
        <span class="flex items-center gap-1 shrink-0">
          <button
            v-if="clearable && modelValue !== null && modelValue !== ''"
            type="button"
            class="text-muted hover:text-primary cursor-pointer px-0.5"
            aria-label="Clear"
            @click="clear"
          >✕</button>
          <svg class="w-4 h-4 text-muted" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M5.5 7.5L10 12l4.5-4.5" stroke-linecap="round" />
          </svg>
        </span>
      </button>

      <div
        v-if="open"
        ref="panelRef"
        class="absolute z-[200] mt-1 w-full bg-surface border border-line rounded-md shadow-2xl max-h-64 overflow-auto"
      >
        <div v-if="searchable" class="p-2 border-b border-line sticky top-0 bg-surface">
          <input
            ref="searchRef"
            v-model="query"
            type="text"
            placeholder="Search..."
            class="w-full bg-surface-raised border border-line rounded px-2 py-1 text-xs outline-none focus:border-accent"
            @keydown="onKeydown"
          />
        </div>
        <ul role="listbox">
          <li
            v-for="(opt, i) in filtered"
            :key="opt.value"
            role="option"
            :aria-selected="opt.value === modelValue"
            :class="[
              'px-3 py-2 text-sm cursor-pointer transition-colors',
              i === hi ? 'bg-surface-muted' : '',
              opt.disabled ? 'opacity-40 cursor-not-allowed' : 'hover:bg-surface-muted',
              opt.value === modelValue ? 'font-bold text-accent' : 'text-primary',
            ]"
            @click="select(opt)"
            @mouseenter="hi = i"
          >
            {{ opt.label }}
          </li>
          <li v-if="filtered.length === 0" class="px-3 py-3 text-xs text-muted text-center">
            No options
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>