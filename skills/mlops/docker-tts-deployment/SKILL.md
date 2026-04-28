---
name: docker-tts-deployment
category: mlops
description: Guide for deploying TTS models (LuxTTS, Coqui, etc.) using Docker with GPU support and custom configurations
---

# Docker 部署 TTS 模型指南

## 概述
本文档总结了使用 Docker 部署各种 TTS (Text-to-Speech) 模型的方法和经验。

## 主要 TTS 模型

### 1. LuxTTS
**官方仓库**: https://github.com/ysharma3501/LuxTTS
- **特点**: 高质量快速 TTS 语音克隆模型，推理速度达 150 倍实时
- **Stars**: 3700+
- **Docker 支持**: 官方未提供 Dockerfile

**替代方案**:
- **OptiClone**: https://github.com/ycharfi09/OptiClone (基于 LuxTTS 的桌面应用)
- **LuxTTS-Gradio**: https://github.com/NidAll/LuxTTS-Gradio (Gradio UI)
- **luxtts-onnx**: https://github.com/ningyos/luxtts-onnx (ONNX 推理)

### 2. 其他 TTS 模型
- **Coqui TTS**: 成熟的开源 TTS 框架
- **Piper**: 快速本地 TTS
- **Bark**: Suno AI 的开源 TTS

## Docker 部署方法

### 方法 1: 使用官方或社区 Docker 镜像
```bash
# 搜索相关镜像
docker search <model-name>

# 拉取镜像
docker pull <image-name>

# 运行容器
docker run -p 7860:7860 <image-name>
```

### 方法 2: 自定义 Dockerfile
当官方未提供 Dockerfile 时:

```dockerfile
FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

# 安装依赖
RUN pip install lux-tts gradio

# 暴露端口
EXPOSE 7860

# 启动命令
CMD ["python", "app.py"]
```

### 方法 3: 使用 Gradio UI
对于有 Gradio 界面的项目:
```bash
docker run -p 7860:7860 --gpus all <image-name>
```

## 常见问题

### 1. GPU 支持
确保 Docker 容器可以访问 GPU:
```bash
docker run --gpus all ...
```

### 2. 数据持久化
使用 volume 挂载数据:
```bash
-v /path/to/data:/app/data
```

### 3. 网络配置
确保端口映射正确:
```bash
-p 7860:7860  # Gradio
-p 5000:5000   # Flask/FastAPI
```

## 推荐流程

1. **检查官方文档**: 首先查看项目 README 是否有 Docker 部署说明
2. **搜索社区镜像**: 在 Docker Hub 搜索相关镜像
3. **自定义构建**: 如无现成镜像，根据 requirements.txt 创建 Dockerfile
4. **测试验证**: 运行容器并测试功能
5. **优化配置**: 根据实际需求调整资源限制和配置

## 参考资料
- LuxTTS GitHub: https://github.com/ysharma3501/LuxTTS
- Docker Hub: https://hub.docker.com
- PyTorch Docker: https://hub.docker.com/r/pytorch/pytorch