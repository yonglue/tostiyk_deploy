#!/bin/bash
# 一键生成干净的客户交付包

RELEASE_DIR="tostiyk_erp_release"
ZIP_NAME="tostiyk_erp_delivery_$(date +%Y%m%d).zip"

echo "🧹 正在清理旧的发布目录..."
rm -rf "$RELEASE_DIR" "$ZIP_NAME"
mkdir -p "$RELEASE_DIR"

echo "📦 正在复制核心代码..."
# 复制后端
cp -r app alembic scripts main.py requirements.txt alembic.ini Dockerfile .dockerignore "$RELEASE_DIR"/

# 复制前端（剔除 node_modules 和 dist）
mkdir -p "$RELEASE_DIR/frontend"
cp -r frontend/src frontend/public frontend/package.json frontend/package-lock.json frontend/vite.config.js frontend/index.html frontend/Dockerfile frontend/nginx.conf "$RELEASE_DIR/frontend"/

# 复制部署配置文件
cp docker-compose.yml "$RELEASE_DIR"/

echo "🗑️  正在清理敏感数据（确保出厂是 0 数据）..."
# 确保客户拿到的是空数据库，绝对不能包含你的本地数据！
rm -f "$RELEASE_DIR/tostiyk_erp.db"

# 清理一些多余的测试文件
rm -rf "$RELEASE_DIR/tests"

echo "🗜️  正在压缩为 ZIP..."
zip -r "$ZIP_NAME" "$RELEASE_DIR" -x "*.DS_Store" > /dev/null

echo "✅ 打包完成！请把这个文件发给客户: $ZIP_NAME"
