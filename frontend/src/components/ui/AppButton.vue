<template>
  <button
    :class="[
      'inline-flex items-center justify-center font-medium transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed',
      sizeClasses,
      variantClasses
    ]"
  >
    <slot />
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  variant: {
    type: String,
    default: 'secondary', // primary | secondary | ghost | danger
  },
  size: {
    type: String,
    default: 'md', // sm | md | lg
  },
  block: {
    type: Boolean,
    default: false,
  },
})

// 统一尺寸，保证触摸区 >= 36px
const sizeClasses = computed(() => {
  const sizes = {
    sm: 'h-8 px-3 text-xs rounded-control',
    md: 'h-9 px-4 text-sm rounded-control',
    lg: 'h-10 px-5 text-sm rounded-control',
  }
  return `${sizes[props.size]} ${props.block ? 'w-full' : ''}`
})

// 统一样式（彻底摒弃白底，使用语义化颜色）
const variantClasses = computed(() => {
  const variants = {
    primary: 'bg-brand text-white hover:bg-brand-hover shadow-sm',
    secondary: 'bg-surface-sunken text-content-primary border border-border-strong hover:bg-slate-200 dark:hover:bg-slate-700',
    ghost: 'bg-transparent text-content-secondary hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-content-primary',
    danger: 'bg-red-50 text-red-600 border border-red-200 hover:bg-red-100 dark:bg-red-900/20 dark:text-red-400 dark:border-red-800 dark:hover:bg-red-900/40',
  }
  return variants[props.variant]
})
</script>
