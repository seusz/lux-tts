"""
LuxTTS REST API 服务
提供完整的 REST API 接口供外部调用
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Response
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Optional
import io
import os
import tempfile
import uvicorn
import shutil

app = FastAPI(
    title="LuxTTS API",
    description="LuxTTS 文本转语音 REST API",
    version="1.0.0"
)

# 模拟 LuxTTS 导入 (实际使用时需要安装 LuxTTS)
try:
    from luxvoice import LuxVoice
    LUXTTS_AVAILABLE = True
except ImportError:
    LUXTTS_AVAILABLE = False

class SpeechRequest(BaseModel):
    """语音生成请求"""
    text: str
    prompt_audio: Optional[str] = None  # base64 编码的音频文件
    speed: float = 1.0
    device: str = "cuda"

class SpeechResponse(BaseModel):
    """语音生成响应"""
    success: bool
    message: str
    audio_url: Optional[str] = None

@app.get("/")
async def root():
    """服务健康检查"""
    return {
        "service": "LuxTTS API",
        "version": "1.0.0",
        "status": "running",
        "luxtts_available": LUXTTS_AVAILABLE
    }

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "luxtts_available": LUXTTS_AVAILABLE
    }

@app.get("/api/docs")
async def api_docs():
    """API 文档"""
    return {
        "title": "LuxTTS API 文档",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/generate": {
                "description": "生成语音",
                "parameters": {
                    "text": "要转换的文本 (必填)",
                    "prompt_audio": "提示音频 (可选，base64 编码)",
                    "speed": "语速 (可选，默认 1.0)"
                },
                "response": "WAV 音频文件"
            },
            "GET /api/status": {
                "description": "检查服务状态",
                "response": "服务状态信息"
            },
            "GET /": {
                "description": "服务信息",
                "response": "服务基本信息"
            }
        }
    }

@app.get("/api/status")
async def api_status():
    """API 状态"""
    return {
        "service": "LuxTTS API",
        "version": "1.0.0",
        "status": "running",
        "luxtts_available": LUXTTS_AVAILABLE,
        "endpoints": [
            "POST /api/generate",
            "GET /api/status",
            "GET /api/docs"
        ]
    }

@app.post("/api/generate")
async def generate_speech(
    text: str = None,
    prompt_audio: UploadFile = None,
    speed: float = 1.0,
    device: str = "cuda"
):
    """
    生成语音
    
    - **text**: 要转换的文本 (必填)
    - **prompt_audio**: 提示音频文件 (可选)
    - **speed**: 语速 (可选，默认 1.0)
    - **device**: 设备 (可选，默认 cuda)
    """
    if not text:
        raise HTTPException(status_code=400, detail="text 参数必需")
    
    if not LUXTTS_AVAILABLE:
        # 模拟模式
        return simulate_speech(text, speed)
    
    try:
        # 处理提示音频
        prompt_path = None
        if prompt_audio:
            prompt_path = f"/tmp/{prompt_audio.filename}"
            with open(prompt_path, "wb") as buffer:
                shutil.copyfileobj(prompt_audio.file, buffer)
        
        # 导入 LuxTTS
        from luxvoice import LuxVoice
        
        # 加载模型
        model = LuxVoice.from_pretrained("/app/models", device=device)
        
        # 生成语音
        audio = model.generate(
            text=text,
            prompt_path=prompt_path,
            device=device
        )
        
        # 释放显存 - 修复显存不释放 bug
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        # 保存为 WAV
        from scipy.io import wavfile
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            wavfile.write(f, 22050, audio)
            audio_path = f.name
        
        # 返回音频文件
        return FileResponse(
            audio_path,
            media_type="audio/wav",
            filename="output.wav"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成失败：{str(e)}")

def simulate_speech(text: str, speed: float):
    """模拟模式 - 生成简单的音频"""
    import numpy as np
    from scipy.io import wavfile
    import tempfile
    
    # 生成简单的正弦波
    sample_rate = 22050
    duration = len(text) * 0.1  # 每个字符 0.1 秒
    frequency = 440  # A4 音符
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = 0.5 * np.sin(2 * np.pi * frequency * t)
    
    # 添加一些变化
    for i, char in enumerate(text):
        start = int(i * 0.1 * sample_rate)
        end = int((i + 1) * 0.1 * sample_rate)
        audio[start:end] *= 1 + 0.1 * np.sin(2 * np.pi * 100 * t[start:end])
    
    # 保存为 WAV
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wavfile.write(f, sample_rate, audio.astype(np.float32))
        audio_path = f.name
    
    return FileResponse(
        audio_path,
        media_type="audio/wav",
        filename="output.wav"
    )

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0", help="绑定地址")
    parser.add_argument("--port", type=int, default=8000, help="端口号")
    args = parser.parse_args()
    
    print(f"🚀 LuxTTS API 服务器启动...")
    print(f"📍 绑定地址：{args.host}:{args.port}")
    print(f"🔗 API 文档：http://{args.host}:{args.port}/api/docs")
    
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="info"
    )
