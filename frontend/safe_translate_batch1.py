import os

# 针对文件的具体替换规则（精准匹配，绝不误伤语法）
replacements = {
    'src/components/Sidebar.vue': [
        ('>客户<', '>{{ isZh ? \'客户\' : isEs ? \'Clientes\' : \'Clients\' }}<'),
        ('>产品<', '>{{ isZh ? \'产品\' : isEs ? \'Productos\' : \'Products\' }}<'),
        ('>流水<', '>{{ isZh ? \'流水\' : isEs ? \'Movimientos\' : \'Transactions\' }}<'),
        ('>首页<', '>{{ isZh ? \'首页\' : isEs ? \'Inicio\' : \'Home\' }}<'),
        ('>我的<', '>{{ isZh ? \'我的\' : isEs ? \'Mi Perfil\' : \'Profile\' }}<'),
        ('设置', '{{ isZh ? \'设置\' : isEs ? \'Ajustes\' : \'Settings\' }}'), # 可能是纯文本
    ],
    'src/components/ConfirmDialog.vue': [
        ('>确认<', '>{{ isZh ? \'确认\' : isEs ? \'Confirmar\' : \'Confirm\' }}<'),
        ('>取消<', '>{{ isZh ? \'取消\' : isEs ? \'Cancelar\' : \'Cancel\' }}<'),
    ],
    'src/components/GlobalNoticeModal.vue': [
        ('>提示<', '>{{ isZh ? \'提示\' : isEs ? \'Aviso\' : \'Notice\' }}<'),
        ('>知道了<', '>{{ isZh ? \'知道了\' : isEs ? \'Entendido\' : \'Got it\' }}<'),
    ],
    'src/components/SideDrawer.vue': [
        ('>关闭<', '>{{ isZh ? \'关闭\' : isEs ? \'Cerrar\' : \'Close\' }}<'),
    ],
    'src/components/TrendChart.vue': [
        ('>近 7 天销售趋势<', '>{{ isZh ? \'近 7 天销售趋势\' : isEs ? \'Tendencia 7 días\' : \'7-Day Trend\' }}<'),
    ]
}

for filepath, rules in replacements.items():
    if not os.path.exists(filepath):
        print(f"⚠️ 找不到文件: {filepath}")
        continue
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    orig = content
    for old, new in rules:
        if old in content:
            content = content.replace(old, new)
            
    if content != orig:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 成功翻译: {filepath}")
    else:
        print(f"⏭️ 跳过（未匹配到中文）: {filepath}")
