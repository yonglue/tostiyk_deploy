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
}

test.describe('移动端主流程 (iPhone 14 Pro 模拟)', () => {
  test.use({ viewport: { width: 393, height: 852 }, isMobile: true, hasTouch: true })

  test.beforeEach(async ({ page }) => {
    await login(page)
    await expect(page.locator('nav')).toBeVisible({ timeout: 10000 })
  })

  test('底部 5 个 Tab 切换与深色模式', async ({ page }) => {
    await page.locator('nav button').filter({ hasText: /产品|Productos|Products/ }).click()
    await expect(page.getByPlaceholder(/搜索 OEM|Buscar OEM|Search OEM/)).toBeVisible()

    await page.locator('nav button').filter({ hasText: /流水|Movimientos|History/ }).click()
    await expect(page.getByText(/全部|Todos|All/).first()).toBeVisible()

    await page.locator('nav button').filter({ hasText: /客户|Clientes|Clients/ }).click()
    await expect(page.getByText(/客户总应收欠款|应收欠款|Total por cobrar|Total Receivables/i)).toBeVisible()

    await page.locator('nav button').filter({ hasText: /我的|Mi Perfil|Me/ }).click()
    
    const html = page.locator('html')
    await expect(html).not.toHaveClass(/dark/)
    await page.getByText(/深色模式|Modo Oscuro|Dark Mode/).locator('..').locator('..').locator('button').click()
    await expect(html).toHaveClass(/dark/)
  })

  test('产品详情页滑入与手势返回', async ({ page }) => {
    // 1. 进入产品页
    await page.locator('nav button').filter({ hasText: /产品|Productos|Products/ }).click()
    
    // 2. 找到搜索框并输入 OEM，强制过滤出我们注入的商品
    const searchInput = page.getByPlaceholder(/搜索 OEM|Buscar OEM|Search OEM/i)
    await expect(searchInput).toBeVisible({ timeout: 10000 })
    await searchInput.fill('TK-12345')
    await page.waitForTimeout(1500) // 等待防抖或接口返回

    // 3. 找到商品卡片并点击（如果找不到会直接抛错红掉，而不是跳过）
    const testCard = page.locator('div').filter({ hasText: 'TK-12345' }).last()
    await expect(testCard).toBeVisible({ timeout: 10000 })
    await testCard.click()

    // 4. 详情页断言与返回
    const backBtn = page.locator('header button').first()
    await expect(backBtn).toBeVisible({ timeout: 5000 })
    
    await backBtn.click()
    await expect(searchInput).toBeVisible()
  })
})
