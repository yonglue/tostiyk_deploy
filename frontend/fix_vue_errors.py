import os, re

# 修复因为正则替换导致嵌套的 {{ }} 问题
def fix_nested_expressions(text):
    # 1. 修复类似 {{ isZh ? '{{ isZh ? 'xxx' : ... }}' : ... }} 的严重嵌套
    # 我们直接暴力提取最里层的内容
    pattern = re.compile(r"\{\{\s*isZh\s*\?\s*'\{\{\s*isZh\s*\?\s*'(.*?)'\s*:\s*isEs\s*\?\s*'(.*?)'\s*:\s*'(.*?)'\s*\}\}'\s*:\s*isEs\s*\?\s*'\{\{\s*isZh\s*\?\s*'(.*?)'\s*:\s*isEs\s*\?\s*'(.*?)'\s*:\s*'(.*?)'\s*\}\}'\s*:\s*'\{\{\s*isZh\s*\?\s*'(.*?)'\s*:\s*isEs\s*\?\s*'(.*?)'\s*:\s*'(.*?)'\s*\}\}'\s*\}\}")
    text = pattern.sub(r"{{ isZh ? '\1' : isEs ? '\4' : '\7' }}", text)
    
    # 2. 修复语言下拉框特有的乱码
    text = text.replace("{{ isZh ? '{{ isZh ? '🇨🇳 中文' : isEs ? '🇨🇳 中文' : '🇨🇳 中文' }}' : isEs ? '{{ isZh ? '🇨🇳 中文' : isEs ? '🇨🇳 中文' : '🇨🇳 中文' }}' : '{{ isZh ? '🇨🇳 中文' : isEs ? '🇨🇳 中文' : '🇨🇳 中文' }}' }}", "🇨🇳 中文")
    text = text.replace("{{ isZh ? '🇨🇳 中文' : isEs ? '🇨🇳 中文' : '🇨🇳 中文' }}", "🇨🇳 中文")
    
    # 3. 清理其他可能因为转义导致的报错
    # 比如 {{ isZh ? '{{' : ... }}
    text = text.replace("{{ isZh ? '{{", "{{ isZh ? '")
    
    return text

modified = 0
for root, dirs, files in os.walk('src'):
    for file in files:
        if file.endswith('.vue') or file.endswith('.js'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content = fix_nested_expressions(content)
            
            # 额外修复：确保 App.vue 的 option 干净
            if file == 'App.vue':
                new_content = re.sub(r"<option value=\"zh\">.*?</option>", "<option value=\"zh\">🇨🇳 中文</option>", new_content)
                new_content = re.sub(r"<option value=\"es\">.*?</option>", "<option value=\"es\">🇪🇸 ES</option>", new_content)
                new_content = re.sub(r"<option value=\"en\">.*?</option>", "<option value=\"en\">🇺🇸 EN</option>", new_content)

            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                modified += 1
                print(f"✅ 修复了 {filepath}")

print(f"🎉 修复完成！共处理了 {modified} 个文件。请刷新浏览器查看。")
