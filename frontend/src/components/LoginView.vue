<template>
  <div class="h-[100dvh] w-full overflow-y-auto flex bg-slate-50 dark:bg-[#0b1120] transition-colors duration-300 relative selection:bg-blue-500/30">
    <div class="fixed -top-32 -left-32 w-[500px] h-[500px] bg-blue-500/20 dark:bg-blue-600/15 rounded-full blur-[120px] pointer-events-none animate-pulse-slow"></div>
    <div class="fixed -bottom-32 -right-32 w-[500px] h-[500px] bg-indigo-500/20 dark:bg-indigo-600/15 rounded-full blur-[120px] pointer-events-none animate-pulse-slow" style="animation-delay: 2s"></div>

    <div class="fixed top-6 right-6 z-50">
      <button @click="toggleThemeWithTransition($event)" class="w-11 h-11 rounded-2xl flex items-center justify-center backdrop-blur-md border border-slate-200/80 dark:border-slate-700/60 bg-white/60 dark:bg-slate-800/60 shadow-sm hover:scale-105 active:scale-95 transition-all duration-300">
        <Sun v-if="isDark" :size="20" class="text-amber-400" />
        <Moon v-else :size="20" class="text-indigo-500" />
      </button>
    </div>

    <div class="hidden lg:flex w-1/2 h-full flex-col justify-center items-center z-10 relative">
      <div class="w-24 h-24 rounded-[2rem] bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white shadow-2xl shadow-blue-500/40 mb-8 animate-float">
        <Cpu :size="48" />
      </div>
      <h1 class="text-5xl font-black text-slate-800 dark:text-white tracking-tighter bg-clip-text text-transparent bg-gradient-to-r from-slate-800 to-slate-500 dark:from-white dark:to-slate-400">TOSTIYK ERP</h1>
      <p class="text-slate-500 dark:text-slate-400 mt-5 max-w-md text-center leading-relaxed text-lg font-medium">{{ isZh ? '全渠道汽车配件商业管理系统。' : isEs ? 'Sistema ERP Multimoneda para Autopartes.' : 'Multi-currency Auto Parts ERP.' }}<br><span class="text-sm">{{ isZh ? '库存、收银、财务，一站式掌控。' : isEs ? 'Inventario, Caja y Finanzas en un solo lugar.' : 'Inventory, POS, and Finance in one place.' }}</span>
      </p>
    </div>

    <div class="w-full lg:w-1/2 min-h-full flex flex-col items-center justify-center p-6 z-10">
      <div class="w-full max-w-md bg-white/70 dark:bg-slate-900/60 backdrop-blur-2xl border border-white/60 dark:border-slate-700/50 rounded-3xl shadow-2xl p-7 sm:p-9 transition-all duration-500">
        <div class="lg:hidden flex flex-col items-center mb-8">
          <div class="w-16 h-16 rounded-2xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center text-white shadow-lg mb-4"><Cpu :size="32" /></div>
          <h1 class="text-2xl font-black text-slate-800 dark:text-white">TOSTIYK ERP</h1>
        </div>

        <div v-if="isChecking" class="py-16 flex flex-col items-center text-slate-400">
          <div class="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-4"></div>
          <span class="text-xs font-mono">{{ isZh ? '正在检测系统状态...' : isEs ? 'Comprobando estado...' : 'Checking status...' }}</span>
        </div>

        <div v-else-if="needsSetup">
          <div class="mb-7">
            <h2 class="text-2xl font-black text-blue-600 dark:text-blue-400">{{ isZh ? '🚀 欢迎使用' : isEs ? '🚀 Bienvenido' : '🚀 Welcome' }}</h2>
            <p class="text-xs text-slate-500 mt-1.5">{{ isZh ? '这是系统的首次启动，请设置您的超级管理员账号。' : isEs ? 'Primer inicio. Configure su super administrador.' : 'First start. Setup super admin.' }}</p>
          </div>
          <form @submit.prevent="handleSetupWrapper" class="space-y-5">
            <div>
              <label class="block text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-2">{{ isZh ? '管理员账号' : isEs ? 'Usuario Admin' : 'Admin Account' }}</label>
              <input ref="setupUsernameRef" v-model="setupForm.username" type="text" :class="['w-full bg-slate-100/70 dark:bg-slate-950/50 border rounded-2xl px-4 py-3 text-sm outline-none transition-all duration-300 focus:ring-4', hasSetupUsernameError ? 'input-error border-rose-500 ring-rose-500/10 animate-shake' : 'border-slate-200 dark:border-slate-700 focus:border-blue-500 focus:ring-blue-500/10']" placeholder="{{ isZh ? '默认使用 admin' : isEs ? 'Usar admin por defecto' : 'Default use admin' }}" @input="hasSetupUsernameError = false; setupError = ''" />
            </div>
            <div>
              <label class="block text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-2">{{ isZh ? '设置密码' : isEs ? 'Configurar contraseña' : 'Set Password' }}</label>
              <input ref="setupPasswordRef" v-model="setupForm.password" type="password" :class="['w-full bg-slate-100/70 dark:bg-slate-950/50 border rounded-2xl px-4 py-3 text-sm outline-none transition-all duration-300 focus:ring-4', hasSetupPasswordError ? 'input-error border-rose-500 ring-rose-500/10 animate-shake' : 'border-slate-200 dark:border-slate-700 focus:border-blue-500 focus:ring-blue-500/10']" placeholder="{{ isZh ? '请输入强密码' : isEs ? 'Ingrese contraseña fuerte' : 'Enter strong password' }}" @input="hasSetupPasswordError = false; setupError = ''" />
            </div>
            <button type="submit" :disabled="isSubmittingSetup" class="w-full py-3.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-2xl font-bold text-sm shadow-xl transition-all active:scale-[0.98]">{{ isSubmittingSetup ? '正在初始化...' : '完成设置并进入系统' }}</button>
          </form>
        </div>

        <div v-else>
          <div class="mb-7 sm:mb-9">
            <h2 class="text-2xl font-black text-slate-800 dark:text-white">{{ isZh ? '欢迎回来' : isEs ? 'Bienvenido' : 'Welcome Back' }}</h2>
            <p class="text-xs sm:text-sm text-slate-500 dark:text-slate-400 mt-1.5 font-medium">{{ isZh ? '请输入您的管理员凭证进入系统' : isEs ? 'Ingrese sus credenciales' : 'Enter your credentials' }}</p>
          </div>
          <form @submit.prevent="handleLoginWrapper" class="space-y-5">
            <div>
              <label class="block text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-2">{{ isZh ? '管理员账号' : isEs ? 'Usuario Admin' : 'Admin Account' }}</label>
              <input ref="usernameInputRef" v-model="loginForm.username" type="text" :class="['w-full bg-slate-100/70 dark:bg-slate-950/50 border rounded-2xl px-4 py-3 text-sm outline-none transition-all duration-300 focus:ring-4', hasUsernameError ? 'input-error border-rose-500 ring-rose-500/10 animate-shake' : 'border-slate-200 dark:border-slate-700 focus:border-blue-500 focus:ring-blue-500/10']" @input="hasUsernameError = false; loginError = ''" />
            </div>
            <div>
              <label class="block text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-2">{{ isZh ? '密码' : isEs ? 'Contraseña' : 'Password' }}</label>
              <input ref="passwordInputRef" v-model="loginForm.password" type="password" :class="['w-full bg-slate-100/70 dark:bg-slate-950/50 border rounded-2xl px-4 py-3 text-sm outline-none transition-all duration-300 focus:ring-4', hasPasswordError ? 'input-error border-rose-500 ring-rose-500/10 animate-shake' : 'border-slate-200 dark:border-slate-700 focus:border-blue-500 focus:ring-blue-500/10']" @input="hasPasswordError = false; loginError = ''" />
            </div>
            <button type="submit" class="w-full py-3.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-2xl font-bold text-sm shadow-xl transition-all active:scale-[0.98]">{{ isZh ? '安全登录' : isEs ? 'Iniciar Sesión' : 'Secure Login' }}</button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { Cpu, Sun, Moon } from 'lucide-vue-next'
import { useAuth } from '../composables/useAuth'
import { useNotifications } from '../composables/useNotifications'
import { useI18n } from '../composables/useI18n'
import { useTheme } from '../composables/useTheme'

const { loginForm, loginError, handleLogin, checkSetupStatus, initializeSystem } = useAuth()
const { showSuccessModal } = useNotifications()
const { currentLang } = useI18n()
const { isDark, toggleThemeWithTransition } = useTheme()

const isZh = computed(() => currentLang.value === 'zh')
const isEs = computed(() => currentLang.value === 'es')

const isChecking = ref(true)
const needsSetup = ref(false)
const setupForm = ref({ username: 'admin', password: '' })
const setupError = ref('')
const isSubmittingSetup = ref(false)

const hasUsernameError = ref(false)
const hasPasswordError = ref(false)
const hasSetupUsernameError = ref(false)
const hasSetupPasswordError = ref(false)

const usernameInputRef = ref(null)
const passwordInputRef = ref(null)
const setupUsernameRef = ref(null)
const setupPasswordRef = ref(null)

onMounted(async () => {
  needsSetup.value = await checkSetupStatus()
  isChecking.value = false
})

const handleLoginWrapper = async () => {
  hasUsernameError.value = false
  hasPasswordError.value = false
  try {
    if (!loginForm.value?.username?.trim()) {
      hasUsernameError.value = true
      if (usernameInputRef.value) usernameInputRef.value.focus()
      return
    }
    if (!loginForm.value?.password) {
      hasPasswordError.value = true
      if (passwordInputRef.value) passwordInputRef.value.focus()
      return
    }
    await handleLogin()
    if (loginError.value) {
      hasPasswordError.value = true
      loginForm.value.password = ''
      if (passwordInputRef.value) passwordInputRef.value.focus()
    }
  } catch (err) {
    hasPasswordError.value = true
  }
}

const handleSetupWrapper = async () => {
  hasSetupUsernameError.value = false
  hasSetupPasswordError.value = false
  setupError.value = ''
  try {
    if (!setupForm.value?.username?.trim()) {
      hasSetupUsernameError.value = true
      if (setupUsernameRef.value) setupUsernameRef.value.focus()
      return
    }
    if (setupForm.value?.password?.length < 4) {
      hasSetupPasswordError.value = true
      if (setupPasswordRef.value) setupPasswordRef.value.focus()
      return
    }
    isSubmittingSetup.value = true
    const res = await initializeSystem(setupForm.value.username, setupForm.value.password)
    if (res.ok) {
      showSuccessModal('🎉 系统初始化成功，请使用新账号登录！')
      needsSetup.value = false
      loginForm.value.username = setupForm.value.username
    } else {
      const err = await res.json()
      setupError.value = err.detail || '初始化失败'
      hasSetupPasswordError.value = true
    }
  } catch (err) {
    hasSetupPasswordError.value = true
  } finally {
    isSubmittingSetup.value = false
  }
}
</script>

<style scoped>
.animate-shake { animation: shake 0.4s cubic-bezier(0.36, 0.07, 0.19, 0.97) both; }
@keyframes shake { 0%, 100% { transform: translateX(0); } 20%, 60% { transform: translateX(-6px); } 40%, 80% { transform: translateX(6px); } }
.animate-float { animation: float 6s ease-in-out infinite; }
@keyframes float { 0%, 100% { transform: translateY(0px); } 50% { transform: translateY(-10px); } }
.animate-pulse-slow { animation: pulseSlow 8s ease-in-out infinite; }
@keyframes pulseSlow { 0%, 100% { opacity: 0.6; transform: scale(1); } 50% { opacity: 1; transform: scale(1.1); } }
.input-error { border-color: #f43f5e !important; }
</style>
