import { test, expect } from '@playwright/test'

const USERNAME = process.env.PW_ADMIN_USER || 'admin'
const PASSWORD = process.env.PW_ADMIN_PASS || 'x'

async function login(page) {
  await page.goto('/')
  await page.evaluate(() => localStorage.clear())
  await page.reload()
  await page.locator('input[type="password"]').fill(PASSWORD)
  await page.locator('form input:not([type="password"])').first().fill(USERNAME)
  await page.locator('form button[type="submit"]').click()
  await expect(page.locator('nav')).toBeVisible({ timeout: 10000 })
  // 只按 Escape 关弹窗，不再删 Vue 管理的 DOM 节点
  await page.keyboard.press('Escape').catch(() => {})
}

test.describe('库存盘点 B1', () => {
  test.beforeEach(async ({ page }) => {
    await login(page)
    await page.locator('[data-testid="nav-inventory_audit"]').click()
  })

  test('提交盘点差异并生成历史流水', async ({ page }) => {
    // 按 OEM 定位，不依赖排序
    const row = page.locator('tr', { hasText: 'TK-12345' })
    await expect(row).toBeVisible({ timeout: 10000 })

    // 断言没有残留遮罩 —— 有就让测试明确失败
    await expect(page.locator('.fixed.inset-0.z-50')).toHaveCount(0)

    // 填实盘数字（999 → 888，差异 -111）
    const input = row.locator('input[type="number"]')
    await input.fill('888')

    // 确认差异提示出现（.text-rose-600 或 .text-emerald-600）
    await expect(row.locator('.text-rose-600, .text-emerald-600').first()).toBeVisible()

    // 提交（不再 force）
    const submitBtn = page.getByRole('button', { name: /提交盘点结果/ })
    await expect(submitBtn).toBeEnabled()
    await submitBtn.click()

    // 等成功提示
    await expect(page.getByText(/盘点完成/)).toBeVisible({ timeout: 5000 })

    // 切历史 tab
    await page.getByRole('button', { name: /历史盘点记录/ }).click()
    await expect(page.locator('tbody tr').first()).toBeVisible()
    await expect(page.locator('tbody').first()).toContainText(/盘盈|盘亏/)
  })
})
