import { test, expect } from '@playwright/test'

const USERNAME = process.env.PW_ADMIN_USER || 'admin'
const PASSWORD = process.env.PW_ADMIN_PASS
if (!PASSWORD) throw new Error('缺少环境变量 PW_ADMIN_PASS，请先 export PW_ADMIN_PASS=<admin密码>')
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

test('客户还款后欠款正确扣减', async ({ page, request }) => {
  await login(page)
  const token = await page.evaluate(() => localStorage.getItem('tostiyk_token'))
  const authHeader = { Authorization: `Bearer ${token}` }

  const clientName = `测试客户应收_${Date.now()}`
  const createRes = await request.post(`${API_BASE}/api/clients`, {
    headers: authHeader,
    data: { name: clientName, debt: 100.0 }
  })
  if (!createRes.ok()) throw new Error(`创建客户失败: ${createRes.status()} ${await createRes.text()}`)

  // 刷新页面加载数据
  await page.locator('[data-testid="nav-clients"]').click()
  await expect(page.locator('tbody')).toBeVisible({ timeout: 10000 })
  
  const searchInput = page.locator('input[placeholder*="搜索"], input[placeholder*="Buscar"], input[placeholder*="Search"]').first()
  await expect(searchInput).toBeVisible({ timeout: 5000 })
  await searchInput.fill(clientName)
  await page.waitForTimeout(1000)
  
  const clientRow = page.locator('tbody tr').filter({ hasText: clientName })
  await expect(clientRow).toBeVisible({ timeout: 10000 })
  await clientRow.click()

  await page.getByTestId('btn-open-repay').first().click()
  const amountInput = page.getByTestId('input-repay-amount')
  await expect(amountInput).toBeVisible()

  // 填入金额
  await amountInput.fill('40')
  await amountInput.dispatchEvent('input')
  await page.waitForTimeout(500)

  // 使用 dispatchEvent 绕过 Playwright 点击限制，直接触发原生点击
  await page.getByTestId('btn-repay-submit').dispatchEvent('click')
  
  // 等待 1.5 秒，确保后端处理完毕且前端的 showSuccessModal 弹出来
  await page.waitForTimeout(1500)

  // 终极杀招：直接刷新页面，彻底清空所有弹窗和遮罩层
  await page.reload()
  
  // 重新进入客户页面
  await page.locator('[data-testid="nav-clients"]').click()
  await expect(page.locator('tbody')).toBeVisible({ timeout: 10000 })
  
  // 重新填入搜索词
  await searchInput.fill(clientName)
  await page.waitForTimeout(1000)

  const updatedRow = page.locator('tbody tr').filter({ hasText: clientName })
  await expect(updatedRow).toContainText('$ 60.00', { timeout: 10000 })
})
