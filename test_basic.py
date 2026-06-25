"""
Prueba básica de Supertonic TTS.
Genera un archivo output.wav con texto en inglés.
"""
from supertonic import TTS

tts = TTS(auto_download=True)
style = tts.get_voice_style(voice_name="M1")

text = "Hello, this is a basic test of Supertonic text to speech."

wav, duration = tts.synthesize(
    text=text,
    lang="en",
    voice_style=style,
    total_steps=8,
    speed=1.3,
)

tts.save_audio(wav, "output_basic.wav")
print(f"Listo. Audio generado: {duration[0]:.2f} segundos -> output_basic.wav")
