// src/composables/useAuth.js
//
// 登录 / 登出 / 重置管理员密码 / 首次初始化系统，以及登录态在 localStorage 中的持久化。

import { ref } from 'vue'
import {
  apiFetch,
  clearAuthStorage,
  getToken,
  setToken,
  AUTH_CURRENT_USER_KEY,
  AUTH_EXPIRED_EVENT,
  AUTH_LOGGED_IN_KEY,
  AUTH_USERNAME_KEY,
} from '../utils/api'
import { useI18n } from './useI18n'

const EMPTY_USER = { username: '', role: 'staff', permissions: [] }

function readStoredUser() {
  try {
    const stored = localStorage.getItem(AUTH_CURRENT_USER_KEY)
    if (stored) {
      const parsed = JSON.parse(stored)
      return {
        username: parsed.username || '',
        role: parsed.role || 'staff',
        permissions: Array.isArray(parsed.permissions) ? parsed.permissions : [],
      }
    }
  } catch (e) {}
  return { ...EMPTY_USER }
}

const hadLoggedInFlag = localStorage.getItem(AUTH_LOGGED_IN_KEY) === 'true'
const hasSession = hadLoggedInFlag && !!getToken()
if (!hasSession) {
  clearAuthStorage()
}

const isLoggedIn = ref(hasSession)
const currentAdminUser = ref(hasSession ? (localStorage.getItem(AUTH_USERNAME_KEY) || '') : '')
const currentUserObj = ref(hasSession ? readStoredUser() : { ...EMPTY_USER })

const loginForm = ref({ username: '', password: '' })
const loginError = ref('')
const resetMessage = ref('')
const resetModalVisible = ref(false)
const resetPinInput = ref('')

const handleAuthExpired = () => {
  isLoggedIn.value = false
  currentAdminUser.value = ''
  currentUserObj.value = { ...EMPTY_USER }
  loginError.value = '登录已过期，请重新登录'
  loginForm.value.password = ''
}

if (typeof window !== 'undefined') {
  window.addEventListener(AUTH_EXPIRED_EVENT, handleAuthExpired)
}

export function useAuth() {
  const { t } = useI18n()

  // ============================================================
  // 🌟 新增 1：检测系统是否已初始化
  // ============================================================
  const checkSetupStatus = async () => {
    try {
      const res = await apiFetch('/api/auth/setup-status')
      if (res.ok) {
        const data = await res.json()
        return !!data.needs_setup
      }
    } catch (e) {
      console.error('检测初始化状态失败', e)
    }
    return false
  }

  // ============================================================
  // 🌟 新增 2：首次初始化（创建超级管理员）
  // ============================================================
  const initializeSystem = async (username, password) => {
    try {
      return await apiFetch('/api/auth/setup', {
        method: 'POST',
        body: JSON.stringify({ username, password }),
      })
    } catch (e) {
      return { ok: false, json: async () => ({ detail: '网络异常' }) }
    }
  }

  // ============================================================
  // 登录
  // ============================================================
  const handleLogin = async () => {
    loginError.value = ''
    resetMessage.value = ''
    if (!loginForm.value.username || !loginForm.value.password) {
      loginError.value = '请输入账号和密码'
      return
    }
    try {
      const res = await apiFetch('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify(loginForm.value),
      })
      if (res.ok) {
        const data = await res.json()
        if (!data.access_token) {
          loginError.value = '登录响应缺少访问令牌，请重试'
          return
        }

        const userData = {
          username: data.username,
          role: data.role || 'staff',
          permissions: data.permissions || [],
        }

        setToken(data.access_token)
        localStorage.setItem(AUTH_LOGGED_IN_KEY, 'true')
        localStorage.setItem(AUTH_USERNAME_KEY, data.username)
        localStorage.setItem(AUTH_CURRENT_USER_KEY, JSON.stringify(userData))

        currentAdminUser.value = data.username
        currentUserObj.value = userData
        isLoggedIn.value = true
      } else {
        const errData = await res.json()
        loginError.value = errData.detail || '登录失败'
      }
    } catch (e) {
      loginError.value = '服务器连接失败'
    }
  }

  const handleLogout = () => {
    isLoggedIn.value = false
    currentAdminUser.value = ''
    currentUserObj.value = { ...EMPTY_USER }
    clearAuthStorage()
    loginForm.value.username = ''
    loginForm.value.password = ''
    loginError.value = ''
  }

  const validateSession = async () => {
    if (!isLoggedIn.value || !getToken()) {
      if (isLoggedIn.value) handleAuthExpired()
      return false
    }
    try {
      const res = await apiFetch('/api/auth/me')
      if (!res.ok) return false
      const data = await res.json()
      const userData = {
        username: data.username,
        role: data.role || 'staff',
        permissions: data.permissions || [],
      }
      currentAdminUser.value = userData.username
      currentUserObj.value = userData
      localStorage.setItem(AUTH_USERNAME_KEY, userData.username)
      localStorage.setItem(AUTH_CURRENT_USER_KEY, JSON.stringify(userData))
      return true
    } catch (e) {
      return false
    }
  }

  const openResetModal = () => {
    loginError.value = ''
    resetMessage.value = ''
    resetPinInput.value = ''
    resetModalVisible.value = true
  }

  const submitResetPassword = async () => {
    loginError.value = ''
    resetMessage.value = ''
    if (!resetPinInput.value) return

    try {
      const res = await apiFetch('/api/auth/reset-admin', {
        method: 'POST',
        body: JSON.stringify({ security_pin: resetPinInput.value }),
      })
      if (res.ok) {
        resetModalVisible.value = false
        resetMessage.value = t.value.resetSuccess || "密码已成功重置为 'tostiyk2026'"
      } else {
        const errData = await res.json()
        loginError.value = errData.detail || '安全密钥验证失败'
        resetModalVisible.value = false
      }
    } catch (e) {
      loginError.value = '服务器连接失败'
      resetModalVisible.value = false
    }
  }

  return {
    isLoggedIn,
    currentAdminUser,
    currentUserObj,
    loginForm,
    loginError,
    resetMessage,
    resetModalVisible,
    resetPinInput,
    handleLogin,
    handleLogout,
    openResetModal,
    submitResetPassword,
    validateSession,
    // 🌟 暴露新增的两个方法
    checkSetupStatus,
    initializeSystem,
  }
}
