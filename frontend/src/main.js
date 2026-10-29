import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

async function bootstrap() {
  const params = new URLSearchParams(window.location.search)
  const isDevUi = import.meta.env.DEV && params.get('dev') === 'ui'

  let RootComponent = App
  if (isDevUi) {
    const mod = await import('./components/dev/UiShowcase.vue')
    RootComponent = mod.default
  }

  createApp(RootComponent).mount('#app')

  // 生产 App 才注册 SW；dev UiShowcase 不需要
  if (!isDevUi && 'serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/sw.js').catch(() => {
        // 开发环境或没有 https 时静默失败即可
      })
    })
  }
}

bootstrap()