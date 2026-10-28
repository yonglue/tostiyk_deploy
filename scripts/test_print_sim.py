import sys

# 模拟 42 字符满宽与左右对齐逻辑
LINE_WIDTH = 42
LEFT_PAD = "  "

def print_divider(char = "-"):
    return LEFT_PAD + char * LINE_WIDTH

def print_row(left_text, right_text):
    r_str = str(right_text or '')
    l_str = str(left_text or '')
    if len(r_str) >= LINE_WIDTH:
        r_str = r_str[:LINE_WIDTH]
    max_left_len = LINE_WIDTH - len(r_str) - 1
    if len(l_str) > max_left_len:
        l_str = l_str[:max_left_len]
    spaces_count = LINE_WIDTH - len(l_str) - len(r_str)
    spaces = " " * (spaces_count if spaces_count > 0 else 0)
    return f"{LEFT_PAD}{l_str}{spaces}{r_str}"

def center_text(str_val):
    s = str(str_val or '').strip()
    if not s:
        return ""
    res = []
    while len(s) > 0:
        chunk = s[:LINE_WIDTH]
        s = s[LINE_WIDTH:]
        left_pad = max(0, (LINE_WIDTH - len(chunk)) // 2)
        res.append(f"{LEFT_PAD}{' ' * left_pad}{chunk}")
    return "\n".join(res)

def left_line(str_val):
    return f"{LEFT_PAD}{str_val}"

# 模拟全量真实业务数据测试（包含长商品名、客户信息、全套财务和支付方式）
mock_data = {
    "companyName": "MUNDO REPUESTOS C.A",
    "companyRif": "J-307219955",
    "companyAddress": "Valencia, Carabobo, Venezuela",
    "companyPhone": "+58 412-0000000",
    "order_no": "TK-9999-8888",
    "date": "2026-10-27 12:45:00",
    "client_name": "TRANSPORTES Y REPUESTOS CARABOBO S.A.",
    "client_rif": "J-50123456-7",
    "operator": "Elias",
    "tasa": 887.00,
    "items": [
        {"name": "ARANDELA TAPA VALVULA/100PC TOYOTA HILUX 2.7 3RZ", "quantity": 2, "price": 35.50, "total": 71.00},
        {"name": "KIT DE TIEMPO COMPLETO COROLA 1.8 1ZZ", "quantity": 1, "price": 145.00, "total": 145.00},
        {"name": "FILTRO DE ACEITE ORIGINAL", "quantity": 4, "price": 8.25, "total": 33.00}
    ],
    "exento": 0.00,
    "iva": 39.04,
    "total_usd": 249.00,
    "total_bs": 22086.30,
    "payment_method": "PAGO MOVIL / BANESCO"
}

print("="*60)
print("📌 【Tostiyk ERP 屏幕端小票排版全量模拟器】 (42列满宽)")
print("="*60 + "\n")

# 开始模拟渲染
output = []
output.append("\n[HARDWARE: 预热走纸 4 行 / 硬件跳过切刀盲区 ESC J 20]\n")
output.append(center_text(mock_data["companyName"]))
output.append(center_text(f"RIF: {mock_data['companyRif']}"))
output.append(center_text(mock_data["companyAddress"]))
output.append(center_text(f"TEL: {mock_data['companyPhone']}"))
output.append(print_divider("="))

output.append(left_line(f"Factura:  {mock_data['order_no']}"))
output.append(left_line(f"Fecha:    {mock_data['date']}"))
output.append(left_line(f"Cliente:  {mock_data['client_name']}"))
output.append(left_line(f"CI/RIF:   {mock_data['client_rif']}"))
output.append(left_line(f"Cajero:   {mock_data['operator']}"))
output.append(left_line(f"Tasa Ref: Bs. {mock_data['tasa']:.2f} / USD"))
output.append(print_divider("-"))

total_items_count = 0
for item in mock_data["items"]:
    qty = item["quantity"]
    price = item["price"]
    subtotal = item["total"]
    total_items_count += qty
    
    item_name = item["name"]
    first_line_max = LINE_WIDTH
    sub_line_max = LINE_WIDTH - 2
    
    if len(item_name) <= first_line_max:
        output.append(left_line(item_name))
    else:
        output.append(left_line(item_name[:first_line_max]))
        item_name = item_name[first_line_max:]
        while len(item_name) > 0:
            output.append(left_line("  " + item_name[:sub_line_max]))
            item_name = item_name[sub_line_max:]
            
    output.append(print_row(f"  {qty} x ${price:.2f}", f"${subtotal:.2f}"))

output.append(print_divider("-"))
output.append(print_row("CANT. PRODUCTOS:", f"{total_items_count}"))
output.append(print_divider("-"))

output.append(print_row("EXENTO", f"${mock_data['exento']:.2f}"))
output.append(print_row("BI G16,00%", f"${mock_data['total_usd']:.2f}"))
output.append(print_row("IVA (16%)", f"${mock_data['iva']:.2f}"))
output.append(print_divider("-"))

output.append("[BOLD START]")
output.append(print_row("TOTAL USD", f"${mock_data['total_usd']:.2f}"))
output.append(print_row("TOTAL BS", f"Bs.{mock_data['total_bs']:.2f}"))
output.append("[BOLD END]")
output.append(print_divider("="))

output.append(center_text("Forma de Pago:"))
output.append(center_text(mock_data["payment_method"]))
output.append("")
output.append(center_text("Gracias por su compra!"))
output.append("\n[HARDWARE: 切纸指令 & 尾部进纸]\n")

print("\n".join(output))
print("="*60)
print("✅ 屏幕模拟测试完成！请核对上方排版是否完美居中、超长商品名是否正确缩进换行、所有字段是否完整。")
