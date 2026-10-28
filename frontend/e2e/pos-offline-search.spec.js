// frontend/e2e/pos-offline-search.spec.js
// 验证 6.1：离线时 POS 仍能从 cached_parts 搜索加购并结账入队
import { test, expect } from '@playwright/test'

const USERNAME = process.env.PW_ADMIN_USER || 'admin'
const PASSWORD = process.env.PW_ADMIN_PASS
if (!PASSWORD) throw new Error('缺少环境变量 PW_ADMIN_PASS')

async function login(page) {
  await page.goto('/')
  await page.evaluate(() => localStorage.clear())
  await page.reload()
  await page.locator('input[type="password"]').fill(PASSWORD)
  await page.locator('form input:not([type="password"])').first().fill(USERNAME)
  await page.locator('form button[type="submit"]').click()
  await expect(page.locator('nav')).toBeVisible()
}

test.describe('POS 离线缓存', () => {
  test.beforeEach(async ({ page }) => {
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
    await page.evaluate(async () => {
      const db = await import('/src/offline/db.js')
      // 只清订单队列，保留 cached_parts（本 spec 需要缓存）
      await db.clearOrders()
    })
  })

  test('离线搜索加购结账：从 cached_parts 加载 + 订单入队', async ({ page, context }) => {
    // 1. 主动触发一次 fetchParts 保证缓存写入（login 里的 refreshAll 可能已完成，
    //    单纯 waitForResponse 会抓不到已发生的响应）
    await page.evaluate(async () => {
      const { useInventory } = await import('/src/composables/useInventory.js')
      await useInventory().fetchParts()
    })

    // 2. 等缓存写入完成
    await expect.poll(async () => {
      return await page.evaluate(async () => {
        const db = await import('/src/offline/db.js')
        return (await db.getAllParts()).length
      })
    }, { timeout: 15_000 }).toBeGreaterThan(0)

    // 3. 模拟断网：/api/parts 全失败 + /api/pos/orders 只 abort POST
    await context.route(
      (url) => url.pathname === '/api/parts',
      (route) => route.abort('failed'),
    )
    await context.route(
      (url) => url.pathname === '/api/pos/orders',
      (route) => {
        if (route.request().method() !== 'POST') return route.continue()
        return route.abort('failed')
      },
    )

    // 4. reload：App.vue onMounted → refreshAll → fetchParts 网络失败 → 从缓存读
    await page.reload()
    await expect(page.locator('nav')).toBeVisible({ timeout: 10_000 })
    // 🌟 等待 partsList 从缓存恢复（fetchParts 里 getAllParts 是异步的，不能直接进 POS）
    await expect.poll(async () => {
      return await page.evaluate(async () => {
        const { useInventory } = await import('/src/composables/useInventory.js')
        return useInventory().partsList.value.length
      })
    }, { timeout: 15_000, intervals: [200, 500, 1000, 2000] }).toBeGreaterThan(0)

    // 5. 进 POS，搜索应能从缓存命中
    await page.waitForTimeout(1000)  // 等 reload 后的 Sidebar CSS transition
    // 🌟 reload 后 Sidebar 折叠动画会让 Playwright 的 stability 检查一直失败，
    //    改用 evaluate click 绕过（DOM 存在且可点击，只是"位置在动"）
    const navPos = page.locator('[data-testid="nav-pos"]')
    await navPos.waitFor({ state: 'attached', timeout: 10_000 })
    await navPos.evaluate(el => el.click())
    await page.waitForTimeout(1500)

    // 诊断：POS 里 partsList 实际长度 + 是否含 TK-12345
    const diag = await page.evaluate(async () => {
      const { useInventory } = await import('/src/composables/useInventory.js')
      const list = useInventory().partsList.value
      const hasTK = list.some(p => (p.oem || '').toUpperCase().includes('TK-12345'))
      return { len: list.length, hasTK, firstOems: list.slice(0, 3).map(p => p.oem) }
    })

    const searchInput = page.locator('[data-testid="pos-search-input"]')
    await searchInput.fill('TK-12345')
    await searchInput.press('Enter')
    await page.waitForTimeout(1500)

    const cartRow = page.locator('[data-testid="cart-table"] tbody tr').first()
    await expect(cartRow).toContainText('TK-12345', { timeout: 5_000 })

    // 6. 结账 → 202 入队
    await page.waitForTimeout(1500)
    const checkoutBtn = page.locator('[data-testid="pos-checkout-btn"]')
    if (!(await checkoutBtn.isEnabled())) {
      await page.locator('[data-testid="pay-cash-usd"]').fill('100')
      await page.keyboard.press('Tab')
      await page.waitForTimeout(1500)
    }
    await checkoutBtn.evaluate(el => el.click())

    const confirmPrintBtn = page.locator('.bg-emerald-600', { hasText: /Confirmar|确认|Print/i }).last()
    await confirmPrintBtn.waitFor({ state: 'attached', timeout: 10_000 })
    await confirmPrintBtn.evaluate(el => el.click())
    await page.waitForTimeout(2000)

    // 7. 断言入队 1 条
    expect(await page.evaluate(async () => {
      const db = await import('/src/offline/db.js')
      return await db.getOrderCount()
    })).toBe(1)

    // 清理
    await page.evaluate(async () => {
      const db = await import('/src/offline/db.js')
      await db.clearAll()
    })
  })
})
