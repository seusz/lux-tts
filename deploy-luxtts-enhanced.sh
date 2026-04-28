#!/bin/bash
# LuxTTS Docker 部署脚本 (增强版)
# 功能：Web UI + REST API + 局域网访问

set -e

echo "=================================================="
echo "🚀 LuxTTS Docker 部署脚本 (增强版)"
echo "=================================================="

# 配置变量
PROJECT_NAME="luxtts-gradio"
CONTAINER_NAME="luxtts-gradio"
WEB_UI_PORT=17860  # 宿主机端口
API_PORT=8000      # API 端口
MODEL_DIR="./models"
DATA_DIR="./data"
OUTPUT_DIR="./output"

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

echo "✅ Docker 已安装"

# 检查 Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "⚠️  docker-compose 未找到，尝试使用 docker compose"
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
    echo "✅ docker-compose 已安装"
fi

# 检查 NVIDIA GPU 支持
if command -v nvidia-smi &> /dev/null; then
    echo "✅ NVIDIA GPU 驱动已安装"
    GPU_SUPPORT="--gpus all"
else
    echo "⚠️  未检测到 NVIDIA GPU，将使用 CPU 模式"
    GPU_SUPPORT=""
fi

# 创建项目目录
echo ""
echo "📁 创建项目目录..."
mkdir -p "$MODEL_DIR"
mkdir -p "$DATA_DIR"
mkdir -p "$OUTPUT_DIR"

# 检查是否已有 docker-compose.yml
if [ ! -f "docker-compose.yml" ]; then
    echo "📝 创建 docker-compose.yml..."
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  luxtts:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: luxtts-gradio
    ports:
      - "17860:7860"
      - "8000:8000"
    volumes:
      - ./models:/app/models
      - ./data:/app/data
      - ./output:/app/output
    environment:
      - GRADIO_SERVER_NAME=0.0.0.0
      - GRADIO_SERVER_PORT=7860
      - CUDA_VISIBLE_DEVICES=0
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
EOF
    echo "✅ docker-compose.yml 创建完成"
else
    echo "✅ docker-compose.yml 已存在"
fi

# 检查是否已有 Dockerfile
if [ ! -f "Dockerfile" ]; then
    echo "📝 创建 Dockerfile..."
    cat > Dockerfile << 'EOF'
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    sox \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/models /app/data /app/output

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY luxtts_gradio_api.py .
COPY luxtts_api_server.py .
RUN pip install --no-cache-dir fastapi uvicorn

EXPOSE 7860 8000

CMD ["python", "luxtts_gradio_api.py", "--host", "0.0.0.0", "--port", "7860"]
EOF
    echo "✅ Dockerfile 创建完成"
else
    echo "✅ Dockerfile 已存在"
fi

# 检查是否已有 requirements.txt
if [ ! -f "requirements.txt" ]; then
    echo "📝 创建 requirements.txt..."
    cat > requirements.txt << 'EOF'
gradio>=4.0.0
luxvoice>=0.1.0
fastapi
uvicorn
scipy
numpy
EOF
    echo "✅ requirements.txt 创建完成"
else
    echo "✅ requirements.txt 已存在"
fi

# 停止并删除现有容器
if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
    echo "⚠️  容器已存在，正在停止并删除..."
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
fi

# 构建镜像
echo ""
echo "🔨 构建 Docker 镜像..."
$COMPOSE_CMD build

echo "✅ 镜像构建完成"

# 启动服务
echo ""
echo "🚀 启动服务..."
$COMPOSE_CMD up -d

echo "✅ 服务启动成功"

# 等待服务就绪
echo ""
echo "⏳ 等待服务就绪..."
sleep 10

# 检查服务状态
echo ""
echo "📊 服务状态检查..."
docker ps -f name="$CONTAINER_NAME"

# 显示访问信息
echo ""
echo "=================================================="
echo "🎉 部署完成!"
echo "=================================================="
echo ""
echo "🌐 Web UI 访问地址:"
echo "   http://localhost:$WEB_UI_PORT"
echo "   http://<你的 IP>:$WEB_UI_PORT  (局域网访问)"
echo ""
echo "🔌 REST API 访问地址:"
echo "   http://localhost:8000"
echo "   http://<你的 IP>:8000  (局域网访问)"
echo ""
echo "📚 API 文档:"
echo "   http://localhost:8000/api/docs"
echo ""
echo "🔍 健康检查:"
echo "   http://localhost:8000/health"
echo ""
echo "📝 日志查看:"
echo "   docker logs -f $CONTAINER_NAME"
echo ""
echo "🛑 停止服务:"
echo "   $COMPOSE_CMD down"
echo ""
echo "🔄 重启服务:"
echo "   $COMPOSE_CMD restart"
echo ""
echo "📁 数据目录:"
echo "   Models: $MODEL_DIR"
echo "   Data: $DATA_DIR"
echo "   Output: $OUTPUT_DIR"
echo ""
echo "=================================================="
echo "💡 使用提示:"
echo "1. 首次运行需要下载模型文件 (约 2-4GB)"
echo "2. 局域网访问：将 <你的 IP> 替换为实际 IP 地址"
echo "3. API 调用示例见 /api/docs"
echo "=================================================="
