import { test, expect } from '@playwright/test'
import { execSync } from 'child_process'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const USERNAME = process.env.PW_ADMIN_USER || 'admin'
const PASSWORD = process.env.PW_ADMIN_PASS
if (!PASSWORD) throw new Error('缺少 PW_ADMIN_PASS')
const API_BASE = 'http://localhost:8000'

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

test('财务 - 供应商付款核销', async ({ page, request }) => {
  await login(page)
  
  const token = await page.evaluate(() => localStorage.getItem('tostiyk_token'))
  const authHeader = { Authorization: `Bearer ${token}` }

  // 1. 通过 API 创建供应商 (只传必填)
  const supName = `付款测试供应商_${Date.now()}`
  const createRes = await request.post(`${API_BASE}/api/suppliers`, {
    headers: authHeader,
    data: { name: supName }
  })
  if (!createRes.ok()) throw new Error(`创建供应商失败: ${createRes.status()}`)

  // 2. 🌟 用 SQL 强行给它注入 $100 欠款
  const dbPath = path.resolve(__dirname, '../../tostiyk_erp.db')
  // 注意：表名可能是 supplier 或者 suppliers，字段可能是 debt 或 debt_usd
  execSync(`sqlite3 "${dbPath}" "UPDATE suppliers SET debt_usd = 100.0 WHERE name = '${supName}';"`)
  // 如果上面报错找不到表，尝试大写 Supplier 等

  // 3. 进入采购中心
  await page.locator('[data-testid="nav-procurement"]').click().catch(() => {
    return page.getByRole('button', { name: /采购|Compras/i }).click()
  })
  await page.waitForTimeout(1000)

  // 4. 点击“供应商管理” Tab
  const supplierTab = page.locator('button').filter({ hasText: /供应商管理|Proveedores|Suppliers/i }).first()
  await await expect(supplierTab).toBeVisible(); await supplierTab.click()
  await page.waitForTimeout(1000)

  // 5. 强制刷新按钮
  const refreshBtn = page.locator('button').filter({ hasText: /🔄 刷新|🔄 Actualizar|🔄 Refresh/i }).first()
  if (await refreshBtn.isVisible()) {
    await await expect(refreshBtn).toBeVisible(); await refreshBtn.click()
    await page.waitForTimeout(1500)
  }

  // 6. 填搜索框
  const searchInput = page.locator('input[placeholder*="搜索"], input[placeholder*="Buscar"]').first()
  await searchInput.fill(supName)
  await page.waitForTimeout(1000)

  // 7. 找到供应商行
  const supRow = page.locator('tbody tr').filter({ hasText: supName }).first()
  await expect(supRow).toContainText('$ 100.00', { timeout: 5000 })

  // 8. 点击付款按钮
  const payBtn = supRow.locator('button').filter({ hasText: /付款|Pagar|Pay/i }).first()
  await await expect(payBtn).toBeVisible(); await payBtn.click()

  // 9. 填金额并确认
  await page.waitForTimeout(1000)
  const amountInput = page.locator('input[type="number"]').last()
  await amountInput.fill('40')
  await amountInput.dispatchEvent('input')
  await page.waitForTimeout(500)
  
  const confirmBtn = page.locator('button').filter({ hasText: /确认付款|Confirmar pago|Confirm Payment/i }).first()
  await await expect(confirmBtn).toBeVisible(); await confirmBtn.click()

  // 10. 验证扣款
  await page.waitForTimeout(1500)
  await searchInput.fill(supName)
  await page.waitForTimeout(1000)
  
  const updatedRow = page.locator('tbody tr').filter({ hasText: supName }).first()
  await expect(updatedRow).toContainText('$ 60.00', { timeout: 10000 })
})
