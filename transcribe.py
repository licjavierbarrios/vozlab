"""
STT (Speech To Text) con whisper.cpp.

Usa el binario precompilado `whisper-cli.exe` (mismo patrón que el `ffmpeg.exe`
ya bundleado): normaliza el audio a 16 kHz mono WAV con ffmpeg, asegura el modelo
GGML descargándolo de Hugging Face bajo demanda, y ejecuta whisper.cpp por subprocess.
100% local, CPU, sin PyTorch.
"""
import os
import subprocess
import tempfile

from huggingface_hub import hf_hub_download

BASE_DIR = os.path.dirname(__file__)
WHISPER_DIR = os.path.join(BASE_DIR, "whisper")
MODELS_DIR = os.path.join(WHISPER_DIR, "models")
FFMPEG = os.path.join(BASE_DIR, "ffmpeg.exe")

# Repo oficial de modelos GGML de whisper.cpp en Hugging Face.
HF_REPO = "ggerganov/whisper.cpp"

MODEL_SIZES = ["tiny", "base", "small", "medium"]
DEFAULT_MODEL = "small"

# En releases recientes el ejecutable se llama whisper-cli.exe; antes era main.exe.
_BIN_NAMES = ["whisper-cli.exe", "main.exe"]

# Evita abrir una ventana de consola por cada subprocess en Windows.
_NO_WINDOW = 0x08000000 if os.name == "nt" else 0


def whisper_bin_path():
    """Devuelve la ruta al binario de whisper.cpp o lanza un error claro si falta."""
    for name in _BIN_NAMES:
        candidate = os.path.join(WHISPER_DIR, name)
        if os.path.isfile(candidate):
            return candidate
    raise FileNotFoundError(
        "No se encontró whisper-cli.exe. Ejecuta primero:\n"
        "    python setup_whisper.py\n"
        "para descargar el binario de whisper.cpp."
    )


def ensure_model(model_size=DEFAULT_MODEL):
    """Descarga (si hace falta) el modelo GGML y devuelve su ruta local."""
    if model_size not in MODEL_SIZES:
        raise ValueError(f"Modelo no soportado: {model_size}. Usa uno de {MODEL_SIZES}.")
    os.makedirs(MODELS_DIR, exist_ok=True)
    filename = f"ggml-{model_size}.bin"
    return hf_hub_download(repo_id=HF_REPO, filename=filename, local_dir=MODELS_DIR)


def _to_wav16k(audio_path):
    """Convierte cualquier audio a 16 kHz mono PCM s16le (requisito de whisper.cpp)."""
    fd, wav_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    cmd = [
        FFMPEG, "-i", audio_path,
        "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le",
        "-y", wav_path,
    ]
    subprocess.run(
        cmd, check=True, capture_output=True,
        creationflags=_NO_WINDOW,
    )
    return wav_path


def transcribe(audio_path, model_size=DEFAULT_MODEL, language="auto"):
    """
    Transcribe un archivo de audio a texto.

    audio_path: ruta a cualquier formato de audio (mp3, wav, m4a, ...).
    model_size: tiny | base | small | medium.
    language: código ISO (es, en, ...) o "auto" para autodetectar.
    """
    if not audio_path or not os.path.isfile(audio_path):
        raise FileNotFoundError(f"No se encontró el audio: {audio_path}")

    binary = whisper_bin_path()
    model = ensure_model(model_size)
    wav_path = _to_wav16k(audio_path)

    out_fd, out_base = tempfile.mkstemp(suffix=".whisper")
    os.close(out_fd)
    txt_path = out_base + ".txt"

    try:
        cmd = [
            binary,
            "-m", model,
            "-f", wav_path,
            "-l", language or "auto",
            "-otxt",
            "-of", out_base,
        ]
        subprocess.run(
            cmd, check=True, capture_output=True,
            creationflags=_NO_WINDOW,
        )
        with open(txt_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    finally:
        for p in (wav_path, txt_path, out_base):
            try:
                os.remove(p)
            except OSError:
                pass
