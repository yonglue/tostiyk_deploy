@echo off
chcp 65001 >nul
title Tostiyk ERP 打印代理 - 一键修复工具
echo 正在检查并修复打印代理状态...
taskkill /F /IM TostiykPrintAgent.exe >nul 2>&1
set "APP_DIR=%~dp0"
set "EXE_PATH=%APP_DIR%TostiykPrintAgent.exe"
schtasks /create /tn "TostiykPrintAgent" /tr "\"%EXE_PATH%\"" /sc onlogon /rl highest /f >nul
start "" "%EXE_PATH%"
echo ✅ 修复完成！如果收银界面绿灯亮起，说明已恢复正常。
timeout /t 3 >nul
