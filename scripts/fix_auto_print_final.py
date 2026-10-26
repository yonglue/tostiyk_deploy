from pathlib import Path
import re

pos_path = Path("frontend/src/components/PosView.vue")
text = pos_path.read_text(encoding="utf-8")

# 1. 找到清空购物车和 window.print() 的那段代码
old_logic = """    props.cartItems.splice(0, props.cartItems.length)


    setTimeout(() => {
      window.print()
    }, 500)"""

# 2. 替换为：先备份数据 -> 清空购物车 -> 调用自动打印
new_logic = """    // 🌟 1. 在清空前备份购物车数据用于打印
    const itemsToPrint = [...props.cartItems]
    const totalToPrint = totalUsd.value

    props.cartItems.splice(0, props.cartItems.length)

    // 🌟 2. 自动静默出票
    autoPrintReceipt({
      order_no: 'POS-' + new Date().getTime().toString().slice(-6), // 如果没有单号，用时间戳代替
      total: totalToPrint,
      items: itemsToPrint.map(item => ({
        name: item.name || item.oem || '商品',
        quantity: item.quantity,
        price: item.price
      }))
    })"""

if old_logic in text:
    text = text.replace(old_logic, new_logic)
    print("[OK] 原生打印弹窗已移除，自动出票逻辑已接入！")
else:
    print("[WARN] 没能精确匹配原生打印代码，尝试暴力替换...")
    text = re.sub(
        r'props\.cartItems\.splice\(0,\s*props\.cartItems\.length\)\s*setTimeout\(\(\)\s*=>\s*\{\s*window\.print\(\)\s*\},\s*\d+\)',
        new_logic,
        text
    )

# 3. 确保 autoPrintReceipt 函数存在
if "const autoPrintReceipt" not in text:
    print("[WARN] 没找到 autoPrintReceipt 函数，正在重新注入...")
    print_func = """
// ===== 🌟 自动打印小票逻辑 =====
const autoPrintReceipt = async (orderData) => {
  try {
    await printer.init()
    try {
      await printer.connectUSB(1)
    } catch (e) {
      console.log('首次打印，请求 USB 授权...')
      await printer.connectUSB(1)
    }
    
    const itemsText = orderData?.items?.map(item => 
      `${item.name.substring(0, 20).padEnd(20, ' ')} x${item.quantity}  $${(item.price * item.quantity).toFixed(2)}`
    ).join('\\n') || ''

    const receiptText = `
========================
       TOSTIYK ERP
========================
单号: ${orderData?.order_no || '--'}
日期: ${new Date().toLocaleString()}
------------------------
${itemsText}
------------------------
总计: $${(orderData?.total || 0).toFixed(2)}
========================
      谢谢惠顾！
      `

    await printer.print({
      type: 'text',
      text: receiptText,
      align: 'center',
      cut: true,
      feed: 3
    })
    console.log('✅ 小票打印成功')
  } catch (error) {
    console.error('❌ 打印失败:', error)
  }
}
"""
    text = text.replace("</script>", print_func + "\n</script>")

pos_path.write_text(text, encoding="utf-8")
print("[DONE] 完美闭环！")
