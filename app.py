import os
import sys
import tempfile
import traceback
from functools import wraps
import numpy as np
import gradio as gr
from pydub import AudioSegment
from supertonic import TTS

import transcribe
import pdf_text


# En Windows, el ProactorEventLoop de asyncio lanza un ConnectionResetError
# (WinError 10054) ruidoso e inofensivo cuando el navegador cierra una conexión.
# Lo silenciamos parcheando el callback interno. (set_exception_handler no sirve:
# uvicorn corre en su propio event loop, no en el del momento de importación.)
if sys.platform == "win32":
    from asyncio.proactor_events import _ProactorBasePipeTransport

    def _silence_connection_reset(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except ConnectionResetError:
                pass
        return wrapper

    _ProactorBasePipeTransport._call_connection_lost = _silence_connection_reset(
        _ProactorBasePipeTransport._call_connection_lost
    )

AudioSegment.converter = os.path.join(os.path.dirname(__file__), "ffmpeg.exe")

tts = TTS(auto_download=True)

LANGUAGES = {
    "Español (es)": "es",
    "English (en)": "en",
    "हिन्दी — Hindi (hi)": "hi",
    "العربية — Arabic (ar)": "ar",
    "Français (fr)": "fr",
    "Русский — Russian (ru)": "ru",
    "Português (pt)": "pt",
    "Bahasa Indonesia (id)": "id",
    "Deutsch (de)": "de",
    "日本語 — Japanese (ja)": "ja",
}

VOICES = ["M1", "M2", "M3", "M4", "M5", "F1", "F2", "F3", "F4", "F5"]

# Idiomas para la transcripción: igual que TTS pero con autodetección al inicio.
STT_LANGUAGES = {"Auto-detectar": "auto", **LANGUAGES}

WHISPER_MODELS = transcribe.MODEL_SIZES  # tiny, base, small, medium

BTN_GENERATING = gr.update(interactive=False, value="Generando...")
BTN_READY = gr.update(interactive=True, value="Generar Audio")

BTN_TRANSCRIBE_BUSY = gr.update(interactive=False, value="Transcribiendo...")
BTN_TRANSCRIBE_READY = gr.update(interactive=True, value="Transcribir")

BTN_EXTRACT_BUSY = gr.update(interactive=False, value="Extrayendo...")
BTN_EXTRACT_READY = gr.update(interactive=True, value="Extraer texto")


def do_transcribe(audio_path, model_size, language_label):
    # outputs: editor (de esta pestaña), status, transcribe_btn
    if not audio_path:
        yield gr.update(), "Sube un archivo de audio primero.", BTN_TRANSCRIBE_READY
        return
    yield gr.update(), "Transcribiendo audio... (puede tardar)", BTN_TRANSCRIBE_BUSY
    try:
        lang_code = STT_LANGUAGES[language_label]
        text = transcribe.transcribe(audio_path, model_size=model_size, language=lang_code)
        yield text, f"Transcripción lista ({len(text)} caracteres). Revísala y edítala abajo.", BTN_TRANSCRIBE_READY
    except Exception as e:
        traceback.print_exc()
        yield gr.update(), f"Error: {e}", BTN_TRANSCRIBE_READY


def do_extract_pdf(pdf_file):
    # outputs: editor (de esta pestaña), status, extract_btn, pdf_input
    if not pdf_file:
        yield gr.update(), "Sube un PDF primero.", BTN_EXTRACT_READY, gr.update()
        return
    if not pdf_file.lower().endswith(".pdf"):
        # Archivo equivocado (p. ej. un audio): avisa y limpia el área de carga.
        yield gr.update(), "El archivo subido no es un PDF. Sube un archivo .pdf.", BTN_EXTRACT_READY, gr.update(value=None)
        return
    yield gr.update(), "Extrayendo texto del PDF...", BTN_EXTRACT_BUSY, gr.update()
    try:
        text = pdf_text.extract_text(pdf_file)
        if not text:
            yield gr.update(), "El PDF no contiene texto extraíble (¿es un PDF escaneado?).", BTN_EXTRACT_READY, gr.update(value=None)
            return
        yield text, f"Texto extraído ({len(text)} caracteres). Revísalo y edítalo abajo.", BTN_EXTRACT_READY, gr.update()
    except Exception as e:
        traceback.print_exc()
        yield gr.update(), f"No se pudo leer el PDF: {e}", BTN_EXTRACT_READY, gr.update(value=None)


def generate_audio(text, language_label, voice_name, total_steps, speed):
    if not text or not text.strip():
        yield None, "El texto no puede estar vacío.", BTN_READY
        return

    yield None, "Generando audio...", BTN_GENERATING

    try:
        lang_code = LANGUAGES[language_label]
        style = tts.get_voice_style(voice_name)

        wav, duration = tts.synthesize(
            text=text,
            voice_style=style,
            total_steps=int(total_steps),
            speed=float(speed),
            lang=lang_code,
        )

        pcm = (wav.squeeze() * 32767).astype(np.int16).tobytes()
        segment = AudioSegment(
            data=pcm,
            sample_width=2,
            frame_rate=tts.sample_rate,
            channels=1,
        )
        fd, tmp_path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)
        segment.export(tmp_path, format="mp3", bitrate="128k")

        yield tmp_path, f"Audio generado: {duration[0]:.2f} segundos", BTN_READY

    except Exception as e:
        traceback.print_exc()
        yield None, f"Error: {e}", BTN_READY


def tts_section():
    """Crea la sección 'Texto → Audio' completa (editor + controles + Generar)
    y cablea su propio botón. Devuelve (editor, status) para que quien la use
    pueda volcar texto y mensajes en ella."""
    text_input = gr.Textbox(
        label="Texto",
        placeholder="Pega aquí el texto que quieres convertir a audio...",
        lines=12,
    )
    with gr.Row():
        language = gr.Dropdown(
            label="Idioma",
            choices=list(LANGUAGES.keys()),
            value="Español (es)",
        )
        voice = gr.Dropdown(
            label="Voz",
            choices=VOICES,
            value="M1",
        )
        total_steps = gr.Slider(
            label="Calidad (pasos de difusión)",
            minimum=1,
            maximum=30,
            step=1,
            value=8,
        )
        speed = gr.Slider(
            label="Velocidad",
            minimum=0.7,
            maximum=2.0,
            step=0.05,
            value=1.35,
        )
    generate_btn = gr.Button("Generar Audio", variant="primary", size="lg")
    audio_output = gr.Audio(label="Audio generado", type="filepath")
    status = gr.Textbox(label="Estado", interactive=False, lines=1)

    generate_btn.click(
        fn=generate_audio,
        inputs=[text_input, language, voice, total_steps, speed],
        outputs=[audio_output, status, generate_btn],
    )
    return text_input, status


with gr.Blocks(title="VozLab — Audio ↔ Texto ↔ Audio") as demo:
    gr.Markdown("# VozLab — Audio ↔ Texto ↔ Audio")

    with gr.Tabs():
        # ── Audio → Texto (+ Texto → Audio abajo) ────────────────────────────
        with gr.Tab("Audio → Texto"):
            with gr.Row():
                with gr.Column(scale=2):
                    stt_audio = gr.Audio(label="Audio a transcribir", type="filepath")
                with gr.Column(scale=1):
                    stt_model = gr.Dropdown(
                        label="Modelo Whisper",
                        choices=WHISPER_MODELS,
                        value=transcribe.DEFAULT_MODEL,
                    )
                    stt_language = gr.Dropdown(
                        label="Idioma del audio",
                        choices=list(STT_LANGUAGES.keys()),
                        value="Auto-detectar",
                    )
            transcribe_btn = gr.Button("Transcribir", variant="secondary")

            gr.Markdown("### Texto → Audio")
            audio_editor, audio_status = tts_section()

            transcribe_btn.click(
                fn=do_transcribe,
                inputs=[stt_audio, stt_model, stt_language],
                outputs=[audio_editor, audio_status, transcribe_btn],
            )

        # ── PDF → Texto (+ Texto → Audio abajo) ──────────────────────────────
        with gr.Tab("PDF → Texto"):
            pdf_input = gr.File(label="PDF", type="filepath")
            extract_btn = gr.Button("Extraer texto", variant="secondary")

            gr.Markdown("### Texto → Audio")
            pdf_editor, pdf_status = tts_section()

            extract_btn.click(
                fn=do_extract_pdf,
                inputs=[pdf_input],
                outputs=[pdf_editor, pdf_status, extract_btn, pdf_input],
            )

        # ── Texto → Audio (versión limpia y sola) ────────────────────────────
        with gr.Tab("Texto → Audio"):
            tts_section()

demo.launch(inbrowser=True)
