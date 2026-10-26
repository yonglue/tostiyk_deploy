#!/bin/bash
# 商业交付一键打包脚本

VERSION=$(date +%Y%m%d)
DELIVERY_DIR="TOSTIYK_ERP_DELIVERY_v$VERSION"
ZIP_NAME="TOSTIYK_ERP_v$VERSION.zip"

echo "🚀 开始构建生产级 Docker 镜像..."
docker compose build --no-cache

echo "📦 导出镜像为离线文件..."
docker save -o tostiyk-erp-backend.tar tostiyk-erp-backend:v1.0
docker save -o tostiyk-erp-frontend.tar tostiyk-erp-frontend:v1.0

echo "📁 正在生成客户交付目录..."
rm -rf "$DELIVERY_DIR"
mkdir -p "$DELIVERY_DIR"

cp tostiyk-erp-backend.tar tostiyk-erp-frontend.tar "$DELIVERY_DIR"/
# 🌟 核心修复：复制 Alembic 迁移文件
cp alembic.ini "$DELIVERY_DIR"/
cp -r alembic "$DELIVERY_DIR"/

# 🌟 核心修复 2：生成纯净的 docker-compose.yml（禁止 build）
cat > "$DELIVERY_DIR/docker-compose.yml" << 'EOM'
services:
  backend:
    image: tostiyk-erp-backend:v1.0
    restart: unless-stopped
    volumes:
      - ./data:/app/data
      - ./uploads:/app/uploads
      - ./backups:/app/backups
    environment:
      - TK_AUTO_CREATE_TABLES=1
      - TK_STRICT_MIGRATION=0
      - TK_STRICT_SECURITY=0
      - TK_ADMIN_PASSWORD=
    expose:
      - "8000"

  frontend:
    image: tostiyk-erp-frontend:v1.0
    restart: unless-stopped
    ports:
      - "80:80"
    depends_on:
      - backend
EOM

mkdir -p "$DELIVERY_DIR/data" "$DELIVERY_DIR/uploads" "$DELIVERY_DIR/backups"

cat > "$DELIVERY_DIR/README.md" << 'EOM'
# TOSTIYK ERP 部署指南

## 1. 环境要求
- 服务器需安装 Docker 和 Docker Compose。

## 2. 导入镜像（必须先执行！）
在终端中执行：
\`\`\`bash
docker load -i tostiyk-erp-backend.tar
docker load -i tostiyk-erp-frontend.tar
\`\`\`

## 3. 启动系统
执行：
\`\`\`bash
docker compose up -d
\`\`\`

## 4. 初始化管理员
浏览器访问 \`http://<服务器IP>\`，系统会自动弹出**欢迎设置**页面。
请设置您的超级管理员账号和密码，即可开始使用。
EOM

echo "🗜️ 正在压缩交付包..."
zip -r "$ZIP_NAME" "$DELIVERY_DIR" > /dev/null

rm tostiyk-erp-backend.tar tostiyk-erp-frontend.tar
rm -rf "$DELIVERY_DIR"

echo "✅ 交付包生成完毕: $ZIP_NAME"
