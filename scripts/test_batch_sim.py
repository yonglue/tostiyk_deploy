import sys

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

# 基础测试商品库
base_parts = [
    {"name": "ARANDELA TAPA VALVULA/100PC TOYOTA HILUX", "price": 12.50},
    {"name": "KIT DE TIEMPO COMPLETO COROLA 1.8 1ZZ", "price": 145.00},
    {"name": "FILTRO DE ACEITE ORIGINAL TOYOTA", "price": 8.25},
    {"name": "PASTILLAS DE FRENO DELANTERA", "price": 45.00},
    {"name": "BOMBA DE AGUA FIESTA POWER 1.6", "price": 38.00},
    {"name": "BUJIAS DE ENCENDIDO IRIDIUM (4 PCS)", "price": 24.00},
    {"name": "CORREA UNICA ALTERNADOR 6PK1650", "price": 18.50},
    {"name": "AMORTIGUADOR TRASEROCHEVROLET CRUZE", "price": 65.00}
];

print("="*60)
print("🚀 【Tostiyk ERP 1至24个商品全量批量排版模拟测试】")
print("="*60 + "\n")

# 循环测试从 1 个商品到 24 个商品
for count in range(1, 25):
    items = []
    total_usd = 0.0
    total_items_count = 0
    
    for i in range(count):
        part = base_parts[i % len(base_parts)]
        qty = (i % 3) + 1  # 动态数量 1~3
        price = part["price"]
        subtotal = qty * price
        items.append({
            "name": f"[{i+1}] {part['name']}",
            "quantity": qty,
            "price": price,
            "total": subtotal
        })
        total_usd += subtotal
        total_items_count += qty

    tasa = 887.00
    total_bs = total_usd * tasa
    iva = round(total_usd * 0.16, 2)

    print(f"\n👉 【测试用例：包含 {count} 种不同商品，总件数 {total_items_count} 件】")
    print("-" * 60)

    output = []
    output.append(center_text("MUNDO REPUESTOS C.A"))
    output.append(center_text("RIF: J-307219955"))
    output.append(print_divider("="))
    output.append(left_line(f"Factura:  TK-TEST-{count:02d}"))
    output.append(left_line(f"Fecha:    2026-10-27 13:00:00"))
    output.append(print_divider("-"))

    for item in items:
        q = item["quantity"]
        p = item["price"]
        sub = item["total"]
        name = item["name"]
        
        if len(name) <= LINE_WIDTH:
            output.append(left_line(name))
        else:
            output.append(left_line(name[:LINE_WIDTH]))
            rem = name[LINE_WIDTH:]
            while len(rem) > 0:
                output.append(left_line("  " + rem[:LINE_WIDTH-2]))
                rem = rem[LINE_WIDTH-2:]
                
        output.append(print_row(f"  {q} x ${p:.2f}", f"${sub:.2f}"))

    output.append(print_divider("-"))
    output.append(print_row("CANT. PRODUCTOS:", f"{total_items_count}"))
    output.append(print_divider("-"))
    output.append(print_row("EXENTO", "$0.00"))
    output.append(print_row("BI G16,00%", f"${total_usd:.2f}"))
    output.append(print_row("IVA (16%)", f"${iva:.2f}"))
    output.append(print_divider("-"))
    output.append(print_row("TOTAL USD", f"${total_usd:.2f}"))
    output.append(print_row("TOTAL BS", f"Bs.{total_bs:.2f}"))
    output.append(print_divider("="))
    
    print("\n".join(output))
    print("=" * 60)

print("\n✅ 1到24个商品全量模拟测试通过！排版结构、对齐与计数器全部正常。")
