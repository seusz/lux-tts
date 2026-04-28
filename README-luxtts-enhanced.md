# 🚀 LuxTTS Docker 部署指南 (增强版)

## 📋 功能特性

### ✅ 已实现功能
1. **Web UI**: Gradio 界面，支持文本输入和音频上传
2. **REST API**: FastAPI 提供的完整 REST API
3. **局域网访问**: 绑定 0.0.0.0，支持局域网访问
4. **端口映射**: 
   - Web UI: 17860 (宿主机) → 7860 (容器)
   - API: 8000 (宿主机) → 8000 (容器)
5. **GPU 加速**: 支持 NVIDIA GPU 加速
6. **健康检查**: 自动健康检查
7. **数据持久化**: 模型、数据、输出目录挂载

---

## 🎯 快速开始

### 方法 1: 使用部署脚本 (推荐)

```bash
# 1. 进入项目目录
cd /opt/data

# 2. 运行部署脚本
chmod +x deploy-luxtts-enhanced.sh
./deploy-luxtts-enhanced.sh
```

### 方法 2: 手动部署

```bash
# 1. 创建项目目录
mkdir -p luxtts-docker
cd luxtts-docker

# 2. 创建目录结构
mkdir -p models data output

# 3. 复制配置文件
# - Dockerfile
# - docker-compose.yml
# - requirements.txt
# - luxtts_gradio_api.py
# - luxtts_api_server.py

# 4. 构建并运行
docker-compose up -d
```

---

## 🌐 访问地址

### Web UI
- **本地访问**: http://localhost:17860
- **局域网访问**: http://<你的 IP>:17860

### REST API
- **本地访问**: http://localhost:8000
- **局域网访问**: http://<你的 IP>:8000

### API 文档
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔌 API 使用示例

### 1. 检查服务状态
```bash
curl http://localhost:8000/health
```

### 2. 生成语音 (最简单)
```bash
curl -X POST "http://localhost:8000/api/generate" \
  -F "text=你好，世界！" \
  -o output.wav
```

### 3. 生成语音 (带提示音频)
```bash
curl -X POST "http://localhost:8000/api/generate" \
  -F "text=使用提示音频克隆的声音" \
  -F "prompt_audio=@prompt.wav" \
  -o output.wav
```

### 4. 批量生成语音
```bash
# 使用 Python 脚本
python api_examples.py
```

### 5. Python 调用示例
```python
import requests

# 简单生成
response = requests.post(
    "http://localhost:8000/api/generate",
    data={"text": "你好，世界！"},
    timeout=120
)

with open("output.wav", "wb") as f:
    f.write(response.content)
```

---

## 📁 目录结构

```
luxtts-docker/
├── Dockerfile                 # Docker 镜像构建文件
├── docker-compose.yml         # Docker Compose 配置
├── requirements.txt           # Python 依赖
├── deploy-luxtts-enhanced.sh  # 部署脚本
├── luxtts_gradio_api.py       # Gradio + API 服务
├── luxtts_api_server.py       # 独立 API 服务
├── api_examples.py            # API 使用示例
├── models/                    # 模型文件目录
├── data/                      # 数据目录
└── output/                    # 输出目录
```

---

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `GRADIO_SERVER_NAME` | Gradio 绑定地址 | 0.0.0.0 |
| `GRADIO_SERVER_PORT` | Gradio 端口 | 7860 |
| `CUDA_VISIBLE_DEVICES` | CUDA 设备 | 0 |

### 数据卷挂载

| 宿主机目录 | 容器目录 | 说明 |
|-----------|---------|------|
| `./models` | `/app/models` | 模型文件 |
| `./data` | `/app/data` | 输入数据 |
| `./output` | `/app/output` | 输出音频 |

---

## 🚀 容器管理

### 查看容器状态
```bash
docker ps -f name=luxtts-gradio
```

### 查看日志
```bash
docker logs -f luxtts-gradio
```

### 停止服务
```bash
docker-compose down
```

### 重启服务
```bash
docker-compose restart
```

### 删除容器
```bash
docker-compose down -v
```

---

## 💡 使用提示

### 1. 首次运行
- 首次运行需要下载模型文件 (约 2-4GB)
- 下载完成后会保存到 `models/` 目录
- 下次启动会直接使用本地模型

### 2. 局域网访问
- 将 `<你的 IP>` 替换为实际 IP 地址
- 确保防火墙允许 17860 和 8000 端口
- 示例：`http://192.168.1.100:17860`

### 3. GPU 加速
- 需要 NVIDIA GPU 和驱动
- 确保 Docker 支持 GPU (`--gpus all`)
- 检查：`docker run --gpus all nvidia/cuda nvidia-smi`

### 4. 性能优化
- 使用 SSD 存储模型文件
- 增加容器内存限制
- 调整 batch size

---

## 🐛 常见问题

### Q: 服务启动失败
**A**: 检查以下事项:
- Docker 是否正常运行
- GPU 驱动是否正确安装
- 端口是否被占用
- 查看日志：`docker logs luxtts-gradio`

### Q: 模型下载失败
**A**: 
- 检查网络连接
- 使用国内镜像源
- 手动下载模型到 `models/` 目录

### Q: 局域网无法访问
**A**:
- 检查防火墙设置
- 确认 IP 地址正确
- 确保端口已开放

### Q: API 调用超时
**A**:
- 增加超时时间
- 检查网络延迟
- 使用较小的文本

---

## 📊 API 端点

### 健康检查
- `GET /health` - 服务健康状态
- `GET /` - 服务信息

### 语音生成
- `POST /api/generate` - 生成语音
  - 参数：`text`, `prompt_audio`, `speed`
  - 返回：WAV 音频文件

### 文档
- `GET /api/docs` - API 文档
- `GET /redoc` - ReDoc 文档

---

## 🔒 安全建议

1. **生产环境**: 添加身份验证
2. **网络隔离**: 使用 Docker 网络隔离
3. **HTTPS**: 使用反向代理配置 HTTPS
4. **限流**: 添加 API 限流保护

---

## 📚 参考资料

- [LuxTTS 官方仓库](https://github.com/ysharma3501/LuxTTS)
- [Gradio 文档](https://www.gradio.app/)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Docker 文档](https://docs.docker.com/)

---

## 🎯 下一步

1. **集成到你的项目**: 使用 API 调用 LuxTTS
2. **自定义配置**: 修改 Dockerfile 添加额外功能
3. **性能调优**: 根据实际需求优化配置
4. **监控维护**: 定期检查容器状态和日志

---

**最后更新**: 2026-04-27
**版本**: 2.0 (增强版)
**作者**: Hermes Agent
