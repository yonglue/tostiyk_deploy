import hashlib
import datetime
import re

SALT = "Tostiyk_ERP_Secret_2026"

def generate_key(machine_code, days=0):
    # 过滤掉所有非字母数字的字符（比如空格、不可见字符）
    machine_code = re.sub(r'[^A-Z0-9]', '', machine_code.upper())
    # 补全 TK-
    if not machine_code.startswith("TK"):
        machine_code = "TK" + machine_code
    machine_code = f"TK-{machine_code.replace('TK', '', 1)}"

    expire_date = "P"
    if days > 0:
        expire_date = (datetime.date.today() + datetime.timedelta(days=days)).strftime("%Y%m%d")
    
    raw = f"{machine_code}{expire_date}{SALT}".encode('utf-8')
    signature = hashlib.sha256(raw).hexdigest()[:8].upper()
    code_part = machine_code.replace("TK-", "")
    
    return f"{code_part}-{expire_date}-{signature}"

if __name__ == "__main__":
    print("=== 终极防呆版算号器 ===")
    code = input("请输入客户的机器码: ")
    
    print("\n1. 永久授权\n2. 7天演示授权")
    choice = input("请输入序号 (1/2): ").strip()
    
    days = 7 if choice == "2" else 0
    key = generate_key(code, days)
    print(f"\n✅ 激活码: {key}")
