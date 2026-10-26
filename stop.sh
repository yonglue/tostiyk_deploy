#!/bin/bash
echo "🛑 正在停止前后端服务..."
kill -9 $(lsof -t -i:8000) 2>/dev/null
kill -9 $(lsof -t -i:5173) 2>/dev/null
pkill -9 -f uvicorn 2>/dev/null
pkill -9 -f "vite" 2>/dev/null
echo "✅ 服务已全部停止！"
