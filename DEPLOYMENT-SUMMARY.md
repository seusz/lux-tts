# 📊 LuxTTS Docker 增强部署方案总结

## 🎯 需求实现

### ✅ 已实现功能

| 功能 | 状态 | 说明 |
|------|------|------|
| **宿主机端口 17860** | ✅ | Web UI 端口映射为 17860 |
| **局域网访问** | ✅ | 绑定 0.0.0.0，支持局域网访问 |
| **REST API** | ✅ | FastAPI 提供完整 REST API |
| **GPU 加速** | ✅ | 支持 NVIDIA GPU |
| **健康检查** | ✅ | 自动健康检查 |
| **数据持久化** | ✅ | 模型、数据、输出目录挂载 |

---

## 📁 创建的文件

### 1. 核心文件
- ✅ **Dockerfile** - Docker 镜像构建文件
- ✅ **docker-compose.yml** - Docker Compose 配置
- ✅ **requirements.txt** - Python 依赖

### 2. 服务文件
- ✅ **luxtts_gradio_api.py** - Gradio + API 集成服务
- ✅ **luxtts_api_server.py** - 独立 FastAPI 服务

### 3. 部署脚本
- ✅ **deploy-luxtts-enhanced.sh** - 增强版部署脚本
- ✅ **api_examples.py** - API 使用示例

### 4. 文档
- ✅ **README-luxtts-enhanced.md** - 完整部署指南
- ✅ **DEPLOYMENT-SUMMARY.md** - 本文档

---

## 🌐 访问地址

### Web UI
```
本地访问：http://localhost:17860
局域网：http://<你的 IP>:17860
```

### REST API
```
本地访问：http://localhost:8000
局域网：http://<你的 IP>:8000
API 文档：http://localhost:8000/api/docs
```

---

## 🔌 API 端点

### 1. 健康检查
```bash
GET /health
GET /
```

### 2. 语音生成
```bash
POST /api/generate
```

**参数**:
- `text` (必填): 要转换的文本
- `prompt_audio` (可选): 提示音频文件
- `speed` (可选): 语速，默认 1.0

**返回**: WAV 音频文件

### 3. API 文档
```bash
GET /api/docs
GET /redoc
```

---

## 🚀 快速部署

### 方法 1: 使用部署脚本
```bash
cd /opt/data
chmod +x deploy-luxtts-enhanced.sh
./deploy-luxtts-enhanced.sh
```

### 方法 2: 手动部署
```bash
# 1. 创建项目目录
mkdir -p luxtts-docker && cd luxtts-docker

# 2. 复制所有文件
# (从 /opt/data 复制所有文件)

# 3. 构建并运行
docker-compose up -d
```

---

## 💻 API 调用示例

### 1. 简单生成
```bash
curl -X POST "http://localhost:8000/api/generate" \
  -F "text=你好，世界！" \
  -o output.wav
```

### 2. 带提示音频
```bash
curl -X POST "http://localhost:8000/api/generate" \
  -F "text=使用提示音频克隆的声音" \
  -F "prompt_audio=@prompt.wav" \
  -o output.wav
```

### 3. Python 调用
```python
import requests

response = requests.post(
    "http://localhost:8000/api/generate",
    data={"text": "你好，世界！"},
    timeout=120
)

with open("output.wav", "wb") as f:
    f.write(response.content)
```

### 4. 批量生成
```python
import requests

texts = [
    "早上好，今天天气真好。",
    "下午好，工作愉快！",
    "晚上好，祝你有个美好的夜晚。"
]

for text in texts:
    response = requests.post(
        "http://localhost:8000/api/generate",
        data={"text": text},
        timeout=120
    )
    with open(f"{text}.wav", "wb") as f:
        f.write(response.content)
```

---

## 📊 端口映射

| 服务 | 宿主机端口 | 容器端口 | 说明 |
|------|-----------|---------|------|
| **Web UI** | 17860 | 7860 | Gradio 界面 |
| **REST API** | 8000 | 8000 | FastAPI 服务 |

---

## 🗂️ 数据目录

| 目录 | 说明 | 用途 |
|------|------|------|
| **models/** | 模型文件 | 存储 LuxTTS 模型 |
| **data/** | 输入数据 | 提示音频、文本等 |
| **output/** | 输出音频 | 生成的 WAV 文件 |

---

## 🔧 容器管理

### 查看状态
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
- 下载完成后保存到 `models/` 目录
- 下次启动直接使用本地模型

### 2. 局域网访问
- 将 `<你的 IP>` 替换为实际 IP 地址
- 确保防火墙允许 17860 和 8000 端口
- 示例：`http://192.168.1.100:17860`

### 3. GPU 加速
- 需要 NVIDIA GPU 和驱动
- 确保 Docker 支持 GPU (`--gpus all`)
- 检查：`docker run --gpus all nvidia/cuda nvidia-smi`

---

## 🐛 常见问题

### Q: 服务启动失败
**A**: 
- 检查 Docker 是否正常运行
- 检查 GPU 驱动是否正确安装
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

---

## 📚 文件清单

所有文件已创建在 `/opt/data/`:

```
/opt/data/
├── Dockerfile                    # Docker 镜像构建文件
├── docker-compose.yml            # Docker Compose 配置
├── requirements.txt              # Python 依赖
├── deploy-luxtts-enhanced.sh     # 增强版部署脚本
├── luxtts_gradio_api.py          # Gradio + API 服务
├── luxtts_api_server.py          # 独立 API 服务
├── api_examples.py               # API 使用示例
├── README-luxtts-enhanced.md     # 完整部署指南
└── DEPLOYMENT-SUMMARY.md         # 本文档
```

---

## 🎯 下一步

1. **运行部署脚本**: `./deploy-luxtts-enhanced.sh`
2. **访问 Web UI**: http://localhost:17860
3. **测试 API**: 使用 `api_examples.py`
4. **集成到你的项目**: 使用 REST API

---

**部署时间**: 2026-04-27
**版本**: 2.0 (增强版)
**状态**: ✅ 所有文件已创建，可立即部署
