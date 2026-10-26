import { test, expect } from '@playwright/test'
import { execSync } from 'child_process'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const USERNAME = process.env.PW_ADMIN_USER || 'admin'
const PASSWORD = process.env.PW_ADMIN_PASS
const API_BASE = 'http://localhost:8000'

async function login(page) {
  await page.goto('/')
  await page.evaluate(() => localStorage.clear())
  await page.reload()
  await page.locator('input[type="password"]').fill(PASSWORD)
  await page.locator('form input:not([type="password"])').first().fill(USERNAME)
  await page.locator('form button[type="submit"]').click()
  await expect(page.locator('nav')).toBeVisible()
}

test.skip('客户还款后欠款正确扣减', async ({ page, request }) => {
  await login(page)
  
  const token = await page.evaluate(() => localStorage.getItem('tostiyk_token'))
  const authHeader = { Authorization: `Bearer ${token}` }

  // 1. 准备测试客户
  const clientName = `测试客户应收_${Date.now()}`
  await request.post(`${API_BASE}/api/clients`, {
    headers: authHeader,
    data: { name: clientName }
  })
  
  // 2. 用 SQL 把他的欠款设为 100 美元
  const dbPath = path.resolve(__dirname, '../../tostiyk_erp.db')
  execSync(`sqlite3 "${dbPath}" "UPDATE client SET debt = 100 WHERE name = '${clientName}';"`)

  // 3. 进入客户页面
  await page.locator('[data-testid="nav-clients"]').click()
  await page.waitForTimeout(1000)
  await page.reload()
  await page.waitForTimeout(1000) // 强制刷新
  
  const searchInput = page.locator('input[placeholder*="搜索"], input[placeholder*="Buscar"]').first()
  if (await searchInput.isVisible()) { await searchInput.fill(clientName); await page.waitForTimeout(500) }
  const clientRow = page.locator('tbody tr').filter({ hasText: clientName })
  await expect(clientRow).toBeVisible({ timeout: 10000 })
  await expect(clientRow).toContainText('$ 100.00')

  // 4. 点击该客户行
  await clientRow.click()

  // 5. 点击收款按钮
  const repayBtn = page.getByTestId('btn-open-repay').first()
  await expect(repayBtn).toBeVisible({ timeout: 5000 })
  await repayBtn.click()

  // 6. 输入金额 40
  const amountInput = page.getByTestId('input-repay-amount')
  await amountInput.clear()
  await amountInput.fill('40')
  await page.keyboard.press('Tab')
  await page.waitForTimeout(500)
  
  // 7. 确认收款
  await page.getByTestId('btn-repay-submit').click()

  // 8. 等待成功提示
  await expect(page.getByText(/成功|exitoso|success/i).first()).toBeVisible({ timeout: 5000 })
  
  // 9. 刷新页面验证
  await page.reload()
  await page.locator('[data-testid="nav-clients"]').click()
  await page.waitForTimeout(1000)
  
  const updatedRow = page.locator('tbody tr').filter({ hasText: clientName })
  await expect(updatedRow).toContainText('$ 60.00', { timeout: 10000 })
})
