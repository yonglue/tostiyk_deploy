import os

def replace_in_file(filepath, old, new):
    if not os.path.exists(filepath): return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    if old in content:
        content = content.replace(old, new)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 修复: {filepath}")

# 1. 修复 App.vue 的 title 属性
replace_in_file('src/App.vue', 
    'title="{{ isZh ? \'折叠/展开侧边栏\' : isEs ? \'Colapsar/Expandir\' : \'Collapse/Expand sidebar\' }}"',
    ':title="isZh ? \'折叠/展开侧边栏\' : isEs ? \'Colapsar/Expandir\' : \'Collapse/Expand sidebar\'"'
)

# 2. 修复 ClientsView.vue 的 title 属性
replace_in_file('src/components/ClientsView.vue',
    'title="{{ isZh ? \'下载对账单\' : isEs ? \'Descargar estado\' : \'Download Statement\' }}"',
    ':title="isZh ? \'下载对账单\' : isEs ? \'Descargar estado\' : \'Download Statement\'"'
)

# 3. 修复 ClientsView.vue 的保存按钮
replace_in_file('src/components/ClientsView.vue',
    "{{ isSavingEdit ? '保存中...' : '保存修改' }}",
    "{{ isSavingEdit ? (isZh ? '保存中...' : isEs ? 'Guardando...' : 'Saving...') : (isZh ? '保存修改' : isEs ? 'Guardar cambios' : 'Save changes') }}"
)

# 4. 修复 ClientsView.vue 的分页文字
replace_in_file('src/components/ClientsView.vue',
    '显示第 <strong class="text-slate-800 dark:text-slate-200">{{ (currentPage - 1) * pageSize + 1 }}</strong> 到 <strong class="text-slate-800 dark:text-slate-200">{{ Math.min(currentPage * pageSize, filteredClients.length) }}</strong> 条，共 <strong class="text-slate-800 dark:text-slate-200">{{ filteredClients.length }}</strong>{{ isZh ? \'个客户\' : isEs ? \'Clientes\' : \'Clients\' }}</span>',
    '{{ isZh ? \'显示第\' : isEs ? \'Mostrando\' : \'Showing\' }} <strong class="text-slate-800 dark:text-slate-200">{{ (currentPage - 1) * pageSize + 1 }}</strong> {{ isZh ? \'到\' : isEs ? \'a\' : \'to\' }} <strong class="text-slate-800 dark:text-slate-200">{{ Math.min(currentPage * pageSize, filteredClients.length) }}</strong> {{ isZh ? \'条，共\' : isEs ? \'de\' : \'of\' }} <strong class="text-slate-800 dark:text-slate-200">{{ filteredClients.length }}</strong>{{ isZh ? \'个客户\' : isEs ? \'Clientes\' : \'Clients\' }}</span>'
)

# 5. 修复 ClientsView.vue 的 "无"
replace_in_file('src/components/ClientsView.vue',
    "{{ currentClient?.rif_or_cedula || '无' }}",
    "{{ currentClient?.rif_or_cedula || (isZh ? '无' : isEs ? 'Ninguno' : 'None') }}"
)

# 6. 修复 AuditLogsView.vue 的分页文字
replace_in_file('src/components/AuditLogsView.vue',
    '显示第 <strong class="text-slate-800 dark:text-slate-200">{{ (currentPage - 1) * pageSize + 1 }}</strong> 到 <strong class="text-slate-800 dark:text-slate-200">{{ Math.min(currentPage * pageSize, filteredLogs.length) }}</strong> 条，共 <strong class="text-slate-800 dark:text-slate-200">{{ filteredLogs.length }}</strong> 条记录',
    '{{ isZh ? \'显示第\' : isEs ? \'Mostrando\' : \'Showing\' }} <strong class="text-slate-800 dark:text-slate-200">{{ (currentPage - 1) * pageSize + 1 }}</strong> {{ isZh ? \'到\' : isEs ? \'a\' : \'to\' }} <strong class="text-slate-800 dark:text-slate-200">{{ Math.min(currentPage * pageSize, filteredLogs.length) }}</strong> {{ isZh ? \'条，共\' : isEs ? \'de\' : \'of\' }} <strong class="text-slate-800 dark:text-slate-200">{{ filteredLogs.length }}</strong> {{ isZh ? \'条记录\' : isEs ? \'registros\' : \'records\' }}'
)
