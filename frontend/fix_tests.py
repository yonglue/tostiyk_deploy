import os, re

# 1. 修复 inventory-audit.spec.js（强制切回中文 + 放宽正则）
p = 'e2e/inventory-audit.spec.js'
if os.path.exists(p):
    s = open(p, encoding='utf-8').read()
    # 确保登录后，把语言重置为中文（如果你的 useI18n 是用 localStorage 存的）
    s = s.replace("await expect(page.locator('nav')).toBeVisible({ timeout: 10000 })", 
                  "await expect(page.locator('nav')).toBeVisible({ timeout: 10000 })\n  await page.evaluate(() => localStorage.setItem('tostiyk_lang', 'zh'))")
    # 把按钮名称的正则放宽，兼容中/英/西
    s = s.replace("page.getByRole('button', { name: /历史盘点记录/ })", 
                  "page.getByRole('button', { name: /历史盘点记录|Historial/i })")
    open(p, 'w', encoding='utf-8').write(s)
    print("✅ 修复 inventory-audit.spec.js")

# 2. 修复 mobile-app.spec.js（修复断言里错误的西语单词）
p = 'e2e/mobile-app.spec.js'
if os.path.exists(p):
    s = open(p, encoding='utf-8').read()
    # 将错误的 Deuda Total 改成正确的 Cuentas por cobrar
    s = s.replace("/客户总应收欠款|Deuda Total|Total Debt/", 
                  "/客户总应收欠款|应收欠款|Cuentas por cobrar|Receivables/i")
    open(p, 'w', encoding='utf-8').write(s)
    print("✅ 修复 mobile-app.spec.js")

# 3. 修复 pos-quote.spec.js（修复显示小票的西语）
p = 'e2e/pos-quote.spec.js'
if os.path.exists(p):
    s = open(p, encoding='utf-8').read()
    # 将错误的 Vista Previa 改成我们实际用的 Mostrar recibo
    s = s.replace("/显示小票|Vista Previa/i", 
                  "/显示小票|Mostrar recibo|Show Receipt/i")
    open(p, 'w', encoding='utf-8').write(s)
    print("✅ 修复 pos-quote.spec.js")

print("🎉 测试脚本修复完毕！")
