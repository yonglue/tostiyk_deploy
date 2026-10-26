// 每次发版修改这里的版本号，或者构建时自动注入
const CACHE_VERSION = 'v1.0.1';
const CACHE_NAME = `tostiyk-erp-${CACHE_VERSION}`;

self.addEventListener('install', (e) => {
  self.skipWaiting()
})

self.addEventListener('activate', (e) => {
  e.waitUntil(clients.claim())
})

self.addEventListener('fetch', (e) => {
  // 简化的网络优先策略：尝试网络请求，失败则走缓存
  e.respondWith(
    fetch(e.request).catch(() => caches.match(e.request))
  )
})
