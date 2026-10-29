import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'
import fs from 'fs'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0', // 仅限本地访问  // 允许局域网任何设备访问: '127.0.0.1'
    port: 5173,
    https: false,      // 关闭 HTTPS，免去证书烦恼
        proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false
      },
      '/uploads': { // 🌟 紧急修复：把图片请求也转发给后端
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  build: {
    chunkSizeWarningLimit: 1000,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            if (id.includes('echarts') || id.includes('zrender')) return 'vendor-echarts'
            if (id.includes('vue') || id.includes('pinia')) return 'vendor-vue'
            return 'vendor'
          }
        }
      }
    }
  }
})
