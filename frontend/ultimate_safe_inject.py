import os, re

# 涵盖刚才报告里 95% 高频词汇的翻译字典
DICT = {
    "客户": ("Cliente", "Client"), "供应商": ("Proveedor", "Supplier"),
    "库存": ("Inventario", "Inventory"), "欠款": ("Deuda", "Debt"),
    "保存": ("Guardar", "Save"), "取消": ("Cancelar", "Cancel"),
    "删除": ("Eliminar", "Delete"), "确认": ("Confirmar", "Confirm"),
    "提交": ("Enviar", "Submit"), "打印": ("Imprimir", "Print"),
    "导出": ("Exportar", "Export"), "下载": ("Descargar", "Download"),
    "编辑": ("Editar", "Edit"), "收款": ("Cobro", "Collection"),
    "收货": ("Recepción", "Receipt"), "日期": ("Fecha", "Date"),
    "名称": ("Nombre", "Name"), "数量": ("Cantidad", "Qty"),
    "单价": ("Precio", "Price"), "总计": ("Total", "Total"),
    "状态": ("Estado", "Status"), "分类": ("Categoría", "Category"),
    "电话": ("Teléfono", "Phone"), "地址": ("Dirección", "Address"),
    "备注": ("Notas", "Notes"), "类型": ("Tipo", "Type"),
    "上一页": ("Anterior", "Prev"), "下一页": ("Siguiente", "Next"),
    "跳转到": ("Ir a", "Go to"), "跳转": ("Ir", "Go"),
    "加载中...": ("Cargando...", "Loading..."),
    "未盘": ("No auditado", "Not audited"),
    "盘亏": ("Faltante", "Shortage"), "盘盈": ("Sobrante", "Surplus"),
    "实盘数量": ("Cant. Real", "Physical Count"),
    "系统库存": ("Stock Sistema", "System Stock"),
    "盈亏差异": ("Diferencia", "Difference"),
    "变动数量": ("Cant. Cambio", "Change Qty"),
    "变动类型": ("Tipo Cambio", "Change Type"),
    "历史盘点记录": ("Historial", "History"),
    "历史盘点单据": ("Docs Historial", "History Docs"),
    "盘点操作": ("Operación", "Operation"),
    "差异原因 (选填)": ("Motivo (opcional)", "Reason (optional)"),
    "导出差异表": ("Exportar diferencias", "Export diffs"),
    "库存盘点（实体清点）": ("Auditoría (Conteo)", "Audit (Count)"),
    "盘点时间 / 批次 / 经办人": ("Fecha / Lote / Op.", "Time / Batch / Op."),
    "请录入实际清点的数量。留空的商品将被系统忽略，不参与本次盘点。": ("Ingrese cantidad real. Vacíos ignorados.", "Enter actual count. Blanks ignored."),
    "系统自动汇总的盘点盈亏流水（来源：进销存系统）": ("Flujo automático de inventario", "Auto inventory ledger"),
    "按进价折算金额": ("Monto al costo", "Amount at cost"),
    "商品信息": ("Info Producto", "Product Info"),
    "管理客户资料、赊账额度以及回款核销。": ("Gestión de clientes y créditos.", "Manage clients and credits."),
    "当前未结欠款：": ("Deuda actual:", "Current debt:"),
    "店铺名称": ("Tienda", "Store Name"),
    "客户名称 (联系人)": ("Nombre (Contacto)", "Name (Contact)"),
    "客户 / 店铺": ("Cliente / Tienda", "Client / Store"),
    "该客户暂无历史交易记录": ("Sin historial de transacciones", "No transaction history"),
    "客户历史对账单": ("Estado de cuenta histórico", "Historical Statement"),
    "生成时间": ("Generado", "Generated"),
    "发生金额": ("Monto", "Amount"),
    "下载对账单": ("Descargar estado", "Download Statement"),
    "🖨️ 打印对账单": ("🖨️ Imprimir estado", "🖨️ Print Statement"),
    "TOSTIKYK ERP - 历史对账单": ("TOSTIKYK ERP - Estado de Cuenta", "TOSTIKYK ERP - Statement"),
    "对账单": ("Estado de cuenta", "Statement"),
    "报价单": ("Cotización", "Quote"),
    "有效报价": ("Cotización válida", "Valid Quote"),
    "销售员签字 / 盖章:": ("Firma / Sello Vendedor:", "Seller Signature / Stamp:"),
    "客户确认签字:": ("Firma Cliente:", "Client Signature:"),
    "总计金额 (VES):": ("Monto total (VES):", "Total amount (VES):"),
    "总计金额 (USD):": ("Monto total (USD):", "Total amount (USD):"),
    "备注：此报价单有效期 7 天，逾期价格可能随市场/汇率波动有所调整，敬请谅解。": ("Válido por 7 días. Precios sujetos a cambio.", "Valid for 7 days. Prices subject to change."),
    "🖨️ 打印 A4 报价单": ("🖨️ Imprimir Cotización A4", "🖨️ Print A4 Quote"),
    "OEM 编号": ("Código OEM", "OEM No."),
    "商品名称 / 描述": ("Nombre / Descripción", "Name / Description"),
    "客户信息": ("Info Cliente", "Client Info"),
    "报价状态:": ("Estado de cotización:", "Quote Status:"),
    "采购入库单": ("Orden de Entrada", "Inbound Order"),
    "交货人签字:": ("Firma quien entrega:", "Deliverer Signature:"),
    "收货人签字 / 盖章:": ("Firma / Sello receptor:", "Receiver Signature / Stamp:"),
    "供应商信息": ("Info Proveedor", "Supplier Info"),
    "成功导入": ("Importado con éxito", "Imported successfully"),
    "系统每 24 小时自动备份一次，防止数据丢失": ("Respaldo automático cada 24h", "Auto backup every 24h"),
    "知道了": ("Entendido", "Got it"),
    "错误明细（最多显示前 5 条）:": ("Detalles del error (máx. 5):", "Error details (max 5):"),
    "目前保留最近 30 天的备份文件": ("Se conservan 30 días de respaldo", "Retains 30 days of backup"),
    "跳过 / 失败": ("Omitidos / Fallidos", "Skipped / Failed"),
    "导入结果报告": ("Reporte de importación", "Import Report"),
    "配置系统基础信息、执行自动备份策略、管理数据导入导出以及数据库底层优化。": ("Configurar sistema, respaldos y optimización.", "Configure system, backups, and optimization."),
    "自动备份系统": ("Sistema de respaldo", "Auto Backup System"),
    "📥 下载": ("📥 Descargar", "📥 Download"),
    "暂无备份记录": ("Sin copias de seguridad", "No backups"),
    "系统运维与数据备份": ("Mantenimiento y Respaldo", "Maintenance & Backup"),
    "正在上传并解析数据": ("Subiendo y analizando datos", "Uploading and parsing data"),
    "返回顶部": ("Volver arriba", "Back to Top"),
    "折叠/展开侧边栏": ("Colapsar/Expandir", "Collapse/Expand sidebar"),
    "库存产品": ("Productos en stock", "Products in Stock"),
    "产品详情": ("Detalles del producto", "Product Details"),
    "售价": ("Precio de Venta", "Sale Price"),
    "暂无历史变动": ("Sin cambios históricos", "No historical changes"),
    "没有找到相关产品": ("Sin productos relacionados", "No products found"),
    "进货价 (USD)": ("Costo (USD)", "Cost Price (USD)"),
    "搜索 OEM 或 配件名称...": ("Buscar OEM o nombre...", "Search OEM or name..."),
    "库存变动历史": ("Historial de inventario", "Inventory History"),
    "货架位置": ("Ubicación", "Location"),
    "库存数量": ("Cantidad en stock", "Stock Quantity"),
    "零售价 (USD)": ("Precio Venta (USD)", "Retail Price (USD)"),
    "全渠道汽车配件商业管理系统。": ("Sistema ERP Multimoneda para Autopartes.", "Multi-currency Auto Parts ERP."),
    "库存、收银、财务，一站式掌控。": ("Inventario, Caja y Finanzas en un solo lugar.", "Inventory, POS, and Finance in one place."),
    "这是系统的首次启动，请设置您的超级管理员账号。": ("Primer inicio. Configure su super administrador.", "First start. Setup super admin."),
    "🚀 欢迎使用": ("🚀 Bienvenido", "🚀 Welcome"),
    "默认使用 admin": ("Usar admin por defecto", "Default use admin"),
    "正在检测系统状态...": ("Comprobando estado...", "Checking status..."),
    "请输入您的管理员凭证进入系统": ("Ingrese sus credenciales", "Enter your credentials"),
    "请输入强密码": ("Ingrese contraseña fuerte", "Enter strong password"),
    "设置密码": ("Configurar contraseña", "Set Password"),
    "密码": ("Contraseña", "Password"),
    "管理员账号": ("Usuario Admin", "Admin Account"),
    "安全登录": ("Iniciar Sesión", "Secure Login"),
    "暂无历史报价记录": ("Sin cotizaciones históricas", "No historical quotes"),
    "📝 确认全单挂账 (Fiado)": ("📝 Confirmar fiado completo", "📝 Confirm Entire Credit"),
    "退出界面": ("Salir", "Exit"),
    "载入 ↵": ("Cargar ↵", "Load ↵"),
    "📂 载入历史报价单": ("📂 Cargar cotización", "📂 Load Quote"),
    "* 挂账前请先在顶部搜索并选择客户": ("* Busque y seleccione cliente antes de fiar", "* Search and select client before crediting"),
    "保存报价": ("Guardar Cotización", "Save Quote"),
    "📂 载入历史": ("📂 Cargar historial", "📂 Load History"),
    "加载中...": ("Cargando...", "Loading..."),
    "搜索": ("Buscar", "Search"),
    "商品库存": ("Stock del producto", "Product Stock"),
    "选择": ("Seleccionar", "Select"),
    "客户档案": ("Directorio de clientes", "Client Directory"),
    "搜索商品 OEM/名称，或客户姓名...": ("Buscar producto o cliente...", "Search product or client..."),
    "全局搜索 (Ctrl + K)": ("Búsqueda global (Ctrl + K)", "Global search (Ctrl + K)"),
    "请输入商品 OEM、名称或客户姓名开始搜索...": ("Ingrese OEM o nombre...", "Enter OEM or name..."),
    "今日暂无动态": ("Sin actividad hoy", "No activity today"),
    "应收欠款": ("Cuentas por cobrar", "Receivables"),
    "预估销售利润": ("Beneficio estimado", "Estimated Profit"),
    "库存总资产 (USD)": ("Valor del inventario (USD)", "Total Inventory (USD)"),
    "最近动态": ("Actividad reciente", "Recent Activity"),
    "TOSTIYK 驾驶舱": ("Cabina TOSTIYK", "TOSTIYK Cockpit"),
    "查看全部": ("Ver todo", "View All"),
    "库存预警": ("Alerta de stock", "Stock Alert"),
    "潜在销售额": ("Ventas potenciales", "Potential Sales"),
    "暂无历史记录": ("Sin historial", "No history"),
    "当前欠款": ("Deuda actual", "Current debt"),
    "客户详情": ("Detalles del cliente", "Client Details"),
    "极速收款": ("Cobro rápido", "Quick Collection"),
    "搜索客户名称、店铺...": ("Buscar cliente o tienda...", "Search client or store..."),
    "历史交易记录": ("Historial de transacciones", "Transaction History"),
    "信用额度上限": ("Límite de crédito", "Credit Limit"),
    "客户总应收欠款": ("Total por cobrar", "Total Receivables"),
    "单据详情": ("Detalles del documento", "Document Details"),
    "总金额": ("Monto total", "Total Amount"),
    "暂无流水记录": ("Sin transacciones", "No transactions"),
    "时间": ("Hora", "Time"),
    "客户/供应商": ("Cliente/Proveedor", "Client/Supplier"),
    "进销存流水": ("Movimientos y Cuentas", "Transactions"),
    "收款金额 (USD)": ("Monto a cobrar (USD)", "Amount to Collect (USD)"),
    "全额": ("Monto total", "Full amount"),
    "⚠️ 收款金额不能大于当前欠款": ("⚠️ El monto no puede exceder la deuda", "⚠️ Amount cannot exceed debt"),
    "确认收款": ("Confirmar cobro", "Confirm Collection"),
    "当前欠款:": ("Deuda actual:", "Current debt:"),
    "小票预览 (80mm)": ("Vista previa de recibo (80mm)", "Receipt Preview (80mm)"),
    "关闭": ("Cerrar", "Close"),
    "打印": ("Imprimir", "Print"),
    "查看所有历史进销存单据、出入库明细及退款记录。": ("Ver todos los documentos y devoluciones.", "View all documents and refunds."),
    "管理汽车配件的入库、出库、定价及多图档案。": ("Gestión de entradas, salidas y precios.", "Manage stock in/out, pricing, and photos."),
    "近 7 天销售趋势": ("Tendencia de ventas 7 días", "7-day Sales Trend"),
    "📄 对账单": ("📄 Estado de cuenta", "📄 Statement"),
    "显示小票": ("Mostrar recibo", "Show Receipt"),
    "件": ("unidades", "items"),
    "项": ("ítems", "items"),
    "个商品": ("Productos", "Products"),
    "个客户": ("Clientes", "Clients"),
    "盘亏 (资产损失)": ("Faltante (Pérdida)", "Shortage (Loss)"),
    "盘盈 (资产增加)": ("Sobrante (Ganancia)", "Surplus (Gain)"),
    "盘亏 (OUT)": ("Faltante (OUT)", "Shortage (OUT)"),
    "盘盈 (IN)": ("Sobrante (IN)", "Surplus (IN)"),
    "📭 没有找到符合条件的商品": ("📭 Sin productos coincidentes", "📭 No matching products"),
    "📭 暂无历史盘点记录": ("📭 Sin historial de inventario", "📭 No inventory history"),
    "例如：破损、丢失...": ("Ej: Dañado, perdido...", "Ex: Damaged, lost..."),
    "🔄 刷新记录": ("🔄 Actualizar", "🔄 Refresh Records"),
    "单号": ("Nro.", "No."),
    "类型": ("Tipo", "Type"),
    "操作": ("Acción", "Action"),
    "状态:": ("Estado:", "Status:"),
    "日期:": ("Fecha:", "Date:"),
    "名称:": ("Nombre:", "Name:"),
    "单号:": ("Nro:", "No:"),
    "总计金额 (VES):": ("Monto total (VES):", "Total (VES):"),
}

# 生成安全的三元表达式
def get_expr(zh):
    es, en = DICT[zh]
    zh_esc = zh.replace("'", "\\'")
    es_esc = es.replace("'", "\\'")
    en_esc = en.replace("'", "\\'")
    return f"{{{{ isZh ? '{zh_esc}' : isEs ? '{es_esc}' : '{en_esc}' }}}}"

modified_files = 0
total_replaced = 0

# 按长度倒序，防止短词覆盖长词
sorted_keys = sorted(DICT.keys(), key=len, reverse=True)

for root, dirs, files in os.walk('src'):
    for file in files:
        if file.endswith('.vue'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            orig = content
            
            for zh in sorted_keys:
                expr = get_expr(zh)
                
                # 1. 替换纯文本标签 >中文<
                # 注意：排除 {{ }} 里面嵌套的
                pattern_text = re.compile(r'>\s*(' + re.escape(zh) + r')\s*<')
                content = pattern_text.sub('>' + expr + '<', content)
                
                # 2. 替换属性 placeholder="中文"
                pattern_attr = re.compile(r'(placeholder|title|label)="' + re.escape(zh) + r'"')
                content = pattern_attr.sub(r'\1="' + expr + '"', content)

            if content != orig:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                modified_files += 1
                print(f"✅ 已注入翻译: {filepath}")

print(f"\n🎉 大功告成！共修改了 {modified_files} 个 Vue 文件。")
print("👉 请去浏览器按 Cmd+Shift+R 强刷，然后切换语言试试！")
