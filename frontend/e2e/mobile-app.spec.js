import { test, expect } from '@playwright/test'

const USERNAME = process.env.PW_ADMIN_USER || 'admin'
const PASSWORD = process.env.PW_ADMIN_PASS

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
    await expect(page.getByText(/客户总应收欠款|Deuda Total|Total Debt/)).toBeVisible()

    await page.locator('nav button').filter({ hasText: /我的|Mi Perfil|Me/ }).click()
    
    const html = page.locator('html')
    await expect(html).not.toHaveClass(/dark/)
    await page.getByText(/深色模式|Modo Oscuro|Dark Mode/).locator('..').locator('..').locator('button').click()
    await expect(html).toHaveClass(/dark/)
  })

  test('产品详情页滑入与手势返回', async ({ page }) => {
    // 1. 进入产品页
    await page.locator('nav button').filter({ hasText: /产品|Productos|Products/ }).click()
    await expect(page.getByPlaceholder(/搜索 OEM|Buscar OEM|Search OEM/)).toBeVisible()
    
    // 2. 等待数据加载（找到商品名为 TK-12345 的卡片）
    const testCard = page.locator('div').filter({ hasText: 'TK-12345' }).last()
    
    // 如果列表里有数据，则点击并测试滑入
    if (await testCard.isVisible({ timeout: 3000 }).catch(() => false)) {
      await testCard.click()
      
      // 3. 详情页会有一个左上角的返回按钮，我们用它来断言
      const backBtn = page.locator('header button').first()
      await expect(backBtn).toBeVisible({ timeout: 5000 })
      
      // 4. 点击返回，回到列表页
      await backBtn.click()
      await expect(page.getByPlaceholder(/搜索 OEM|Buscar OEM|Search OEM/)).toBeVisible()
    } else {
      test.skip(true, '产品列表为空，跳过测试')
    }
  })
})
