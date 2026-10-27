// frontend/e2e/offline-indicator.spec.js
// 验证 header 上的离线队列指示器：塞 2 单到 IndexedDB → 指示器显示"待同步 2"
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

  const passwordInput = page.locator('input[type="password"]')
  await expect(passwordInput).toBeVisible({ timeout: 10_000 })
  await page.locator('form input:not([type="password"])').first().fill(USERNAME)
  await passwordInput.fill(PASSWORD)
  await page.locator('form button[type="submit"]').click()
  await expect(page.locator('input[type="password"]')).toHaveCount(0, { timeout: 10_000 })
  await expect(page.locator('nav')).toBeVisible({ timeout: 5_000 })
}

test('离线指示器：无待同步订单时不显示数字', async ({ page }) => {
  await login(page)
  const indicator = page.locator('[data-testid="offline-indicator"]')
  await expect(indicator).toBeVisible()
  // 默认在线 + 0 待同步 → label 为空
  await expect(indicator).not.toContainText(/待同步|Pending|Pendiente/)
})

test('离线指示器：塞 2 单后显示"待同步 2"', async ({ page }) => {
  await login(page)

  // 先清空队列，保证起点干净
  await page.evaluate(async () => {
    const mod = await import('/src/offline/db.js')
    await mod.clearAll()
    await mod.putOrder({ local_id: 'IND-1', total_usd: 1 })
    await mod.putOrder({ local_id: 'IND-2', total_usd: 2 })
  })

  // 触发 refreshCount（用线上事件或直接 reload）
  await page.reload()
  await expect(page.locator('nav')).toBeVisible({ timeout: 10_000 })

  const indicator = page.locator('[data-testid="offline-indicator"]')
  await expect(indicator).toBeVisible()
  await expect(indicator).toContainText(/待同步\s*2|Pending\s*2|Pendiente\s*2/, { timeout: 5_000 })

  // 清理
  await page.evaluate(async () => {
    const mod = await import('/src/offline/db.js')
    await mod.clearAll()
  })
})
