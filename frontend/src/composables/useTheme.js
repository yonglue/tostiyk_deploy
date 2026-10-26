// src/composables/useTheme.js
import { ref, computed, watch } from 'vue'

const STORAGE_KEY = 'tostiyk_theme'
const theme = ref(localStorage.getItem(STORAGE_KEY) || 'system')
let mediaQuery = null
let initialized = false

const systemPrefersDark = ref(false)

function updateSystemPref() {
  if (typeof window !== 'undefined' && window.matchMedia) {
    systemPrefersDark.value = window.matchMedia('(prefers-color-scheme: dark)').matches
  }
}

function applyTheme() {
  if (typeof document === 'undefined') return
  const isDark =
    theme.value === 'dark' ||
    (theme.value === 'system' && systemPrefersDark.value)
  const root = document.documentElement
  root.classList.toggle('dark', isDark)
  root.style.colorScheme = isDark ? 'dark' : 'light'
}

function initTheme() {
  if (initialized || typeof window === 'undefined') return
  initialized = true

  updateSystemPref()
  applyTheme()

  mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  const handler = (e) => {
    systemPrefersDark.value = e.matches
    if (theme.value === 'system') applyTheme()
  }
  // 兼容老浏览器
  if (mediaQuery.addEventListener) mediaQuery.addEventListener('change', handler)
  else if (mediaQuery.addListener) mediaQuery.addListener(handler)

  watch(theme, () => {
    localStorage.setItem(STORAGE_KEY, theme.value)
    applyTheme()
  })
}

export function useTheme() {
  initTheme()

  const isDark = computed(
    () => theme.value === 'dark' || (theme.value === 'system' && systemPrefersDark.value)
  )
  const resolvedTheme = computed(() => (isDark.value ? 'dark' : 'light'))

  const setTheme = (next) => {
    if (!['light', 'dark', 'system'].includes(next)) return
    theme.value = next
  }

  const cycleTheme = () => {
    const order = ['light', 'dark', 'system']
    const i = order.indexOf(theme.value)
    setTheme(order[(i + 1) % order.length])
  }


  const toggleThemeWithTransition = (event) => {
    if (!document.startViewTransition) { cycleTheme(); return }
    const x = event?.clientX ?? window.innerWidth / 2
    const y = event?.clientY ?? window.innerHeight / 2
    const endRadius = Math.hypot(Math.max(x, window.innerWidth - x), Math.max(y, window.innerHeight - y))
    const order = ['light', 'dark', 'system']
    const currentIndex = order.indexOf(theme.value)
    const nextTheme = order[(currentIndex + 1) % order.length]
    let nextIsDark = nextTheme === 'dark' || (nextTheme === 'system' && systemPrefersDark.value)

    document.documentElement.classList.add('view-transition-active')
    const transition = document.startViewTransition(() => {
      const root = document.documentElement
      root.classList.toggle('dark', nextIsDark)
      root.style.colorScheme = nextIsDark ? 'dark' : 'light'
      theme.value = nextTheme
    })

    transition.ready.then(() => {
      const root = document.documentElement
      root.style.setProperty('--x', `${x}px`)
      root.style.setProperty('--y', `${y}px`)
      root.style.setProperty('--r', `${endRadius}px`)
      if (nextIsDark) root.classList.add('transition-to-dark')
      else root.classList.add('transition-to-light')
    })

    transition.finished.finally(() => {
      document.documentElement.classList.remove('transition-to-dark', 'transition-to-light', 'view-transition-active')
    })
  }
  return { theme, isDark, resolvedTheme, setTheme, cycleTheme, toggleThemeWithTransition }
}