"""
Prueba de velocidad y pasos de síntesis.
Compara calidad/velocidad variando total_steps y speed.
"""
import time
from supertonic import TTS

tts = TTS(auto_download=True)
style = tts.get_voice_style(voice_name="M1")

text = "This is a speed and quality benchmark test for Supertonic."

configs = [
    {"total_steps": 4,  "speed": 1.0,  "label": "rapido_4steps"},
    {"total_steps": 8,  "speed": 1.0,  "label": "normal_8steps"},
    {"total_steps": 16, "speed": 1.0,  "label": "calidad_16steps"},
    {"total_steps": 8,  "speed": 1.5,  "label": "veloz_150pct"},
    {"total_steps": 8,  "speed": 0.75, "label": "lento_75pct"},
]

for cfg in configs:
    inicio = time.time()
    wav, duration = tts.synthesize(
        text=text,
        lang="en",
        voice_style=style,
        total_steps=cfg["total_steps"],
        speed=cfg["speed"],
    )
    elapsed = time.time() - inicio
    archivo = f"output_{cfg['label']}.wav"
    tts.save_audio(wav, archivo)
    print(f"[{cfg['label']}] audio={duration[0]:.2f}s | tiempo={elapsed:.2f}s | RTF={elapsed/duration[0]:.2f}")
