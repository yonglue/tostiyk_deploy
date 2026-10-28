/**
 * IndexedDB 封装（离线队列底层）。
 *
 * 设计：
 * - 不引第三方库（dexie 等），纯原生 API，减少依赖。
 * - 三个 store：
 *   * pending_orders: 离线开单队列（key: local_id）
 *   * cached_parts:  商品缓存（key: oem）
 *   * meta:          杂项（key-value，key: key）
 * - 单例连接：openDB() 首次打开后缓存 promise，避免重复 open。
 * - 所有写操作在独立事务里执行，失败向上抛。
 */

export const DB_NAME = 'tostiyk_offline'
export const DB_VERSION = 2  // v2: cached_parts keyPath 从 'oem' 改为 'id'（修复同 OEM 多品牌覆盖）
export const STORE_ORDERS = 'pending_orders'
export const STORE_PARTS = 'cached_parts'
export const STORE_META = 'meta'

let _dbPromise = null

export function openDB() {
  if (_dbPromise) return _dbPromise
  _dbPromise = new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, DB_VERSION)
    req.onupgradeneeded = (evt) => {
      const db = evt.target.result
      if (!db.objectStoreNames.contains(STORE_ORDERS)) {
        db.createObjectStore(STORE_ORDERS, { keyPath: 'local_id' })
      }
      // v2: 若存在 v1 的 cached_parts（keyPath='oem'），删掉重建（keyPath='id'）
      // 数据是缓存，重建不影响业务（下次 fetch 会重新填充）
      if (db.objectStoreNames.contains(STORE_PARTS) && evt.oldVersion < 2) {
        db.deleteObjectStore(STORE_PARTS)
      }
      if (!db.objectStoreNames.contains(STORE_PARTS)) {
        db.createObjectStore(STORE_PARTS, { keyPath: 'id' })
      }
      if (!db.objectStoreNames.contains(STORE_META)) {
        db.createObjectStore(STORE_META, { keyPath: 'key' })
      }
    }
    req.onsuccess = () => resolve(req.result)
    req.onerror = () => reject(req.error)
    req.onblocked = () => reject(new Error('IndexedDB blocked'))
  })
  return _dbPromise
}

function _store(db, name, mode) {
  return db.transaction(name, mode).objectStore(name)
}

function _req(req) {
  return new Promise((res, rej) => {
    req.onsuccess = () => res(req.result)
    req.onerror = () => rej(req.error)
  })
}

// ═══════ pending_orders ═══════
export async function putOrder(order) {
  const db = await openDB()
  await _req(_store(db, STORE_ORDERS, 'readwrite').put(order))
  return order.local_id
}

export async function getAllOrders() {
  const db = await openDB()
  return await _req(_store(db, STORE_ORDERS, 'readonly').getAll())
}

export async function deleteOrder(local_id) {
  const db = await openDB()
  await _req(_store(db, STORE_ORDERS, 'readwrite').delete(local_id))
}

export async function getOrderCount() {
  const db = await openDB()
  return await _req(_store(db, STORE_ORDERS, 'readonly').count())
}

export async function clearOrders() {
  const db = await openDB()
  await _req(_store(db, STORE_ORDERS, 'readwrite').clear())
}

// ═══════ cached_parts ═══════
export async function putParts(items) {
  if (!Array.isArray(items) || items.length === 0) return
  const db = await openDB()
  const tx = db.transaction(STORE_PARTS, 'readwrite')
  const store = tx.objectStore(STORE_PARTS)
  await Promise.all(items.map(it => _req(store.put(it))))
}

export async function getAllParts() {
  const db = await openDB()
  return await _req(_store(db, STORE_PARTS, 'readonly').getAll())
}

export async function clearParts() {
  const db = await openDB()
  await _req(_store(db, STORE_PARTS, 'readwrite').clear())
}

// ═══════ meta ═══════
export async function putMeta(key, value) {
  const db = await openDB()
  await _req(_store(db, STORE_META, 'readwrite').put({ key, value }))
}

export async function getMeta(key) {
  const db = await openDB()
  const row = await _req(_store(db, STORE_META, 'readonly').get(key))
  return row ? row.value : undefined
}

// ═══════ 测试/维护用 ═══════
export async function clearAll() {
  const db = await openDB()
  const tx = db.transaction([STORE_ORDERS, STORE_PARTS, STORE_META], 'readwrite')
  await Promise.all([
    _req(tx.objectStore(STORE_ORDERS).clear()),
    _req(tx.objectStore(STORE_PARTS).clear()),
    _req(tx.objectStore(STORE_META).clear()),
  ])
}

export async function closeDB() {
  if (_dbPromise) {
    const db = await _dbPromise
    db.close()
    _dbPromise = null
  }
}
