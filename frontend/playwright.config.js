import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  globalSetup: './e2e/global-setup.js',
  testDir: './e2e',
  fullyParallel: false,
  workers: 1,
  retries: 0,
  reporter: [['list'], ['html', { open: 'never' }]],
  timeout: 45_000,
  expect: { timeout: 5_000 },
  use: {
    // 换到 5175，避开开发时占用的 5173
    baseURL: 'http://localhost:5175',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
  // 注意：本配置只负责启动前端。跑 E2E 前请确保后端已在 127.0.0.1:8000 运行。
  webServer: {
    command: 'PW_HTTP=1 npm run dev -- --port 5175 --strictPort',
    url: 'http://localhost:5175',
    // 必须 false：复用旧 dev 服务会丢失 PW_HTTP=1 环境变量，导致 mock 不生效
    reuseExistingServer: false,
    timeout: 60_000,
  },
})
