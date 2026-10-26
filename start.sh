#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"
echo "🛑 清理旧进程..."
kill -9 $(lsof -t -i:8000) 2>/dev/null
kill -9 $(lsof -t -i:5173) 2>/dev/null
echo "🐍 启动后端..."
source venv/bin/activate
nohup uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --reload-dir app > backend.log 2>&1 &
echo "🎨 启动前端..."
cd frontend
nohup npm run dev > ../frontend.log 2>&1 &
echo "✅ 启动完成！请访问 http://localhost:5173"
