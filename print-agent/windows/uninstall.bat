@echo off
chcp 65001 >nul
title Tostiyk ERP 打印代理 - 卸载程序
echo 正在卸载打印代理...
schtasks /delete /tn "TostiykPrintAgent" /f >nul 2>&1
taskkill /F /IM TostiykPrintAgent.exe >nul 2>&1
echo ✅ 打印代理已完全卸载！
pause
