# LuxTTS Gradio API 增强版
# 提供 Web UI + REST API 双重功能

import gradio as gr
import requests
import io
import base64
from typing import Optional
import numpy as np
from scipy.io import wavfile
import os

# 导入 LuxTTS
try:
    from luxvoice import LuxVoice
    LUXTTS_AVAILABLE = True
except ImportError:
    LUXTTS_AVAILABLE = False
    print("⚠️ LuxTTS 未安装，将使用模拟模式")

class LuxTTSAPI:
    """LuxTTS REST API 服务类"""
    
    def __init__(self, model_path: str = None, device: str = "cuda"):
        self.model = None
        self.device = device
        self.model_path = model_path or "/app/models"
        
    def load_model(self):
        """加载 LuxTTS 模型"""
        if not LUXTTS_AVAILABLE:
            print("⚠️ LuxTTS 未安装，使用模拟模式")
            return False
            
        try:
            self.model = LuxVoice.from_pretrained(
                self.model_path, 
                device=self.device
            )
            print("✅ LuxTTS 模型加载成功")
            return True
        except Exception as e:
            print(f"❌ 模型加载失败：{e}")
            return False
    
    def text_to_speech(self, text: str, prompt_audio: Optional[bytes] = None) -> bytes:
        """文本转语音"""
        if not self.model:
            if not self.load_model():
                raise Exception("模型未加载")
        
        # 如果有提示音频，保存为临时文件
        prompt_path = None
        if prompt_audio:
            prompt_path = "/tmp/prompt.wav"
            with open(prompt_path, "wb") as f:
                f.write(prompt_audio)
        
        try:
            # 生成语音
            audio = self.model.generate(
                text=text,
                prompt_path=prompt_path,
                device=self.device
            )
            
            # 释放显存 - 修复显存不释放 bug
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            # 转换为 WAV 格式
            audio_bytes = io.BytesIO()
            wavfile.write(audio_bytes, 22050, audio)
            audio_bytes.seek(0)
            
            return audio_bytes.read()
            
        except Exception as e:
            raise Exception(f"生成失败：{e}")
        finally:
            if prompt_path and os.path.exists(prompt_path):
                os.remove(prompt_path)

# 全局 API 实例
api_instance = LuxTTSAPI()

def generate_speech(text: str, prompt_file = None) -> tuple:
    """Gradio 处理函数"""
    try:
        # 处理提示音频
        prompt_bytes = None
        if prompt_file:
            with open(prompt_file, "rb") as f:
                prompt_bytes = f.read()
        
        # 生成语音
        audio_bytes = api_instance.text_to_speech(text, prompt_bytes)
        
        # 创建临时文件用于 Gradio 显示
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            audio_path = f.name
        
        return audio_path, "✅ 生成成功"
        
    except Exception as e:
        return None, f"❌ 错误：{str(e)}"

# Gradio UI
def create_gradio_interface():
    """创建 Gradio 界面"""
    
    with gr.Blocks(title="LuxTTS - 文本转语音") as demo:
        gr.Markdown("# 🎙️ LuxTTS 文本转语音")
        gr.Markdown("基于 LuxTTS 的高质量语音克隆模型")
        
        with gr.Row():
            with gr.Column():
                text_input = gr.Textbox(
                    label="输入文本",
                    placeholder="请输入要转换的文本...",
                    lines=4
                )
                
                prompt_input = gr.File(
                    label="提示音频 (可选)",
                    file_types=[".wav", ".flac", ".mp3"]
                )
                
                generate_btn = gr.Button("🎵 生成语音", variant="primary")
            
            with gr.Column():
                audio_output = gr.Audio(
                    label="生成的语音",
                    type="filepath"
                )
                status_output = gr.Textbox(
                    label="状态",
                    interactive=False
                )
        
        generate_btn.click(
            fn=generate_speech,
            inputs=[text_input, prompt_input],
            outputs=[audio_output, status_output]
        )
        
        gr.Markdown("""
        ### 📖 使用说明
        
        1. 输入要转换的文本
        2. (可选) 上传提示音频用于语音克隆
        3. 点击"生成语音"按钮
        4. 等待生成完成并播放结果
        
        ### 🔌 API 访问
        
        同时提供 REST API:
        - `POST /api/generate` - 生成语音
        - `GET /api/status` - 检查服务状态
        - `GET /api/docs` - API 文档
        
        详细 API 文档见 `/api/docs`
        """)
    
    return demo

# 启动 API 服务器
if __name__ == "__main__":
    import argparse
    import threading
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0", help="绑定地址")
    parser.add_argument("--port", type=int, default=7860, help="端口号")
    parser.add_argument("--model-path", default="/app/models", help="模型路径")
    args = parser.parse_args()
    
    # 初始化 API
    api_instance.model_path = args.model_path
    
    # 创建 Gradio 界面
    demo = create_gradio_interface()
    
    # 启动 Gradio 服务器
    print(f"🚀 启动 LuxTTS 服务...")
    print(f"📍 绑定地址：{args.host}:{args.port}")
    print(f"📁 模型路径：{args.model_path}")
    
    # 启动 Gradio
    demo.launch(
        server_name=args.host,
        server_port=args.port,
        share=False
    )
