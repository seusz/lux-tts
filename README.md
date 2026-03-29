# LuxTTS 语音克隆

基于 [LuxTTS](https://github.com/ysharma3501/LuxTTS) 的轻量级语音克隆工具，支持用少量参考音频克隆音色，生成任意文本的中文/英文语音。

## 特性

| 特性 | 说明 |
|------|------|
| 轻量化 | 仅需 **1GB 显存**（RTX 2060 完全够用） |
| 高音质 | 输出 **48kHz** 音频（普通 TTS 的 2 倍采样率） |
| 极速推理 | GPU 推理约 **3 倍实时** |
| 零样本克隆 | 仅需 **3~5 秒** 参考音频即可克隆音色 |
| 中文支持 | 完整支持中文文本合成 |
| 多接口 | Web 界面 / API / 命令行多种使用方式 |

## 文件说明

| 文件 | 说明 |
|------|------|
| `lux_ui.py` | Gradio 网页界面（推荐日常使用） |
| `lux_api.py` | FastAPI 后端服务（SillyTavern 等应用调用） |
| `start_lux_ui.bat` | 双击启动 Gradio Web 界面 |
| `start_lux_api.bat` | 双击启动 API 服务 |
| `user_voice.wav` | 你的声音参考音频（可替换） |
| `_tts_direct.py` | 命令行直接生成脚本（开发调试用） |

## 快速开始

### 方式一：Web 界面（推荐）

双击 `start_lux_ui.bat`，浏览器自动打开 `http://127.0.0.1:7860`。

上传参考音频 → 输入文本 → 点击合成。

### 方式二：API 服务（SillyTavern 等）

双击 `start_lux_api.bat`，服务启动于 `http://0.0.0.0:8080`。

### SillyTavern 配置

```
API 格式:     OpenAI
API 地址:    http://192.168.8.76:8080
API Key:    （留空）
模型名:     lux-tts
```

上传你的参考音频 `.wav` 到 SillyTavern 的语音设置中即可。

### 方式三：命令行直接生成

```bash
conda activate luxtts
cd C:\Users\Administrator\.qclaw\workspace\LuxTTS-Project
python _tts_direct.py
```

修改脚本中的 `ref_path` 和 `text` 变量即可生成不同内容。

## API 文档

### 语音合成

```
POST /v1/audio/speech  (form-data)
POST /v1/audio/speech/json  (JSON body)
```

**请求参数（form-data）：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `text` | string | ✅ | 要合成的文本 |
| `ref_audio` | file | ✅ | 参考音频文件（.wav/.mp3） |
| `speed` | float | ❌ | 语速，默认 1.0 |
| `num_steps` | int | ❌ | 推理步数，默认 4（越大越慢质量越高） |
| `guidance_scale` | float | ❌ | 引导强度，默认 3.0 |
| `t_shift` | float | ❌ | 音调偏移，默认 0.5 |

**响应：** 返回 WAV 音频文件（48kHz, 16bit, 单声道）。

**示例（curl）：**
```bash
curl -X POST http://192.168.8.76:8080/v1/audio/speech \
  -F "text=你好，这是一段语音克隆测试" \
  -F "ref_audio=@user_voice.wav" \
  -F "speed=1.0" \
  --output output.wav
```

**示例（Python）：**
```python
import requests

with open("user_voice.wav", "rb") as f:
    resp = requests.post(
        "http://192.168.8.76:8080/v1/audio/speech",
        files={"ref_audio": f},
        data={"text": "你好，这是一段语音克隆测试", "speed": 1.0}
    )
with open("output.wav", "wb") as f:
    f.write(resp.content)
```

### 其他端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/v1/models` | GET | 返回可用模型列表 |

## 环境要求

| 项目 | 最低要求 |
|------|---------|
| 显存 | 1GB（推荐 4GB+） |
| 内存 | 4GB+ |
| 硬盘 | 2GB 可用空间 |
| Python | 3.10+ |
| CUDA | 11.8+（支持 GPU 加速） |

## 已知问题

| 问题 | 说明 | 解决方案 |
|------|------|---------|
| `k2` 未安装 | Swoosh 降级到 PyTorch 实现 | 可接受，速度稍慢 |
| 首次下载模型慢 | HuggingFace 连接不稳定 | 设置镜像或提前缓存 |
| Gradio 中文乱码 | Windows 控制台编码问题 | 不影响功能，界面正常显示 |
| pydub 找不到 ffmpeg | soundfile 已替代，不影响 | 可忽略 |

## 自定义参考音频

替换 `user_voice.wav` 为你自己的录音即可。参考音频要求：

- 时长：3~10 秒为宜
- 格式：WAV/MP3
- 内容：清晰人声，背景安静
- 采样率：24kHz 以上均可

## 开源许可

本项目基于 [LuxTTS](https://github.com/ysharma3501/LuxTTS) 和 [ZipVoice](https://github.com/ysharma3501/ZipVoice) 构建，遵守其对应的开源协议。
