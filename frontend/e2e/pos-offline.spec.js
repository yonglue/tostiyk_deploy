// frontend/e2e/pos-offline.spec.js
import { test, expect } from '@playwright/test'

const USERNAME = process.env.PW_ADMIN_USER || 'admin'
const PASSWORD = process.env.PW_ADMIN_PASS
if (!PASSWORD) throw new Error('缺少环境变量 PW_ADMIN_PASS')

// 🌟 共享谓词 + 开关（route/unroute 必须同一函数引用才能正确解除）
const _OFFLINE_TEST_PREDICATE = (url) => url.pathname === '/api/pos/orders'
let _ABORT_POST = true

async function login(page) {
  await page.goto('/')
  await page.evaluate(() => localStorage.clear())
  await page.reload()
  await page.locator('input[type="password"]').fill(PASSWORD)
  await page.locator('form input:not([type="password"])').first().fill(USERNAME)
  await page.locator('form button[type="submit"]').click()
  await expect(page.locator('nav')).toBeVisible()
}

async function addAndCheckout(page) {
  await page.locator('[data-testid="nav-pos"]').click()
  const searchInput = page.locator('[data-testid="pos-search-input"]')
  await searchInput.fill('TK-12345')
  await searchInput.press('Enter')
  await page.waitForTimeout(1500)

  const checkoutBtn = page.locator('[data-testid="pos-checkout-btn"]')
  if (!(await checkoutBtn.isEnabled())) {
    await page.locator('[data-testid="pay-cash-usd"]').fill('100')
    await page.keyboard.press('Tab')
    await page.waitForTimeout(1000)
  }
  await checkoutBtn.click()
  // 🌟 离线状态下不弹窗，直接清空购物车并入队
}

test.describe('POS 离线入队', () => {
  test.beforeEach(async ({ page }) => {
    // 🌟 禁用 Service Worker：SW 会绕过 page.route 直接 fetch，导致拦截失效
    await page.addInitScript(() => {
      if (navigator.serviceWorker) {
        try {
          navigator.serviceWorker.register = () => Promise.reject(new Error('SW disabled for e2e'))
        } catch (_) {}
      }
    })
    await page.addInitScript(() => {
      window.print = () => {}
      const orig = document.createElement
      document.createElement = function (tag) {
        const el = orig.call(this, tag)
        if (String(tag).toLowerCase() === 'iframe') {
          el.addEventListener('load', () => {
            if (el.contentWindow) el.contentWindow.print = () => {}
          })
        }
        return el
      }
    })
    await login(page)
    // 🌟 清理已注册的 SW（即使 addInitScript 生效，防 context 内残留）
    await page.evaluate(async () => {
      if ('serviceWorker' in navigator) {
        try {
          const regs = await navigator.serviceWorker.getRegistrations()
          for (const r of regs) await r.unregister()
        } catch (_) {}
      }
      const db = await import('/src/offline/db.js')
      await db.clearAll()
    })
  })

  test('断网结账：入队 1 条 + 购物车清空 + 指示器显示待同步 1', async ({ page, context }) => {
    // 模拟网络断
    // 🌟 只 abort POST；开关 _ABORT_POST 控制是否生效（flush 用例里关闭）
    _ABORT_POST = true
    await context.route(_OFFLINE_TEST_PREDICATE, (route) => {
      if (!_ABORT_POST) return route.continue()
      if (route.request().method() !== 'POST') return route.continue()
      return route.abort('failed')
    })

    await addAndCheckout(page)

    // 购物车清空（202 分支走完）
    await expect(
      page.locator('[data-testid="cart-table"] tbody tr', { hasText: 'TK-12345' })
    ).toHaveCount(0, { timeout: 10_000 })

    // IndexedDB 有 1 条
    const count = await page.evaluate(async () => {
      const db = await import('/src/offline/db.js')
      return await db.getOrderCount()
    })
    expect(count).toBe(1)

    // 指示器显示待同步 1（reload 触发 refreshCount）
    await page.reload()
    await expect(page.locator('nav')).toBeVisible({ timeout: 10_000 })
    await expect(page.locator('[data-testid="offline-indicator"]'))
      .toContainText(/待同步\s*1|Pending\s*1|Pendiente\s*1/, { timeout: 5_000 })

    // 清理
    await page.evaluate(async () => {
      const db = await import('/src/offline/db.js')
      await db.clearAll()
    })
  })

  test('离线入队后联网 flush：队列清空', async ({ page, context }) => {
    // 🌟 只 abort POST；开关 _ABORT_POST 控制是否生效（flush 用例里关闭）
    _ABORT_POST = true
    await context.route(_OFFLINE_TEST_PREDICATE, (route) => {
      if (!_ABORT_POST) return route.continue()
      if (route.request().method() !== 'POST') return route.continue()
      return route.abort('failed')
    })
    await addAndCheckout(page)
    await page.waitForTimeout(1500)

    // 确认入队
    expect(await page.evaluate(async () => {
      const db = await import('/src/offline/db.js')
      return await db.getOrderCount()
    })).toBe(1)

    // 恢复网络
    _ABORT_POST = false   // 🌟 关闭 abort（不依赖 unroute 函数引用匹配）

    // 手动 flush
    const result = await page.evaluate(async () => {
      const { useOfflineQueue } = await import('/src/composables/useOfflineQueue.js')
      const q = useOfflineQueue()
      return await q.flush()
    })
    expect(result.synced).toBe(1)
    expect(result.failed).toBe(0)

    // 队列清空
    expect(await page.evaluate(async () => {
      const db = await import('/src/offline/db.js')
      return await db.getOrderCount()
    })).toBe(0)

    // 清理
    await page.evaluate(async () => {
      const db = await import('/src/offline/db.js')
      await db.clearAll()
    })
  })
})
