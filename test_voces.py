"""
Prueba de múltiples voces disponibles en Supertonic.
Genera un .wav por cada voz con el mismo texto.
"""
from supertonic import TTS

tts = TTS(auto_download=True)

text = "Testing voice number"
voces = ["M1", "M2", "F1", "F2"]

for nombre in voces:
    try:
        style = tts.get_voice_style(voice_name=nombre)
        wav, duration = tts.synthesize(
            text=f"{text} {nombre}",
            lang="en",
            voice_style=style,
            total_steps=8,
            speed=1.0,
        )
        archivo = f"output_{nombre}.wav"
        tts.save_audio(wav, archivo)
        print(f"[OK] Voz {nombre} -> {archivo} ({duration[0]:.2f}s)")
    except Exception as e:
        print(f"[ERROR] Voz {nombre}: {e}")
