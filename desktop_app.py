import os

import sys
if getattr(sys, 'frozen', False):
    os.environ['TK_IS_DESKTOP'] = '1'

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

SALT = "Tostiyk_ERP_Secret_2026" # 你的加密盐，千万不能泄露给客户

def get_machine_id():
    try:
        if sys.platform == 'win32':
            out = subprocess.check_output('wmic csproduct get uuid', shell=True).decode()
            hw_id = out.split('\n')[1].strip()
        elif sys.platform == 'darwin':
            out = subprocess.check_output("ioreg -rd1 -c IOPlatformExpertDevice | grep IOPlatformUUID", shell=True).decode()
            hw_id = out.split('"')[3]
        else:
            hw_id = str(uuid.getnode())
        return f"TK-{hw_id[-8:].upper()}"
    except Exception:
        return "TK-UNKNOWN"

MACHINE_CODE = get_machine_id()
LICENSE_FILE = "license.key"

def generate_expected_key(machine_code):
    """根据机器码生成唯一合法的激活码"""
    raw = f"{machine_code}{SALT}".encode('utf-8')
    return hashlib.sha256(raw).hexdigest()[:16].upper()

def check_license():
    if not os.path.exists(LICENSE_FILE):
        return False
    with open(LICENSE_FILE, "r") as f:
        saved_key = f.read().strip()
    return saved_key == generate_expected_key(MACHINE_CODE)

def show_activation_window():
    """显示激活窗口"""
    root = tk.Tk()
    root.title("Tostiyk ERP - 软件激活")
    root.geometry("450x250")
    root.eval('tk::PlaceWindow . center')
    
    tk.Label(root, text="软件未授权，请将下方机器码发送给管理员", font=("Arial", 12)).pack(pady=10)
    
    # 机器码展示区
    frame_code = tk.Frame(root)
    frame_code.pack(pady=5)
    code_var = tk.StringVar(value=MACHINE_CODE)
    tk.Entry(frame_code, textvariable=code_var, state="readonly", font=("Consolas", 14), width=20, justify="center").pack(side=tk.LEFT, padx=5)
    
    def copy_code():
        root.clipboard_clear()
        root.clipboard_append(MACHINE_CODE)
        messagebox.showinfo("提示", "机器码已复制到剪贴板！")
    tk.Button(frame_code, text="复制", command=copy_code).pack(side=tk.LEFT)

    tk.Label(root, text="请输入管理员提供的激活码:", font=("Arial", 11)).pack(pady=(15, 5))
    key_var = tk.StringVar()
    tk.Entry(root, textvariable=key_var, font=("Consolas", 14), width=25, justify="center").pack()

    def do_activate():
        user_input = key_var.get().strip().upper()
        if user_input == generate_expected_key(MACHINE_CODE):
            with open(LICENSE_FILE, "w") as f:
                f.write(user_input)
            messagebox.showinfo("成功", "激活成功！即将进入系统。")
            root.destroy()
        else:
            messagebox.showerror("错误", "激活码不正确，请核对后重试。")

    tk.Button(root, text="立即激活", bg="#2563eb", fg="white", font=("Arial", 11, "bold"), width=15, command=do_activate).pack(pady=20)

    root.mainloop()

def start_backend():
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, log_level="error")

if __name__ == '__main__':
    # 1. 检查授权
    if not check_license():
        show_activation_window()
        # 如果用户直接关了激活窗口，退出程序
        if not check_license():
            sys.exit(0)

    # 2. 启动后端
    t = threading.Thread(target=start_backend, daemon=True)
    t.start()
    time.sleep(2)

    # 3. 唤起独立客户端窗口
    window = webview.create_window(
        title="Tostiyk ERP - 汽配进销存",
        url="http://127.0.0.1:8000",
        width=1440,
        height=900,
        maximized=True
    )
    webview.start()
