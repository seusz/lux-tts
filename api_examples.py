"""
LuxTTS API 使用示例
展示如何使用 REST API 调用 LuxTTS
"""

import requests
import base64
import json

# API 配置
API_BASE_URL = "http://localhost:8000"  # 修改为你的服务器地址

def check_health():
    """检查服务健康状态"""
    response = requests.get(f"{API_BASE_URL}/health")
    print("📊 健康检查:")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def get_api_docs():
    """获取 API 文档"""
    response = requests.get(f"{API_BASE_URL}/api/docs")
    print("📚 API 文档:")
    print(json.dumps(response.json(), indent=2))
    return response.json()

def generate_speech(text, prompt_audio_path=None):
    """
    生成语音
    
    Args:
        text: 要转换的文本
        prompt_audio_path: 提示音频文件路径 (可选)
    
    Returns:
        WAV 音频文件
    """
    url = f"{API_BASE_URL}/api/generate"
    
    # 准备请求数据
    data = {
        "text": text,
        "speed": 1.0
    }
    
    files = {}
    if prompt_audio_path:
        with open(prompt_audio_path, "rb") as f:
            files["prompt_audio"] = ("prompt.wav", f, "audio/wav")
    
    print(f"🎤 生成语音：{text[:50]}...")
    
    try:
        response = requests.post(url, data=data, files=files, timeout=120)
        response.raise_for_status()
        
        # 保存音频文件
        output_file = "output.wav"
        with open(output_file, "wb") as f:
            f.write(response.content)
        
        print(f"✅ 语音生成成功！保存为：{output_file}")
        return output_file
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败：{e}")
        return None

def generate_speech_with_base64(text, prompt_audio_base64):
    """
    使用 base64 编码的提示音频生成语音
    
    Args:
        text: 要转换的文本
        prompt_audio_base64: base64 编码的音频数据
    """
    url = f"{API_BASE_URL}/api/generate"
    
    data = {
        "text": text,
        "prompt_audio": prompt_audio_base64,
        "speed": 1.0
    }
    
    print(f"🎤 生成语音 (带提示音频): {text[:50]}...")
    
    try:
        response = requests.post(url, json=data, timeout=120)
        response.raise_for_status()
        
        output_file = "output_base64.wav"
        with open(output_file, "wb") as f:
            f.write(response.content)
        
        print(f"✅ 语音生成成功！保存为：{output_file}")
        return output_file
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败：{e}")
        return None

def batch_generate_speech(texts, prompt_audio_path=None):
    """
    批量生成语音
    
    Args:
        texts: 文本列表
        prompt_audio_path: 提示音频文件路径 (可选)
    """
    print(f"🎤 批量生成 {len(texts)} 个语音...")
    
    results = []
    for i, text in enumerate(texts, 1):
        print(f"\n[{i}/{len(texts)}] 处理：{text[:30]}...")
        output_file = generate_speech(text, prompt_audio_path)
        results.append({
            "text": text,
            "output": output_file,
            "status": "success" if output_file else "failed"
        })
    
    print(f"\n✅ 批量生成完成！")
    return results

# 使用示例
if __name__ == "__main__":
    print("=" * 60)
    print("🎙️ LuxTTS API 使用示例")
    print("=" * 60)
    
    # 1. 检查服务状态
    print("\n1️⃣ 检查服务状态")
    check_health()
    
    # 2. 获取 API 文档
    print("\n2️⃣ 获取 API 文档")
    get_api_docs()
    
    # 3. 生成简单语音
    print("\n3️⃣ 生成简单语音")
    generate_speech("你好，世界！这是一个测试。")
    
    # 4. 批量生成语音
    print("\n4️⃣ 批量生成语音")
    texts = [
        "早上好，今天天气真好。",
        "下午好，工作愉快！",
        "晚上好，祝你有个美好的夜晚。"
    ]
    batch_generate_speech(texts)
    
    # 5. 使用提示音频 (如果有)
    print("\n5️⃣ 使用提示音频生成语音")
    # generate_speech("使用提示音频克隆的声音", "prompt.wav")
    
    print("\n" + "=" * 60)
    print("✅ 示例完成！")
    print("=" * 60)
