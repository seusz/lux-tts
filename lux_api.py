"""
LuxTTS OpenAI-Compat API Server
===============================
兼容 SillyTavern / OpenAI TTS API 格式
端点: POST /v1/audio/speech
"""
import io
import tempfile
import os
import traceback
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Lazy-load LuxTTS to avoid blocking startup
model = None
app = FastAPI(title="LuxTTS API", version="1.0.0")

# CORS - allow all for SillyTavern
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_model():
    global model
    if model is None:
        print("Loading LuxTTS model on GPU...")
        from lux_tts import LuxTTS
        model = LuxTTS(device="cuda")
        print("Model loaded.")
    return model


@app.get("/")
async def root():
    return {
        "name": "LuxTTS API",
        "version": "1.0.0",
        "status": "ok",
        "endpoints": {
            "POST /v1/audio/speech": "Generate speech (OpenAI compat)",
            "POST /v1/audio/speech/file": "Generate with reference audio file upload",
            "GET  /health": "Health check",
        }
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/v1/models")
async def list_models():
    """OpenAI-compatible models endpoint"""
    return {
        "object": "list",
        "data": [
            {
                "id": "lux-tts",
                "object": "model",
                "created": 1700000000,
                "owned_by": "LuxTTS",
            }
        ]
    }


@app.post("/v1/audio/speech")
async def tts_openai_compat(
    input: str = Form(...),
    model: str = Form(default="lux-tts"),
    voice: UploadFile = File(...),
    response_format: str = Form(default="wav"),
    speed: float = Form(default=1.0),
):
    """
    OpenAI TTS API 兼容端点 (form-data)
    SillyTavern 通常发送:
      - input: 要合成的文本
      - model: "tts-1" (我们忽略，用 lux-tts)
      - voice: 参考音频文件
      - response_format: "wav" / "mp3" (我们只支持 wav)
      - speed: 语速 (0.25 - 4.0)
    """
    try:
        print(f"[TTS] input={input!r}, voice={voice.filename}, speed={speed}")

        # Save uploaded reference audio to temp file
        suffix = Path(voice.filename).suffix.lower() if voice.filename else ".wav"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(await voice.read())
            ref_path = tmp.name

        m = get_model()

        # LuxTTS synthesize
        audio_tensor = m.synthesize(
            ref_audio_path=ref_path,
            text=input,
            speed=speed,
        )

        # Convert to numpy
        if hasattr(audio_tensor, "cpu"):
            import torch
            audio_np = audio_tensor.cpu().numpy()
        else:
            audio_np = audio_tensor

        # Flatten if multi-channel
        if audio_np.ndim > 1:
            audio_np = audio_np.mean(axis=1) if audio_np.ndim == 2 else audio_np.flatten()
        audio_np = audio_np.astype("float32")

        # Encode as WAV
        import numpy as np
        import struct
        import wave

        buf = io.BytesIO()
        with wave.open(buf, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(48000)
            # Clamp and convert to 16-bit int
            samples = np.clip(audio_np, -1.0, 1.0)
            int_samples = (samples * 32767).astype("<h")
            w.writeframes(int_samples.tobytes())

        buf.seek(0)

        # Cleanup temp file
        os.unlink(ref_path)

        return Response(
            content=buf.read(),
            media_type="audio/wav",
            headers={
                "Content-Disposition": 'attachment; filename="output.wav"'
            }
        )

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/audio/speech/json")
async def tts_json(
    input: str = Form(...),
    ref_audio_url: str = Form(default=""),
    ref_audio_b64: str = Form(default=""),
    speed: float = Form(default=1.0),
):
    """
    JSON body 版本端点
    可以传 Base64 编码的参考音频，适合 API 调用
    """
    import base64
    import struct
    import wave
    import numpy as np

    try:
        # Get reference audio bytes
        if ref_audio_b64:
            ref_bytes = base64.b64decode(ref_audio_b64)
        elif ref_audio_url:
            import urllib.request
            with urllib.request.urlopen(ref_audio_url, timeout=10) as r:
                ref_bytes = r.read()
        else:
            raise HTTPException(status_code=400, detail="Must provide ref_audio_b64 or ref_audio_url")

        suffix = ".wav"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(ref_bytes)
            ref_path = tmp.name

        m = get_model()
        audio_tensor = m.synthesize(ref_audio_path=ref_path, text=input, speed=speed)

        if hasattr(audio_tensor, "cpu"):
            audio_np = audio_tensor.cpu().numpy()
        else:
            audio_np = audio_tensor

        if audio_np.ndim > 1:
            audio_np = audio_np.mean(axis=1) if audio_np.ndim == 2 else audio_np.flatten()
        audio_np = audio_np.astype("float32")

        buf = io.BytesIO()
        with wave.open(buf, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(48000)
            samples = np.clip(audio_np, -1.0, 1.0)
            int_samples = (samples * 32767).astype("<h")
            w.writeframes(int_samples.tobytes())

        buf.seek(0)
        os.unlink(ref_path)

        return Response(
            content=buf.read(),
            media_type="audio/wav",
            headers={"Content-Disposition": 'attachment; filename="output.wav"'}
        )

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print("=" * 50)
    print("  LuxTTS OpenAI-Compat API Server")
    print("  http://0.0.0.0:8080")
    print("  Endpoints:")
    print("    POST /v1/audio/speech  (form-data, SillyTavern compatible)")
    print("    POST /v1/audio/speech/json  (JSON body, Base64 ref audio)")
    print("    GET  /health")
    print("=" * 50)
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info",
    )
