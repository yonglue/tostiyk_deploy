import hashlib
import datetime

SALT = "Tostiyk_ERP_Secret_2026"

def generate_key(machine_code, days=0):
    expire_date = "P" # P 代表 Permanent (永久)
    if days > 0:
        expire_date = (datetime.date.today() + datetime.timedelta(days=days)).strftime("%Y%m%d")
    
    raw = f"{machine_code}{expire_date}{SALT}".encode('utf-8')
    signature = hashlib.sha256(raw).hexdigest()[:8].upper()
    code_part = machine_code.replace("TK-", "")
    return f"{code_part}-{expire_date}-{signature}"

if __name__ == "__main__":
    print("=== Tostiyk ERP 激活码生成器 ===")
    code = input("请输入客户的机器码 (例如 TK-A1B2C3D4): ").strip().upper()
    
    print("\n请选择授权类型：")
    print("1. 永久授权")
    print("2. 7天演示授权")
    print("3. 30天演示授权")
    print("4. 自定义天数")
    choice = input("请输入序号 (1-4): ").strip()
    
    days = 0
    if choice == "2": days = 7
    elif choice == "3": days = 30
    elif choice == "4": days = int(input("请输入天数: "))
    
    key = generate_key(code, days)
    
    print(f"\n✅ 客户的激活码是: {key}")
    if days > 0:
        print(f"⏳ 该代码将于 {days} 天后过期。")
    else:
        print("♾️ 该代码为永久授权。")
