import hashlib
import datetime
import re

SALT = "Tostiyk_ERP_Secret_2026"

def generate_key(machine_code, days=0):
    machine_code = re.sub(r'[^A-Z0-9]', '', machine_code.upper())
    if not machine_code.startswith("TK"):
        machine_code = "TK" + machine_code
    machine_code = f"TK-{machine_code.replace('TK', '', 1)}"
    
    expire_date = "P" if days == 0 else (datetime.date.today() + datetime.timedelta(days=days)).strftime("%Y%m%d")
    
    raw = f"{machine_code}{expire_date}{SALT}".encode('utf-8')
    signature = hashlib.sha256(raw).hexdigest()[:8].upper()
    return f"{machine_code.replace('TK-', '')}-{expire_date}-{signature}"

def verify_key(input_key, current_machine_code):
    clean_input = re.sub(r'[^A-Za-z0-9\-]', '', input_key.strip())
    parts = clean_input.split('-')
    if len(parts) != 3: return False, "格式错误"
    code_part, expire_part, signature = parts
    if code_part != current_machine_code.replace("TK-", ""): return False, "机器码不匹配"
    
    raw = f"{current_machine_code}{expire_part}{SALT}".encode('utf-8')
    expected_sig = hashlib.sha256(raw).hexdigest()[:8].upper()
    if signature != expected_sig: return False, f"签名不匹配，期望 {expected_sig}"
    return True, "OK"

# 测试一下
machine = "TK-A1B2C3D4"
key = generate_key(machine, 7)
print(f"机器码: {machine}")
print(f"生成的激活码: {key}")
print(f"验证结果: {verify_key(key, machine)}")
