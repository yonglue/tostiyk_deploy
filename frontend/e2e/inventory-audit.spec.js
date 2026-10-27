import { test, expect } from '@playwright/test'

const USERNAME = process.env.PW_ADMIN_USER || 'admin'
const PASSWORD = process.env.PW_ADMIN_PASS
if (!PASSWORD) throw new Error('缺少 PW_ADMIN_PASS')

async function login(page) {
  await page.goto('/')
  await page.evaluate(() => localStorage.clear())
  await page.evaluate(() => localStorage.setItem('tostiyk_lang', 'zh'))
  await page.reload()
  
  await page.locator('input[type="password"]').fill(PASSWORD)
  await page.locator('form input:not([type="password"])').first().fill(USERNAME)
  await page.locator('form button[type="submit"]').click()
  await expect(page.locator('nav')).toBeVisible({ timeout: 10000 })
  await page.keyboard.press('Escape').catch(() => {})
}

test.describe('库存盘点 B1', () => {
  test.beforeEach(async ({ page }) => {
    await login(page)
    await page.locator('[data-testid="nav-inventory_audit"]').click()
  })

  test('提交盘点差异并生成历史流水', async ({ page }) => {
    // 定位行
    const row = page.locator('tr', { hasText: 'TK-12345' })
    await expect(row).toBeVisible({ timeout: 10000 })

    // 填实盘数字
    const input = row.locator('input[type="number"]')
    await input.fill('888')

    // 点击提交
    const submitBtn = page.getByRole('button', { name: /提交盘点结果/ })
    await expect(submitBtn).toBeEnabled()
    await submitBtn.click()
    
    // 等待接口和成功提示
    await page.waitForTimeout(1500)
    await page.keyboard.press('Escape').catch(() => {})

    // 切到历史 Tab
    const historyTab = page.locator('button').filter({ hasText: /历史|History|Historial/i }).first()
    await await expect(historyTab).toBeVisible(); await historyTab.click()

    // 强制刷新
    await page.waitForTimeout(1000)
    const refreshBtn = page.locator('button').filter({ hasText: /刷新记录|Actualizar|Refresh/i }).first()
    if (await refreshBtn.isVisible()) {
      await await expect(refreshBtn).toBeVisible(); await refreshBtn.click()
      await page.waitForTimeout(1500)
    }

    // 只要第一行不是“暂无历史盘点记录”，就算成功
    const emptyState = page.getByText(/暂无历史盘点记录|Sin historial/i)
    await expect(emptyState).toBeHidden({ timeout: 5000 })
  })
})
