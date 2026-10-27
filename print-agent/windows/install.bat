@echo off
chcp 65001 >nul
title Tostiyk ERP 打印代理 - 安装程序
echo 正在配置 Tostiyk ERP 打印代理...
set "APP_DIR=%~dp0"
set "EXE_PATH=%APP_DIR%TostiykPrintAgent.exe"

:: 注册到计划任务，隐藏窗口静默运行
schtasks /create /tn "TostiykPrintAgent" /tr "\"%EXE_PATH%\"" /sc onlogon /rl highest /f
if %ERRORLEVEL% equ 0 (
    echo ✅ 打印代理安装成功！将在登录时自动后台静默运行。
    start "" "%EXE_PATH%"
) else (
    echo ❌ 安装失败，请右键点击本文件，选择“以管理员身份运行”。
)
pause
