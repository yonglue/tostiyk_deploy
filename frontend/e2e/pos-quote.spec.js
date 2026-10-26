import { test, expect } from '@playwright/test'

const USERNAME = process.env.PW_ADMIN_USER || 'admin'
const PASSWORD = process.env.PW_ADMIN_PASS
if (!PASSWORD) throw new Error('缺少环境变量 PW_ADMIN_PASS，请先 export PW_ADMIN_PASS=<admin密码>')

async function login(page) {
  await page.goto('/')
  await page.evaluate(() => localStorage.clear())
  await page.reload()
  await page.locator('input[type="password"]').fill(PASSWORD)
  await page.locator('form input:not([type="password"])').first().fill(USERNAME)
  await page.locator('form button[type="submit"]').click()
  await expect(page.locator('nav')).toBeVisible()
}

test.describe('POS 核心业务与打印闭环', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      window.print = () => { console.log('Mock Print Triggered') }
      const originalCreateElement = document.createElement;
      document.createElement = function(tagName) {
        const el = originalCreateElement.call(this, tagName);
        if (tagName.toLowerCase() === 'iframe') {
          el.addEventListener('load', () => {
            if (el.contentWindow) el.contentWindow.print = () => { console.log('Mock iframe print triggered') };
          });
        }
        return el;
      };
    })
    await login(page)
  })

  test('快速收银：加购并成功结账，验证打印内容', async ({ page }) => {
    await page.locator('[data-testid="nav-pos"]').click()
    const searchInput = page.locator('[data-testid="pos-search-input"]')
    
    // 加购
    await searchInput.fill('TK-12345')
    await searchInput.press('Enter')
    await expect(page.locator('[data-testid="cart-table"] tbody tr').first()).toContainText('TK-12345')
    
    // 🌟 核心修复：不需要填钱！因为系统加购后默认会自动填满“刷卡”金额
    await page.waitForTimeout(1500) // 等待 watch(goodsTotalUsd) 触发
    
    const checkoutBtn = page.locator('[data-testid="pos-checkout-btn"]')
    // 如果按钮还是 disabled，才用强制输入兜底
    if (!(await checkoutBtn.isEnabled())) {
      const cashUsdInput = page.locator('[data-testid="pay-cash-usd"]')
      await cashUsdInput.fill('100')
      await page.keyboard.press('Tab')
      await page.waitForTimeout(1000)
    }
    
    // 等待按钮启用
    await checkoutBtn.click()
    
    const confirmPrintBtn = page.locator('.bg-emerald-600', { hasText: /Confirmar|确认|Print/i }).last()
    await expect(confirmPrintBtn).toBeVisible()
    
    await Promise.all([
      page.waitForResponse(res => res.url().includes('/api/pos/orders') && res.status() === 200),
      confirmPrintBtn.click()
    ])
    
    await page.waitForTimeout(1000)
    const printFrame = page.frameLocator('iframe').last()
    await expect(printFrame.locator('body')).toContainText(/TK-\d{4}-\d{4}/)
    await expect(printFrame.locator('body')).toContainText('TK-12345')
    await expect(page.getByText(/购物车为空|Carrito vacío|Cart is empty/)).toBeVisible()
  })

  test('历史补打：预览订单并验证弹窗内容', async ({ page }) => {
    await page.locator('[data-testid="nav-pos"]').click()
    const searchInput = page.locator('[data-testid="pos-search-input"]')
    
    await searchInput.fill('TK-12345')
    await searchInput.press('Enter')
    await page.waitForTimeout(1500) // 等待默认填钱
    
    const checkoutBtn = page.locator('[data-testid="pos-checkout-btn"]')
    if (!(await checkoutBtn.isEnabled())) {
      await page.locator('[data-testid="pay-cash-usd"]').fill('100')
      await page.keyboard.press('Tab')
      await page.waitForTimeout(1000)
    }
    await checkoutBtn.click()
    
    const confirmPrintBtn = page.locator('.bg-emerald-600', { hasText: /Confirmar|确认|Print/i }).last()
    await Promise.all([
      page.waitForResponse(res => res.url().includes('/api/pos/orders')),
      confirmPrintBtn.click()
    ])
    
    await page.waitForTimeout(3500) // 等自动销毁
    
    // 去历史记录补打
    await page.getByRole('button', { name: /销售历史与退货|Historial/i }).click()
    const previewBtn = page.getByRole('button', { name: /显示小票|Vista Previa/i }).first()
    await expect(previewBtn).toBeVisible()
    await previewBtn.click()
    
    await page.waitForTimeout(1000)
    const printFrame = page.frameLocator('iframe').last()
    await expect(printFrame.locator('body')).toContainText('TK-12345')
  })
})
