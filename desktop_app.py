import os
import sys
import threading
import time
import uuid
import subprocess
import webview
import uvicorn
import hashlib
import tkinter as tk
from tkinter import messagebox
import datetime
import re
import requests

if getattr(sys, 'frozen', False):
    os.environ['TK_IS_DESKTOP'] = '1'

SALT = "Tostiyk_ERP_Secret_2026"

def get_machine_id():
    try:
        if sys.platform == 'win32':
            try:
                # 优先用 PowerShell (兼容 Win11)
                out = subprocess.check_output('powershell -Command "(Get-CimInstance Win32_ComputerSystemProduct).UUID"', shell=True).decode()
                hw_id = out.strip()
            except:
                # 回退到 wmic (兼容旧版)
                out = subprocess.check_output('wmic csproduct get uuid', shell=True).decode()
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
LICENSE_FILE = "license.key"

def verify_key(input_key):
    # ==========================================
    # 🌟 万能后门：只要输入这个码，无条件通过！
    # ==========================================
    if input_key.strip().upper() == "TK-DEMO-2026":
        return True, "验证成功"
        
    try:
        clean_input = re.sub(r'[^A-Za-z0-9\-]', '', input_key.strip())
        parts = clean_input.split('-')
        if len(parts) != 3: return False, "激活码格式错误"
        
        code_part, expire_part, signature = parts
        
        if code_part != MACHINE_CODE.replace("TK-", ""):
            return False, f"激活码与本机机器码不匹配 (当前机器码: {MACHINE_CODE})"
            
        raw = f"{MACHINE_CODE}{expire_part}{SALT}".encode('utf-8')
        expected_sig = hashlib.sha256(raw).hexdigest()[:8].upper()
        if signature != expected_sig:
            return False, f"激活码无效或已被篡改 (期望签名: {expected_sig})"
            
        if expire_part != "P":
            try:
                expire_date = datetime.datetime.strptime(expire_part, "%Y%m%d").date()
                if datetime.date.today() > expire_date:
                    return False, f"演示授权已于 {expire_date} 过期"
            except ValueError:
                return False, "激活码日期格式错误"
                
        return True, "验证成功"
    except Exception as e:
        return False, f"激活码解析失败: {e}"

def check_license():
    if not os.path.exists(LICENSE_FILE): 
        return False
    with open(LICENSE_FILE, "r") as f:
        saved_key = f.read().strip()
    
    # 处理 Huiyi1314 专属 7 天记录
    if saved_key.startswith("HUIYI1314_"):
        try:
            start_date_str = saved_key.split("_")[1]
            start_date = datetime.datetime.strptime(start_date_str, "%Y%m%d").date()
            if (datetime.date.today() - start_date).days > 7:
                return False # 超过7天
            return True # 有效期内
        except Exception:
            return False
            
    is_valid, _ = verify_key(saved_key)
    return is_valid

def show_activation_window():
    root = tk.Tk()
    root.title("Tostiyk ERP - 软件激活")
    root.geometry("450x250")
    root.eval('tk::PlaceWindow . center')
    
    tk.Label(root, text="软件未授权或授权已过期", font=("Arial", 12), fg="red").pack(pady=10)
    
    frame_code = tk.Frame(root)
    frame_code.pack(pady=5)
    code_var = tk.StringVar(value=MACHINE_CODE)
    tk.Entry(frame_code, textvariable=code_var, state="readonly", font=("Consolas", 14), width=20, justify="center").pack(side=tk.LEFT, padx=5)
    
    def copy_code():
        root.clipboard_clear()
        root.clipboard_append(MACHINE_CODE)
        messagebox.showinfo("提示", "机器码已复制到剪贴板！")
    tk.Button(frame_code, text="复制", command=copy_code).pack(side=tk.LEFT)

    tk.Label(root, text="请输入激活码:", font=("Arial", 11)).pack(pady=(15, 5))
    key_var = tk.StringVar()
    tk.Entry(root, textvariable=key_var, font=("Consolas", 14), width=30, justify="center").pack()

    def do_activate():
        user_input = key_var.get().strip().upper()
        
        # 处理专属 7 天密码
        if user_input == "HUIYI1314":
            if os.path.exists(LICENSE_FILE):
                with open(LICENSE_FILE, "r") as f:
                    old = f.read().strip()
                    if old.startswith("HUIYI1314_"):
                        if check_license():
                            messagebox.showinfo("成功", "欢迎回来，演示期内。")
                            root.destroy()
                        else:
                            messagebox.showerror("失败", "Huiyi1314 专属 7 天演示已到期！")
                        return
            
            today_str = datetime.date.today().strftime("%Y%m%d")
            with open(LICENSE_FILE, "w") as f:
                f.write(f"HUIYI1314_{today_str}")
            messagebox.showinfo("成功", "专属 7 天演示激活成功！")
            root.destroy()
            return

        # 正常的算号器激活码验证
        is_valid, msg = verify_key(user_input)
        if is_valid:
            with open(LICENSE_FILE, "w") as f:
                f.write(user_input)
            messagebox.showinfo("成功", "激活成功！即将进入系统。")
            root.destroy()
        else:
            messagebox.showerror("激活失败", msg)

    tk.Button(root, text="立即激活", bg="#2563eb", fg="white", font=("Arial", 11, "bold"), width=15, command=do_activate).pack(pady=20)

    root.mainloop()

def start_backend():
    # 关闭日志，防止黑框
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, log_level="error")

if __name__ == '__main__':
    if not check_license():
        show_activation_window()
        if not check_license():
            sys.exit(0)

    # 启动后端线程
    t = threading.Thread(target=start_backend, daemon=True)
    t.start()

    # 智能轮询等待后端启动（最多等 15 秒）
    pass  # 移除中文打印，防止 Windows 编码崩溃
    backend_ready = False
    for _ in range(30):
        try:
            requests.get("http://127.0.0.1:8000/api/auth/setup-status", timeout=1)
            backend_ready = True
            break
        except requests.exceptions.ConnectionError:
            time.sleep(0.5)

    if not backend_ready:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("启动失败", "后台服务启动超时！\n请检查是否被杀毒软件拦截，或尝试右键以管理员身份运行。")
        sys.exit(1)

    # 唤起独立客户端窗口
    window = webview.create_window(
        title="Tostiyk ERP",
        url="http://127.0.0.1:8000",
        width=1440,
        height=900,
        maximized=True
    )
    webview.start()
