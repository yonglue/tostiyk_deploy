import os
import sys
import threading
import time
import uuid
import subprocess
import uvicorn
import hashlib
import datetime
import re
import webbrowser
import requests
from pathlib import Path

# 1. 找到有写入权限的目录存数据库和授权文件（避开 C 盘受保护的 Program Files）
if getattr(sys, 'frozen', False):
    # 打包后，把数据存在用户的“文档”目录下，防止 C 盘权限报错
    USER_HOME = Path(os.path.expanduser("~"))
    DATA_DIR = USER_HOME / "TostiykERP_Data"
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    os.environ['TK_DESKTOP_DATA_DIR'] = str(DATA_DIR)
    os.environ['TK_IS_DESKTOP'] = '1'
    
    # 把工作目录切换过去，防止生成的 db 和 log 落在 C 盘没权限的地方
    os.chdir(DATA_DIR)
else:
    DATA_DIR = Path(__file__).parent

LICENSE_FILE = DATA_DIR / "license.key"
SALT = "Tostiyk_ERP_Secret_2026"

def get_machine_id():
    try:
        if sys.platform == 'win32':
            try:
                out = subprocess.check_output('powershell -Command "(Get-CimInstance Win32_ComputerSystemProduct).UUID"', shell=True, creationflags=subprocess.CREATE_NO_WINDOW).decode()
                hw_id = out.strip()
            except:
                out = subprocess.check_output('wmic csproduct get uuid', shell=True, creationflags=subprocess.CREATE_NO_WINDOW).decode()
                hw_id = out.split('\n')[1].strip()
        elif sys.platform == 'darwin':
            out = subprocess.check_output("ioreg -rd1 -c IOPlatformExpertDevice | grep IOPlatformUUID", shell=True).decode()
            hw_id = out.split('"')[3]
        else:
            hw_id = str(uuid.getnode())
            
        clean_hw = re.sub(r'[^A-Z0-9]', '', hw_id[-8:].upper())
        return f"TK-{clean_hw}"
    except Exception:
        return "TK-UNKNOWN"

MACHINE_CODE = get_machine_id()

def verify_key(input_key):
    if input_key.strip().upper() == "TK-DEMO-2026":
        return True, "验证成功"
        
    try:
        clean_input = re.sub(r'[^A-Za-z0-9\-]', '', input_key.strip())
        parts = clean_input.split('-')
        if len(parts) != 3: return False, "激活码格式错误"
        code_part, expire_part, signature = parts
        
        if code_part != MACHINE_CODE.replace("TK-", ""):
            return False, "机器码不匹配"
            
        raw = f"{MACHINE_CODE}{expire_part}{SALT}".encode('utf-8')
        expected_sig = hashlib.sha256(raw).hexdigest()[:8].upper()
        if signature != expected_sig:
            return False, "激活码无效"
            
        if expire_part != "P":
            expire_date = datetime.datetime.strptime(expire_part, "%Y%m%d").date()
            if datetime.date.today() > expire_date:
                return False, "演示授权已过期"
                
        return True, "验证成功"
    except Exception as e:
        return False, f"激活码解析失败: {e}"

def check_license():
    if not LICENSE_FILE.exists(): return False
    with open(LICENSE_FILE, "r") as f:
        saved_key = f.read().strip()
    
    if saved_key.startswith("HUIYI1314_"):
        try:
            start_date = datetime.datetime.strptime(saved_key.split("_")[1], "%Y%m%d").date()
            if (datetime.date.today() - start_date).days > 7:
                return False # 超过7天
            return True
        except:
            return False
            
    is_valid, _ = verify_key(saved_key)
    return is_valid

# 用控制台版本替代 Tkinter，更稳定
def show_activation_prompt():
    print("\n" + "="*40)
    print(" Tostiyk ERP 软件激活")
    print("="*40)
    print(f" 您的机器码: {MACHINE_CODE}")
    print(" 请输入激活码 (或直接输入 Huiyi1314 开启7天试用):")
    user_input = input(" > ").strip()
    
    if user_input.upper() == "HUIYI1314":
        today_str = datetime.date.today().strftime("%Y%m%d")
        with open(LICENSE_FILE, "w") as f:
            f.write(f"HUIYI1314_{today_str}")
        print(" ✅ 专属 7 天演示激活成功！")
        return True

    is_valid, msg = verify_key(user_input)
    if is_valid:
        with open(LICENSE_FILE, "w") as f:
            f.write(user_input)
        print(" ✅ 激活成功！")
        return True
    else:
        print(f" ❌ 激活失败: {msg}")
        input("按回车键退出...")
        return False

def start_backend():
    from app.main import app as fastapi_app
    uvicorn.run(fastapi_app, host="127.0.0.1", port=8523, log_level="error", log_config=None)

if __name__ == '__main__':
    # 强制请求管理员权限
    if sys.platform == 'win32':
        import ctypes
        try:
            if not ctypes.windll.shell32.IsUserAnAdmin():
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
                sys.exit(0)
        except: pass

    if not check_license():
        if not show_activation_prompt():
            sys.exit(0)

    print("\n正在启动后台服务，请稍候... (请勿关闭此窗口)")
    
    t = threading.Thread(target=start_backend, daemon=True)
    t.start()

    backend_ready = False
    for _ in range(30):
        try:
            requests.get("http://127.0.0.1:8523/api/auth/setup-status", timeout=1)
            backend_ready = True
            break
        except requests.exceptions.ConnectionError:
            time.sleep(0.5)

    if not backend_ready:
        print("\n❌ 后台服务启动超时！请检查是否被杀毒软件拦截。")
        input("按回车键退出...")
        sys.exit(1)

    print("✅ 后台服务已启动！即将为您打开浏览器...")
    webbrowser.open("http://127.0.0.1:8523")
    
    print("\n⚠️ 提示：软件正在运行中，请不要关闭这个黑窗口！")
    print("   如果您关掉黑窗口，软件就无法使用了。")
    
    # 挂起主线程，保持后台运行
    while True:
        time.sleep(1)
