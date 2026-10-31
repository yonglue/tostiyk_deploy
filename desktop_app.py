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
import tkinter as tk
from tkinter import messagebox
from pathlib import Path

# 1. 找到有写入权限的目录存数据库和授权文件
if getattr(sys, 'frozen', False):
    USER_HOME = Path(os.path.expanduser("~"))
    DATA_DIR = USER_HOME / "TostiykERP_Data"
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    os.environ['TK_DESKTOP_DATA_DIR'] = str(DATA_DIR)
    os.environ['TK_IS_DESKTOP'] = '1'
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
                return False
            return True
        except:
            return False
            
    is_valid, _ = verify_key(saved_key)
    return is_valid

def start_backend():
    from app.main import app as fastapi_app
    uvicorn.run(fastapi_app, host="127.0.0.1", port=8523, log_level="error", log_config=None)

def show_activation_window():
    root = tk.Tk()
    root.title("Tostiyk ERP - 软件激活")
    root.geometry("450x250")
    root.eval('tk::PlaceWindow . center')
    
    tk.Label(root, text="软件未授权，请输入试用码", font=("Arial", 12), fg="red").pack(pady=10)
    
    frame_code = tk.Frame(root)
    frame_code.pack(pady=5)
    code_var = tk.StringVar(value=MACHINE_CODE)
    tk.Entry(frame_code, textvariable=code_var, state="readonly", font=("Consolas", 14), width=20, justify="center").pack(side=tk.LEFT, padx=5)
    
    def copy_code():
        root.clipboard_clear()
        root.clipboard_append(MACHINE_CODE)
        messagebox.showinfo("提示", "机器码已复制")
    tk.Button(frame_code, text="复制", command=copy_code).pack(side=tk.LEFT)

    tk.Label(root, text="请输入激活码:", font=("Arial", 11)).pack(pady=(15, 5))
    key_var = tk.StringVar()
    tk.Entry(root, textvariable=key_var, font=("Consolas", 14), width=30, justify="center").pack()

    def do_activate():
        user_input = key_var.get().strip().upper()
        
        if user_input == "HUIYI1314":
            today_str = datetime.date.today().strftime("%Y%m%d")
            with open(LICENSE_FILE, "w") as f:
                f.write(f"HUIYI1314_{today_str}")
            messagebox.showinfo("成功", "7天演示激活成功！即将进入系统。")
            root.destroy()
            return

        is_valid, msg = verify_key(user_input)
        if is_valid:
            with open(LICENSE_FILE, "w") as f:
                f.write(user_input)
            messagebox.showinfo("成功", "激活成功！即将进入系统。")
            root.destroy()
        else:
            messagebox.showerror("失败", msg)

    tk.Button(root, text="立即激活", bg="#2563eb", fg="white", font=("Arial", 11, "bold"), width=15, command=do_activate).pack(pady=20)
    root.mainloop()

if __name__ == '__main__':
    # 强制申请管理员权限
    if sys.platform == 'win32':
        import ctypes
        try:
            if not ctypes.windll.shell32.IsUserAnAdmin():
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
                sys.exit(0)
        except: pass

    # 1. 授权检查
    if not check_license():
        show_activation_window()
        if not check_license():
            sys.exit(0)

    # 2. 启动后端
    t = threading.Thread(target=start_backend, daemon=True)
    t.start()

    # 3. 等待后端就绪
    backend_ready = False
    for _ in range(30):
        try:
            requests.get("http://127.0.0.1:8523/api/auth/setup-status", timeout=1)
            backend_ready = True
            break
        except requests.exceptions.ConnectionError:
            time.sleep(0.5)

    if not backend_ready:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("启动失败", "后台服务启动超时！\n请检查是否被杀毒软件拦截，或尝试以管理员身份运行。")
        sys.exit(1)

    # 4. 打开浏览器
    webbrowser.open("http://127.0.0.1:8523")

    # 5. 显示一个“保持运行”的常驻小窗口
    root = tk.Tk()
    root.title("Tostiyk ERP - 正在运行")
    root.geometry("300x120")
    root.eval('tk::PlaceWindow . center')
    
    tk.Label(root, text="✅ ERP 已在浏览器中打开", font=("Arial", 12, "bold"), fg="green").pack(pady=15)
    tk.Label(root, text="请勿关闭此窗口，否则软件将断开。", font=("Arial", 9), fg="gray").pack(pady=5)
    
    root.mainloop()  # 挂起主线程，直到用户关掉这个窗口
