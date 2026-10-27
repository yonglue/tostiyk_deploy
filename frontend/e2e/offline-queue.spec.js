// frontend/e2e/offline-queue.spec.js
// 直接 page.evaluate 调 offline/db.js，验证 IndexedDB 底层语义。
// 不登录、不动 UI，纯底层单测。
import { test, expect } from '@playwright/test'

test.describe('离线队列 (IndexedDB 底层)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.evaluate(async () => {
      const mod = await import('/src/offline/db.js')
      await mod.clearAll()
    })
  })

  test('putOrder + getAllOrders + getOrderCount', async ({ page }) => {
    const result = await page.evaluate(async () => {
      const mod = await import('/src/offline/db.js')
      await mod.putOrder({ local_id: 'L1', total_usd: 10 })
      await mod.putOrder({ local_id: 'L2', total_usd: 20 })
      const count = await mod.getOrderCount()
      const all = await mod.getAllOrders()
      return {
        count,
        keys: all.map((o) => o.local_id).sort(),
      }
    })
    expect(result.count).toBe(2)
    expect(result.keys).toEqual(['L1', 'L2'])
  })

  test('deleteOrder 减少数量', async ({ page }) => {
    const result = await page.evaluate(async () => {
      const mod = await import('/src/offline/db.js')
      await mod.putOrder({ local_id: 'L1' })
      await mod.putOrder({ local_id: 'L2' })
      await mod.putOrder({ local_id: 'L3' })
      await mod.deleteOrder('L2')
      const all = await mod.getAllOrders()
      return all.map((o) => o.local_id).sort()
    })
    expect(result).toEqual(['L1', 'L3'])
  })

  test('clearOrders + clearAll', async ({ page }) => {
    const result = await page.evaluate(async () => {
      const mod = await import('/src/offline/db.js')
      await mod.putOrder({ local_id: 'L1' })
      await mod.putOrder({ local_id: 'L2' })
      await mod.putMeta('last_sync_at', 'X')
      await mod.clearOrders()
      const afterClearOrders = await mod.getOrderCount()
      await mod.putMeta('k2', 'v2')
      await mod.clearAll()
      const all = await mod.getAllOrders()
      const meta = await mod.getMeta('k2')
      return { afterClearOrders, allLen: all.length, meta }
    })
    expect(result.afterClearOrders).toBe(0)
    expect(result.allLen).toBe(0)
    expect(result.meta).toBeUndefined()
  })
})
