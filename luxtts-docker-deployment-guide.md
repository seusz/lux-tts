# LuxTTS Docker 部署指南

## 📋 搜索结果总结

### 🔍 官方信息
- **官方仓库**: [ysharma3501/LuxTTS](https://github.com/ysharma3501/LuxTTS)
- **Stars**: 3732
- **描述**: A high-quality rapid TTS voice cloning model that reaches speeds of 150x realtime
- **Docker 支持**: ❌ 官方仓库没有提供 Dockerfile

### 🎯 推荐的第三方部署方案

#### 1. LuxTTS-Gradio (推荐)
- **仓库**: [NidAll/LuxTTS-Gradio](https://github.com/NidAll/LuxTTS-Gradio)
- **Stars**: 25
- **特点**: 
  - 提供 Gradio Web UI
  - 适合快速部署和测试
  - 包含完整的安装脚本

#### 2. OptiClone
- **仓库**: [ycharfi09/OptiClone](https://github.com/ycharfi09/OptiClone)
- **Stars**: 42
- **特点**: 
  - 桌面应用
  - 适合本地使用

#### 3. LuxTTS-ONNX
- **仓库**: [ningyos/luxtts-onnx](https://github.com/ningyos/luxtts-onnx)
- **Stars**: 3
- **特点**: 
  - ONNX 推理
  - 无需 PyTorch

---

## 🐳 Docker 部署方案

### 方案 1: 使用 LuxTTS-Gradio 创建 Dockerfile

#### 1. 克隆仓库
```bash
git clone https://github.com/NidAll/LuxTTS-Gradio.git
cd LuxTTS-Gradio
```

#### 2. 创建 Dockerfile
```dockerfile
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
```

#### 3. 构建镜像
```bash
docker build -t luxtts-gradio .
```

#### 4. 运行容器
```bash
docker run -d \
  --name luxtts-gradio \
  -p 7860:7860 \
  -v $(pwd)/models:/app/models \
  luxtts-gradio
```

#### 5. 访问 Web UI
打开浏览器访问：`http://localhost:7860`

---

### 方案 2: 手动创建自定义 Dockerfile

#### 1. 创建项目目录
```bash
mkdir luxtts-docker
cd luxtts-docker
```

#### 2. 创建 Dockerfile
```dockerfile
FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    sox \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 克隆 LuxTTS 仓库
RUN git clone https://github.com/ysharma3501/LuxTTS.git .

# 安装依赖
RUN pip install --no-cache-dir -e .

# 暴露端口 (如果使用 Gradio)
EXPOSE 7860

# 默认命令
CMD ["python", "-c", "print('LuxTTS container ready')"]
```

#### 3. 构建镜像
```bash
docker build -t luxtts .
```

#### 4. 运行容器
```bash
docker run -d \
  --name luxtts \
  --gpus all \
  -p 7860:7860 \
  -v $(pwd)/models:/app/models \
  luxtts
```

---

## 📝 使用 Docker Compose

### docker-compose.yml
```yaml
version: '3.8'

services:
  luxtts:
    build: .
    container_name: luxtts-gradio
    ports:
      - "7860:7860"
    volumes:
      - ./models:/app/models
      - ./data:/app/data
    environment:
      - GRADIO_SERVER_NAME=0.0.0.0
      - GRADIO_SERVER_PORT=7860
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    restart: unless-stopped
```

### 启动服务
```bash
docker-compose up -d
```

### 查看日志
```bash
docker-compose logs -f luxtts
```

---

## 🔧 配置说明

### 环境变量
- `GRADIO_SERVER_NAME`: 绑定地址 (默认 0.0.0.0)
- `GRADIO_SERVER_PORT`: 服务端口 (默认 7860)
- `CUDA_VISIBLE_DEVICES`: CUDA 设备可见性

### 数据卷
- `./models`: 模型文件存储
- `./data`: 音频数据存储
- `./output`: 生成音频输出

---

## ⚡ 性能优化

### GPU 加速
```bash
docker run --gpus all ...
```

### 内存优化
```dockerfile
# 在 Dockerfile 中设置
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
```

### 缓存优化
```dockerfile
# 使用多阶段构建
FROM python:3.10-slim AS builder
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.10-slim
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
```

---

## 🎯 快速开始

### 1. 使用 LuxTTS-Gradio (最简单)
```bash
git clone https://github.com/NidAll/LuxTTS-Gradio.git
cd LuxTTS-Gradio
docker build -t luxtts-gradio .
docker run -d -p 7860:7860 luxtts-gradio
```

### 2. 访问 Web UI
打开浏览器访问：`http://localhost:7860`

### 3. 使用流程
1. 输入文本
2. 上传提示音频 (WAV/FLAC 推荐)
3. 等待 "Model status: ready"
4. 点击 Generate 生成音频
5. 播放输出

---

## 📚 参考资料

- **官方仓库**: https://github.com/ysharma3501/LuxTTS
- **Gradio UI**: https://github.com/NidAll/LuxTTS-Gradio
- **OptiClone**: https://github.com/ycharfi09/OptiClone
- **ONNX 版本**: https://github.com/ningyos/luxtts-onnx

---

## ⚠️ 注意事项

1. **GPU 支持**: 需要 NVIDIA GPU 和 Docker GPU 支持
2. **内存需求**: 建议至少 8GB 内存
3. **磁盘空间**: 模型文件约 2-4GB
4. **音频格式**: 支持 WAV, FLAC, MP3
5. **网络**: 首次运行需要下载模型

---

## 🐛 常见问题

### Q: Docker 启动失败
A: 检查 GPU 驱动和 Docker GPU 支持

### Q: 模型加载慢
A: 首次运行需要下载模型，建议使用本地模型

### Q: 音频质量差
A: 使用高质量的提示音频 (WAV/FLAC)

---

**最后更新**: 2026-04-27
**版本**: 1.0
