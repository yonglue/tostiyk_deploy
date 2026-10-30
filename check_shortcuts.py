import re
import os

print("==================================================")
print(" 🔍 TOSTIYK ERP - POS 快捷键自动化检查工具 v3.1")
print("==================================================")

filepath = "PosView.vue"
if not os.path.exists(filepath):
    print(f"❌ 错误: 未找到文件 {filepath}，请在项目根目录下运行此脚本。")
    exit(1)

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# 1. 检查 handleGlobalKeydown 函数是否存在
if "handleGlobalKeydown" not in content:
    print("❌ 警告: 未在 PosView.vue 中找到 handleGlobalKeydown 函数！")
else:
    print("✅ 已成功定位全局快捷键监听函数: handleGlobalKeydown")

# 2. 提取所有监听的按键
keys_checked = re.findall(r"e\.key\s*===\s*['\"]([^'\"]+)['\"]", content)
unique_keys = sorted(list(set(keys_checked)))

print(f"\n📋 系统检测到监听的快捷键列表 ({len(unique_keys)} 个):")
for k in unique_keys:
    print(f"   • 键位: [ {k} ]")

# 3. 核心快捷键完整性校验
expected_shortcuts = ['/', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F12', 'Delete', 'Escape']
missing = [k for k in expected_shortcuts if k not in unique_keys]

print("\n--------------------------------------------------")
print(" 📊 关键快捷键健康状态自测:")
print("--------------------------------------------------")
for k in expected_shortcuts:
    if k in unique_keys:
        print(f"   [✓] 快捷键 '{k}' 已注册并生效")
    else:
        print(f"   [!] 快捷键 '{k}' 未在全局监听中找到")

if missing:
    print(f"\n⚠️ 提示: 以下关键快捷键未检测到显式监听: {missing}")
else:
    print("\n🎉 状态完美: 所有核心收银与导航快捷键均已正确绑定！")

print("==================================================\n")
