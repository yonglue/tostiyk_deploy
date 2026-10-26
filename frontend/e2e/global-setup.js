export default async function globalSetup() {
  console.log('\n🛠️  [GlobalSetup] 开始重置测试数据...')
  const API_BASE = process.env.PW_API_BASE || 'http://127.0.0.1:8000'
  const ADMIN_USER = process.env.PW_ADMIN_USER || 'admin'
  const ADMIN_PASS = process.env.PW_ADMIN_PASS || 'x'

  // 1. 尝试 setup（admin 已存在会返回 4xx，忽略）
  try {
    const setupRes = await fetch(`${API_BASE}/api/auth/setup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: ADMIN_USER, password: ADMIN_PASS })
    })
    console.log(`[GlobalSetup] admin setup 状态: ${setupRes.status}（已存在属正常）`)
  } catch (e) {
    console.log(`[GlobalSetup] admin setup 跳过: ${e.message}`)
  }

  // 2. 登录必须成功，否则 throw
  const loginRes = await fetch(`${API_BASE}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: ADMIN_USER, password: ADMIN_PASS })
  })
  if (!loginRes.ok) {
    const text = await loginRes.text()
    throw new Error(`[GlobalSetup] 登录失败 HTTP ${loginRes.status}（确认 PW_ADMIN_PASS 与后端一致）: ${text}`)
  }
  const { access_token: token } = await loginRes.json()
  if (!token) throw new Error('[GlobalSetup] 登录成功但没拿到 token')
  console.log('✅ [GlobalSetup] admin 登录成功')

  // 3. 商品 TK-12345 用 import_parts upsert（可重入，stock 强制回 999）
  const csv = [
    'oem,name,brand,category,stock,price,cost_price,bin_location,cross_references',
    'TK-12345,TEST PART,GENERAL,未分类,999,77.00,50.00,A-1,'
  ].join('\n')
  const formData = new FormData()
  formData.append('file', new Blob([csv], { type: 'text/csv' }), 'e2e-fixture.csv')
  const partRes = await fetch(`${API_BASE}/api/import/parts`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: formData
  })
  if (!partRes.ok) {
    const text = await partRes.text()
    throw new Error(`[GlobalSetup] 商品注入失败 HTTP ${partRes.status}: ${text}`)
  }
  console.log('✅ [GlobalSetup] 商品 TK-12345 已 upsert（stock=999）')

  // 4. 客户 elias（幂等：存在则跳过）
  const checkRes = await fetch(`${API_BASE}/api/clients`, {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  let clientExists = false
  if (checkRes.ok) {
    try {
      const data = await checkRes.json()
      const clients = Array.isArray(data) ? data : (data.items || data.data || [])
      clientExists = clients.some(c => c && c.name === 'elias')
    } catch { /* 格式不对就当不存在 */ }
  }
  if (clientExists) {
    console.log('✅ [GlobalSetup] 客户 elias 已存在，跳过')
  } else {
    const clientRes = await fetch(`${API_BASE}/api/clients`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: 'elias', phone: '+584140000000', rif_or_cedula: 'V-12345678' })
    })
    if (!clientRes.ok) {
      const text = await clientRes.text()
      throw new Error(`[GlobalSetup] 客户创建失败 HTTP ${clientRes.status}: ${text}`)
    }
    console.log('✅ [GlobalSetup] 客户 elias 已创建')
  }

  console.log('✅ [GlobalSetup] 测试数据准备完毕\n')
}
