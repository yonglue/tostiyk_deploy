#!/bin/bash
cd ~/tostiyk-erp

# 确保后端在跑
if ! lsof -i :8000 > /dev/null 2>&1; then
  echo "🛑 后端未启动，正在启动..."
  ./start.sh
  sleep 4
fi

# 杀掉现有 Vite（让 Playwright 起新的，确保代码是最新的）
pkill -9 -f "vite" 2>/dev/null || true
kill -9 $(lsof -t -i:5173) 2>/dev/null || true
sleep 1

# 跑测试
cd frontend
PW_ADMIN_PASS=${PW_ADMIN_PASS:-admin} npx playwright test "$@"
