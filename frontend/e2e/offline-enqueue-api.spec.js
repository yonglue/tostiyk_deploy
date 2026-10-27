// frontend/e2e/offline-enqueue-api.spec.js
// 验证 apiFetch + offline.queueOnFail：网络断时自动入队 + 返回合成 202
import { test, expect } from '@playwright/test'

const USERNAME = process.env.PW_ADMIN_USER || 'admin'
const PASSWORD = process.env.PW_ADMIN_PASS

if (!PASSWORD) {
  throw new Error('缺少环境变量 PW_ADMIN_PASS')
}

async function login(page) {
  await page.goto('/')
  await page.evaluate(() => localStorage.clear())
  await page.reload()
  const pw = page.locator('input[type="password"]')
  await expect(pw).toBeVisible({ timeout: 10_000 })
  await page.locator('form input:not([type="password"])').first().fill(USERNAME)
  await pw.fill(PASSWORD)
  await page.locator('form button[type="submit"]').click()
  await expect(page.locator('input[type="password"]')).toHaveCount(0, { timeout: 10_000 })
  await expect(page.locator('nav')).toBeVisible({ timeout: 5_000 })
}

test.beforeEach(async ({ page }) => {
  await login(page)
  await page.evaluate(async () => {
    const db = await import('/src/offline/db.js')
    await db.clearAll()
  })
})

test('offline.queueOnFail + 网络断 → 202 QUEUED + 入队 1 条', async ({ page }) => {
  const result = await page.evaluate(async () => {
    const realFetch = window.fetch
    window.fetch = () => Promise.reject(new Error('network down'))
    try {
      const { apiFetch } = await import('/src/utils/api.js')
      const res = await apiFetch('/api/pos/orders', {
        method: 'POST',
        body: JSON.stringify({ items: [], total_usd: 99 }),
        offline: { queueOnFail: true },
        silent: true,
      })
      const body = await res.json()
      const db = await import('/src/offline/db.js')
      const all = await db.getAllOrders()
      return { status: res.status, body, queueCount: all.length, first: all[0] }
    } finally {
      window.fetch = realFetch
    }
  })

  expect(result.status).toBe(202)
  expect(result.body.status).toBe('QUEUED')
  expect(result.queueCount).toBe(1)
  expect(result.first.total_usd).toBe(99)
  expect(result.first._url).toBe('/api/pos/orders')
  expect(result.first._method).toBe('POST')
})

test('未传 offline.queueOnFail → 网络断时照常抛错，不入队', async ({ page }) => {
  const result = await page.evaluate(async () => {
    const realFetch = window.fetch
    window.fetch = () => Promise.reject(new Error('network down'))
    try {
      const { apiFetch } = await import('/src/utils/api.js')
      let threw = false
      try {
        await apiFetch('/api/pos/orders', {
          method: 'POST',
          body: JSON.stringify({ items: [] }),
          silent: true,
        })
      } catch (e) {
        threw = true
      }
      const db = await import('/src/offline/db.js')
      const all = await db.getAllOrders()
      return { threw, queueCount: all.length }
    } finally {
      window.fetch = realFetch
    }
  })

  expect(result.threw).toBe(true)
  expect(result.queueCount).toBe(0)
})

test('成功响应时不入队（200 优先）', async ({ page }) => {
  const result = await page.evaluate(async () => {
    const realFetch = window.fetch
    window.fetch = () => Promise.resolve(new Response(
      JSON.stringify({ status: 'success' }),
      { status: 200, headers: { 'Content-Type': 'application/json' } },
    ))
    try {
      const { apiFetch } = await import('/src/utils/api.js')
      const res = await apiFetch('/api/pos/orders', {
        method: 'POST',
        body: JSON.stringify({ items: [] }),
        offline: { queueOnFail: true },
        silent: true,
      })
      const db = await import('/src/offline/db.js')
      const all = await db.getAllOrders()
      return { status: res.status, queueCount: all.length }
    } finally {
      window.fetch = realFetch
    }
  })

  expect(result.status).toBe(200)
  expect(result.queueCount).toBe(0)
})
