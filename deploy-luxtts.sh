#!/bin/bash
# LuxTTS Docker 部署脚本
# 使用方法：./deploy-luxtts.sh

set -e

echo "=================================================="
echo "🚀 LuxTTS Docker 部署脚本"
echo "=================================================="

# 配置变量
PROJECT_NAME="luxtts-gradio"
CONTAINER_NAME="luxtts-gradio"
HOST_PORT=7860
CONTAINER_PORT=7860
MODEL_DIR="./models"
DATA_DIR="./data"

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

echo "✅ Docker 已安装"

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

# 克隆 LuxTTS-Gradio 仓库
if [ ! -d "LuxTTS-Gradio" ]; then
    echo "📦 克隆 LuxTTS-Gradio 仓库..."
    git clone https://github.com/NidAll/LuxTTS-Gradio.git
else
    echo "✅ LuxTTS-Gradio 已存在"
fi

cd LuxTTS-Gradio

# 创建 Dockerfile
echo ""
echo "🐳 创建 Dockerfile..."
cat > Dockerfile << 'EOF'
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    sox \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露 Gradio 端口
EXPOSE 7860

# 启动命令
CMD ["python", "gradio_app.py"]
EOF

echo "✅ Dockerfile 创建完成"

# 构建镜像
echo ""
echo "🔨 构建 Docker 镜像..."
docker build -t "$PROJECT_NAME" .

echo "✅ 镜像构建完成"

# 检查是否已有容器运行
if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
    echo "⚠️  容器已存在，正在停止并删除..."
    docker stop "$CONTAINER_NAME"
    docker rm "$CONTAINER_NAME"
fi

# 运行容器
echo ""
echo "🚀 启动容器..."
docker run -d \
    $GPU_SUPPORT \
    --name "$CONTAINER_NAME" \
    -p "$HOST_PORT:$CONTAINER_PORT" \
    -v "$MODEL_DIR:/app/models" \
    -v "$DATA_DIR:/app/data" \
    -e GRADIO_SERVER_NAME="0.0.0.0" \
    -e GRADIO_SERVER_PORT="$CONTAINER_PORT" \
    "$PROJECT_NAME"

echo "✅ 容器启动成功"

# 显示状态
echo ""
echo "=================================================="
echo "🎉 部署完成!"
echo "=================================================="
echo ""
echo "📊 容器状态:"
docker ps -f name="$CONTAINER_NAME"
echo ""
echo "🌐 Web UI 访问地址:"
echo "   http://localhost:$HOST_PORT"
echo ""
echo "📝 日志查看:"
echo "   docker logs -f $CONTAINER_NAME"
echo ""
echo "🛑 停止容器:"
echo "   docker stop $CONTAINER_NAME"
echo ""
echo "🔄 重启容器:"
echo "   docker restart $CONTAINER_NAME"
echo ""
echo "🗑️  删除容器:"
echo "   docker rm -f $CONTAINER_NAME"
echo ""
echo "=================================================="
