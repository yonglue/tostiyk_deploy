<!-- src/components/ThemeSwitcher.vue -->
<template>
  <button
    @click="toggleThemeWithTransition($event)"
    class="group relative flex items-center justify-center w-10 h-10 rounded-2xl
           border border-slate-200/80 dark:border-slate-700/60
           shadow-2xs backdrop-blur-md
           transition-all duration-300 ease-out hover:scale-105 active:scale-95"
    :class="{
      'bg-amber-50/80 hover:bg-amber-100 dark:bg-slate-800/70 dark:hover:bg-slate-700/80': theme === 'light',
      'bg-indigo-50/80 hover:bg-indigo-100 dark:bg-indigo-900/40 dark:hover:bg-indigo-800/60': theme === 'dark',
      'bg-sky-50/80 hover:bg-sky-100 dark:bg-slate-800/70 dark:hover:bg-slate-700/80': theme === 'system'
    }"
    :title="`${currentOption.label} →`"
  >
    <Transition name="spin-fade" mode="out-in">
      <component 
        :is="currentOption.icon" 
        :size="20" 
        :stroke-width="2.5" 
        :key="currentOption.value"
        :class="{
          'text-amber-500': theme === 'light',
          'text-indigo-500 dark:text-indigo-400': theme === 'dark',
          'text-sky-500': theme === 'system'
        }"
      />
    </Transition>
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { Sun, Moon, MonitorSmartphone } from 'lucide-vue-next'
import { useTheme } from '../composables/useTheme'

// 🌟 引入炫酷的动画切换函数
const { theme, toggleThemeWithTransition } = useTheme()

const options = [
  { value: 'light',  icon: Sun,                label: '白天 / Día / Day' },
  { value: 'dark',   icon: Moon,               label: '黑夜 / Noche / Night' },
  { value: 'system', icon: MonitorSmartphone,  label: '系统 / Sistema / System' },
]

const currentOption = computed(() => {
  return options.find(o => o.value === theme.value) || options[0]
})
</script>

<style scoped>
/* 切换时的旋转 + 淡入淡出动画 */
.spin-fade-enter-active,
.spin-fade-leave-active {
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.spin-fade-enter-from {
  opacity: 0;
  transform: rotate(-90deg) scale(0.5);
}
.spin-fade-leave-to {
  opacity: 0;
  transform: rotate(90deg) scale(0.5);
}
</style>
