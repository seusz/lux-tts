FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    sox \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 创建数据目录
RUN mkdir -p /app/models /app/data /app/output

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY luxtts_gradio_api.py .
COPY luxtts_api_server.py .

# 安装 FastAPI 和 Uvicorn
RUN pip install --no-cache-dir fastapi uvicorn

# 暴露端口
EXPOSE 7860 8000

# 默认启动 Gradio + API
CMD ["python", "luxtts_gradio_api.py", "--host", "0.0.0.0", "--port", "7860"]
