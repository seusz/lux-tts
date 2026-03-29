"""
LuxTTS Voice Clone Web UI  ·  Gradio 6
"""
import os, time, warnings
warnings.filterwarnings("ignore")

import gradio as gr
from zipvoice.luxvoice import LuxTTS
import librosa, soundfile
import numpy as np

# ─── Model init ─────────────────────────────────────────────────────────────
MODEL_CACHE = os.path.expanduser(
    "C:/Users/Administrator/.cache/huggingface/hub/"
    "models--YatharthS--LuxTTS/snapshots/"
    "527f245a276a0eb42ea103a7a512bcfd771eb9b6"
)
REF_PATH     = "C:/Users/Administrator/.qclaw/workspace/user_voice.wav"
OUTPUT_PATH  = "C:/Users/Administrator/.qclaw/workspace/lux_output.wav"

print("Loading LuxTTS model …")
t0 = time.time()
tts = LuxTTS(model_path=MODEL_CACHE, device="cuda", threads=4)
print(f"Model loaded in {time.time()-t0:.1f}s  —  ready at http://127.0.0.1:7860")

# ─── Core synthesis ──────────────────────────────────────────────────────────
def synthesize(text, ref_audio, duration_sec, progress=gr.Progress()):
    """Encode ref → generate → return audio path + status message."""
    if not text or not text.strip():
        return None, "⚠️ 请输入要合成的文本"

    if ref_audio is None:
        return None, "⚠️ 请上传参考音频（你的声音）"

    # ── step 1: save & convert ref ─────────────────────────────────────────
    progress(0.10, desc="处理参考音频…")
    try:
        y, _ = librosa.load(ref_audio, sr=24000, duration=10)
        soundfile.write(REF_PATH, y, 24000)
    except Exception as e:
        return None, f"❌ 参考音频读取失败：{e}"

    # ── step 2: encode prompt ───────────────────────────────────────────────
    progress(0.30, desc="提取音色特征…")
    try:
        encode_dict = tts.encode_prompt(
            prompt_audio=REF_PATH,
            duration=float(duration_sec),
            rms=0.001
        )
    except Exception as e:
        return None, f"❌ 音色提取失败：{e}"

    # ── step 3: generate ────────────────────────────────────────────────────
    progress(0.60, desc="正在合成…")
    try:
        audio = tts.generate_speech(text=text.strip(), encode_dict=encode_dict)
    except Exception as e:
        return None, f"❌ 合成失败：{e}"

    # ── step 4: save output ─────────────────────────────────────────────────
    out_np = audio.squeeze().cpu().numpy()
    soundfile.write(OUTPUT_PATH, out_np, 48000)

    audio_dur  = len(out_np) / 48000
    total_time = time.time() - t0
    rtf         = total_time / audio_dur
    msg = (f"✅ {audio_dur:.1f}s 合成完成 / 耗时 {total_time:.1f}s "
           f"/ RTF={rtf:.2f} ({1/rtf:.1f}x realtime)")

    return OUTPUT_PATH, msg

# ─── Theme & CSS ────────────────────────────────────────────────────────────
MAIN_CSS = """
:root {
    --bg-primary:   #0d0d14;
    --bg-secondary: #13131e;
    --bg-card:      #181825;
    --accent:       #7c6af7;
    --accent-glow:  rgba(124,106,247,0.35);
    --accent2:      #f76a8a;
    --text:         #e8e8f0;
    --text-muted:   #7070a0;
    --border:       #2a2a3d;
}
* { font-family: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei', sans-serif;
    box-sizing: border-box; }
body, .gradio-container { background: var(--bg-primary) !important; color: var(--text); }
.main { max-width: 900px; margin: 0 auto; padding: 0 16px 40px; }

/* Header */
.header { text-align: center; padding: 40px 0 32px; }
.header h1 {
    font-size: 2.2rem; font-weight: 700; margin: 0 0 8px;
    background: linear-gradient(120deg, #7c6af7 0%, #f76a8a 60%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
}
.header p { color: var(--text-muted); font-size: 0.95rem; margin: 0; }

/* Card */
.card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 24px 28px;
    margin-bottom: 16px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}

/* Labels */
.label { font-size: 0.75rem; font-weight: 600;
    letter-spacing: 1.4px; text-transform: uppercase;
    color: var(--accent); margin-bottom: 12px; display: block; }

/* Inputs */
textarea, input[type=text] {
    background: var(--bg-secondary) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
    font-size: 1rem !important;
    padding: 14px 18px !important;
    resize: vertical !important;
    transition: border-color 0.2s, box-shadow 0.2s;
}
textarea:focus, input[type=text]:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-glow) !important;
    outline: none !important;
}
textarea::placeholder { color: var(--text-muted) !important; }

/* Slider */
input[type=range"] { accent-color: var(--accent) !important; }

/* Audio */
.audio-player audio { width: 100% !important; border-radius: 10px; }
.audio-container { border-radius: 12px !important; overflow: hidden; }

/* Button */
.btn {
    background: linear-gradient(135deg, #7c6af7 0%, #9b6af7 100%) !important;
    border: none !important; border-radius: 14px !important;
    color: white !important; font-weight: 600 !important;
    font-size: 1.05rem !important; padding: 16px 32px !important;
    cursor: pointer; width: 100%; margin-top: 16px;
    transition: transform 0.15s, box-shadow 0.15s;
    box-shadow: 0 4px 20px rgba(124,106,247,0.4);
}
.btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 28px rgba(124,106,247,0.5) !important;
}
.btn:active { transform: translateY(0); }

/* Status */
.status {
    background: var(--bg-secondary); border: 1px solid var(--border);
    border-radius: 12px; padding: 14px 18px;
    font-size: 0.9rem; min-height: 48px;
    display: flex; align-items: center;
}
.status.ok   { color: #6fdb8a; border-color: rgba(111,219,138,0.3); }
.status.warn { color: #f7c76a; border-color: rgba(247,199,106,0.3); }
.status.err  { color: var(--accent2); border-color: rgba(247,106,138,0.3); }

/* Divider */
.divider { height: 1px; background: var(--border); margin: 4px 0 20px; }

/* Footer */
.footer { text-align: center; padding: 20px;
    color: var(--text-muted); font-size: 0.8rem; }
.footer span { color: var(--accent); }

/* Responsive */
@media (max-width: 600px) {
    .header h1 { font-size: 1.6rem; }
    .card { padding: 16px; border-radius: 14px; }
}
"""

# ─── Build UI ───────────────────────────────────────────────────────────────
with gr.Blocks(css=MAIN_CSS, title="LuxTTS 语音克隆") as demo:

    gr.HTML("""<div class="header">
        <h1>🎙️ LuxTTS 语音克隆</h1>
        <p>上传你的声音 &nbsp;·&nbsp; 输入任意文本 &nbsp;·&nbsp; 合成 48kHz 高保真语音</p>
    </div>""")

    with gr.Column(elem_classes="main"):

        # ── Row: Left (ref) / Right (text) ──────────────────────────────────
        with gr.Row():
            # Left column: reference audio + settings
            with gr.Column(scale=1, min_width=300):
                with gr.Group():
                    gr.HTML('<div class="card">')
                    gr.HTML('<span class="label">🎵 参考音频（你的声音）</span>')
                    ref_audio = gr.Audio(
                        label=None, type="filepath",
                        sources=["upload"],
                    )
                    gr.HTML('<span style="font-size:0.78rem;color:var(--text-muted)">'
                            '支持 WAV/MP3/OGG，建议 5-10 秒，语音清晰无噪声</span>')
                    gr.HTML('</div>')

                with gr.Group():
                    gr.HTML('<div class="card">')
                    gr.HTML('<span class="label">⚙️ 采样时长</span>')
                    duration_slider = gr.Slider(
                        minimum=3, maximum=10, value=8, step=0.5,
                        info="从参考音频中采样多少秒用于音色提取",
                    )
                    gr.HTML('</div>')

            # Right column: text + button + output
            with gr.Column(scale=1, min_width=340):
                with gr.Group():
                    gr.HTML('<div class="card">')
                    gr.HTML('<span class="label">✏️ 合成文本</span>')
                    text_input = gr.Textbox(
                        label=None,
                        placeholder="输入你想让 LuxTTS 说的话…\n例如：你好，这是我用自己声音克隆出来的语音。",
                        lines=6, max_lines=12,
                    )
                    gr.HTML('</div>')

                generate_btn = gr.Button("🚀 开始合成", elem_classes="btn")

                status_html = gr.HTML(
                    '<div class="status warn">👆 上传参考音频并输入文本后，点击上方按钮开始合成</div>'
                )

                with gr.Group():
                    gr.HTML('<div class="card">')
                    gr.HTML('<span class="label">🔊 合成结果</span>')
                    output_audio = gr.Audio(
                        label=None, type="filepath",
                        interactive=False,
                    )
                    gr.HTML('</div>')

        gr.HTML("""<div class="footer">
            Powered by <span>LuxTTS</span> · ZipVoice 架构 · Whisper ASR + LinaCodec
        </div>""")

    # ─── Event wiring ───────────────────────────────────────────────────────
    def on_click(text, ref, dur):
        audio, msg = synthesize(text, ref, dur)
        cls = "ok" if audio else ("err" if msg.startswith("❌") else "warn")
        return (
            audio,
            f'<div class="status {cls}">{msg}</div>'
        )

    generate_btn.click(
        fn=on_click,
        inputs=[text_input, ref_audio, duration_slider],
        outputs=[output_audio, status_html],
        show_progress="full",
    )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True,
        share=False,
        max_threads=4,
    )
