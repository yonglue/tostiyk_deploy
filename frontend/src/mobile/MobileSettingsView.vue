<template>
  <div class="min-h-full bg-slate-50 dark:bg-slate-950 pb-24">
    
    <header class="px-5 pt-8 pb-6">
      <h1 class="text-2xl font-black text-slate-800 dark:text-slate-100">{{ isZh ? '我的' : isEs ? 'Mi Perfil' : 'Settings' }}</h1>
      <p class="text-xs text-slate-400 mt-1">{{ isZh ? '偏好设置与账号管理' : isEs ? 'Preferencias y cuenta' : 'Preferences & account' }}</p>
    </header>

    <!-- 用户信息卡片 -->
    <section class="px-5 mb-6">
      <div class="bg-white dark:bg-slate-900 rounded-3xl p-5 border border-slate-100 dark:border-slate-800 flex items-center gap-4 shadow-sm">
        <div class="w-14 h-14 rounded-2xl bg-gradient-to-tr from-blue-500 to-indigo-600 flex items-center justify-center text-white font-black text-xl shadow-sm">
          {{ userInitial }}
        </div>
        <div>
          <h2 class="text-base font-bold text-slate-800 dark:text-slate-100">{{ currentUserObj.username || 'Unknown' }}</h2>
          <p class="text-[11px] font-bold text-accent dark:text-accent uppercase tracking-wider mt-0.5">{{ currentUserObj.role || 'Staff' }}</p>
        </div>
      </div>
    </section>

    <!-- 偏好设置列表 -->
    <section class="px-5 mb-6">
      <h3 class="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2 ml-1">{{ isZh ? '偏好设置' : isEs ? 'Preferencias' : 'Preferences' }}</h3>
      <div class="bg-white dark:bg-slate-900 rounded-2xl border border-slate-100 dark:border-slate-800 overflow-hidden">
        
        <!-- 深色模式 -->
        <div class="flex items-center justify-between p-4 border-b border-slate-50 dark:border-slate-800/60">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-lg bg-indigo-50 dark:bg-indigo-900/30 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
              <Moon v-if="isDark" :size="16" />
              <Sun v-else :size="16" />
            </div>
            <span class="text-sm font-semibold text-slate-700 dark:text-slate-300">{{ isZh ? '深色模式' : isEs ? 'Modo Oscuro' : 'Dark Mode' }}</span>
          </div>
          <button 
            @click="setTheme(isDark ? 'light' : 'dark')"
            class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-200 focus:outline-none"
            :class="isDark ? 'bg-accent' : 'bg-slate-200 dark:bg-slate-700'"
          >
            <span 
              class="inline-block h-5 w-5 transform rounded-full bg-white transition-transform duration-200 shadow-sm"
              :class="isDark ? 'translate-x-[22px]' : 'translate-x-[2px]'"
            />
          </button>
        </div>

        <!-- 🌟 优化：语言切换（改为点击弹出） -->
        <div @click="showLangPicker = true" class="flex items-center justify-between p-4 cursor-pointer active:bg-slate-50 dark:active:bg-slate-800/50 transition-colors">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-lg bg-emerald-50 dark:bg-emerald-900/30 flex items-center justify-center text-emerald-600 dark:text-emerald-400">
              <Globe :size="16" />
            </div>
            <span class="text-sm font-semibold text-slate-700 dark:text-slate-300">{{ isZh ? '系统语言' : isEs ? 'Idioma' : 'Language' }}</span>
          </div>
          <div class="flex items-center gap-1 text-sm font-bold text-slate-500 dark:text-slate-400">
            {{ currentLangLabel }}
            </div>
        </div>

      </div>
    </section>

    <!-- 退出登录按钮 -->
    <section class="px-5 mt-4">
      <button @click="handleLogout" class="w-full py-4 bg-white dark:bg-slate-900 rounded-2xl border border-rose-100 dark:border-rose-900/30 flex items-center justify-center gap-2 text-rose-600 dark:text-rose-400 font-bold text-sm shadow-sm active:scale-[0.98] transition-transform">
        <LogOut :size="18" />
        {{ isZh ? '安全退出登录' : isEs ? 'Cerrar Sesión' : 'Logout' }}
      </button>
    </section>

    <!-- 🌟 原生级语言选择弹窗 (Bottom Sheet) -->
    <Transition name="fade">
      <div v-if="showLangPicker" class="fixed inset-0 z-[100] bg-black/40 backdrop-blur-sm flex flex-col justify-end" @click.self="showLangPicker = false">
        <Transition name="slide-up">
          <div class="bg-slate-50 dark:bg-slate-900 w-full rounded-t-3xl overflow-hidden pb-safe">
            <div class="p-5 pb-3 text-center border-b border-slate-200/50 dark:border-slate-800/50">
              <h3 class="font-bold text-slate-800 dark:text-slate-100">{{ isZh ? '选择语言' : isEs ? 'Seleccionar Idioma' : 'Select Language' }}</h3>
            </div>
            <div class="p-2">
              <button 
                v-for="lang in langOptions" 
                :key="lang.value"
                @click="selectLanguage(lang.value)"
                class="w-full py-4 text-center font-bold text-base rounded-xl transition-colors flex items-center justify-center gap-2"
                :class="currentLang === lang.value ? 'text-accent dark:text-accent bg-accent/10 dark:bg-blue-900/20' : 'text-slate-700 dark:text-slate-300 active:bg-slate-200 dark:active:bg-slate-800'"
              >
                {{ lang.label }}
                <Check v-if="currentLang === lang.value" :size="18" />
              </button>
            </div>
            <div class="p-4 pb-6">
              <button @click="showLangPicker = false" class="w-full py-3.5 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-bold rounded-xl shadow-sm active:scale-[0.98] transition-transform">
                {{ isZh ? '取消' : isEs ? 'Cancelar' : 'Cancel' }}
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Moon, Sun, Globe, LogOut, ChevronRight, Check } from 'lucide-vue-next'
import { useTheme } from '../composables/useTheme'
import { useI18n } from '../composables/useI18n'
import { useAuth } from '../composables/useAuth'

const { isDark, setTheme } = useTheme()
const { currentLang } = useI18n()
const { currentUserObj, handleLogout } = useAuth()

const userInitial = computed(() => (currentUserObj.value?.username || 'U').charAt(0).toUpperCase())
const isZh = computed(() => currentLang.value === 'zh')
const isEs = computed(() => currentLang.value === 'es')

// 语言选择弹窗状态
const showLangPicker = ref(false)

const langOptions = [
  { value: 'es', label: 'Español' },
  { value: 'zh', label: '中文' },
  { value: 'en', label: 'English' }
]

const currentLangLabel = computed(() => {
  const lang = langOptions.find(l => l.value === currentLang.value)
  return lang ? lang.label : 'Español'
})

const selectLanguage = (val) => {
  currentLang.value = val
  showLangPicker.value = false
}
</script>

<style scoped>
/* 遮罩淡入淡出 */
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* 底部面板上滑动画 */
.slide-up-enter-active, .slide-up-leave-active { transition: transform 0.3s cubic-bezier(0.25, 1, 0.5, 1); }
.slide-up-enter-from, .slide-up-leave-to { transform: translateY(100%); }
</style>
