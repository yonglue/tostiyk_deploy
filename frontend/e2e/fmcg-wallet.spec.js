// frontend/e2e/fmcg-wallet.spec.js
import { test, expect } from '@playwright/test'

const USERNAME = process.env.PW_ADMIN_USER || 'admin'
const PASSWORD = process.env.PW_ADMIN_PASS

if (!PASSWORD) {
  throw new Error('缺少环境变量 PW_ADMIN_PASS，请先 export PW_ADMIN_PASS=<admin密码>')
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

async function gotoFmcgWallet(page) {
  const nav = page.locator('[data-testid="nav-fmcg_wallet"]')
  await expect(nav).toBeVisible({ timeout: 5_000 })
  await nav.click()
  await expect(
    page.locator('h2').filter({ hasText: /找零钱包|Change Wallet|Monedero/ })
  ).toBeVisible({ timeout: 5_000 })
}

test('FMCG 找零钱包：侧边栏入口可见并可点开', async ({ page }) => {
  await login(page)
  await gotoFmcgWallet(page)
  await expect(page.locator('[data-testid="fmcg-wallet-search"]')).toBeVisible()
  await expect(page.locator('[data-testid="fmcg-wallet-credit"]')).toBeVisible()
})

test('FMCG 找零钱包：查不存在的手机号显示空状态', async ({ page }) => {
  await login(page)
  await gotoFmcgWallet(page)

  const phone = `0414-E2E-404-${Date.now()}`
  // 左侧查询面板：唯一一个 input[type="text"] 里排第一个
  await page.locator('input[type="text"]').first().fill(phone)
  await page.locator('[data-testid="fmcg-wallet-search"]').click()

  await expect(page.locator('[data-testid="fmcg-wallet-empty"]')).toBeVisible({ timeout: 10_000 })
})

test('FMCG 找零钱包：手动入账成功后余额卡片出现', async ({ page }) => {
  await login(page)
  await gotoFmcgWallet(page)

  const ts = Date.now()
  const phone = `0414-E2E-${ts}`
  const refId = `E2E-MAN-${ts}`

  // input[type="text"] 顺序（按 DOM 顺序）：
  //   0 = 左侧查询手机号
  //   1 = 右侧入账手机号
  //   2 = 右侧 ref_type
  //   3 = 右侧 ref_id
  //   4 = 右侧 note
  const textInputs = page.locator('input[type="text"]')
  await textInputs.nth(1).fill(phone)
  await page.locator('input[type="number"]').fill('1.5')
  await textInputs.nth(2).fill('manual')
  await textInputs.nth(3).fill(refId)

  await page.locator('[data-testid="fmcg-wallet-credit"]').click()

  // 入账成功提示（后端口径 amount 是 4 位小数）
  await expect(page.getByText(/\+1\.5000/)).toBeVisible({ timeout: 10_000 })

  // 用同一手机号查询，应显示余额卡片
  await textInputs.nth(0).fill(phone)
  await page.locator('[data-testid="fmcg-wallet-search"]').click()
  await expect(page.locator('[data-testid="fmcg-wallet-balance-card"]')).toBeVisible({ timeout: 10_000 })
})
