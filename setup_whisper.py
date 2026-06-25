"""
Instalación de binarios (de un solo uso).

Descarga lo que no resuelve pip:
- `ffmpeg.exe` (build de Windows) a la raíz del proyecto.
- el binario precompilado de whisper.cpp para Windows x64, extraído en `whisper/`.
- el modelo GGML por defecto de Whisper.

Si prefieres hacerlo a mano:
- ffmpeg: descarga `ffmpeg-release-essentials.zip` desde https://www.gyan.dev/ffmpeg/builds/
  y copia `bin\\ffmpeg.exe` a la raíz del proyecto.
- whisper: descarga `whisper-bin-x64.zip` desde
  https://github.com/ggerganov/whisper.cpp/releases y copia whisper-cli.exe
  (y sus .dll) a la carpeta `whisper/`.
"""
import io
import json
import os
import urllib.request
import zipfile

import transcribe

GITHUB_API = "https://api.github.com/repos/ggerganov/whisper.cpp/releases/latest"
FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"


def download_ffmpeg():
    """Descarga ffmpeg.exe a la raíz del proyecto si no está ya presente."""
    if os.path.isfile(transcribe.FFMPEG):
        print(f"ffmpeg.exe ya existe: {transcribe.FFMPEG}")
        return

    print("Descargando ffmpeg (build de Windows)...")
    req = urllib.request.Request(FFMPEG_URL, headers={"User-Agent": "supertonic-setup"})
    with urllib.request.urlopen(req) as resp:
        data = resp.read()

    print("Extrayendo ffmpeg.exe...")
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        member = next(
            (m for m in zf.namelist() if os.path.basename(m).lower() == "ffmpeg.exe"),
            None,
        )
        if not member:
            raise RuntimeError(
                "No se encontró ffmpeg.exe en el zip descargado. Descárgalo a mano "
                "desde https://www.gyan.dev/ffmpeg/builds/ y copia bin\\ffmpeg.exe a la raíz."
            )
        with zf.open(member) as src, open(transcribe.FFMPEG, "wb") as dst:
            dst.write(src.read())
    print(f"ffmpeg listo: {transcribe.FFMPEG}")


def _find_windows_asset(release):
    """Elige el zip de binarios Windows x64 (CPU) entre los assets del release."""
    assets = release.get("assets", [])
    # Preferencia: build CPU plano "whisper-bin-x64.zip". Evita variantes blas/cublas/clblast.
    def score(name):
        n = name.lower()
        if not (n.endswith(".zip") and "x64" in n and "bin" in n):
            return -1
        if any(v in n for v in ("blas", "cublas", "clblast", "cuda", "arm")):
            return 1
        return 2

    best = None
    best_score = 0
    for a in assets:
        s = score(a.get("name", ""))
        if s > best_score:
            best, best_score = a, s
    return best


def download_binary():
    os.makedirs(transcribe.WHISPER_DIR, exist_ok=True)

    print("Consultando el último release de whisper.cpp...")
    req = urllib.request.Request(GITHUB_API, headers={"User-Agent": "supertonic-setup"})
    with urllib.request.urlopen(req) as resp:
        release = json.load(resp)

    asset = _find_windows_asset(release)
    if not asset:
        raise RuntimeError(
            "No se encontró un asset de Windows x64 en el último release.\n"
            "Descárgalo a mano desde "
            "https://github.com/ggerganov/whisper.cpp/releases y copia "
            "whisper-cli.exe + .dll a la carpeta whisper/."
        )

    name = asset["name"]
    url = asset["browser_download_url"]
    print(f"Descargando {name} ({release.get('tag_name', '')})...")
    req = urllib.request.Request(url, headers={"User-Agent": "supertonic-setup"})
    with urllib.request.urlopen(req) as resp:
        data = resp.read()

    print("Extrayendo whisper-cli.exe y librerías...")
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        for member in zf.namelist():
            base = os.path.basename(member)
            if not base:
                continue
            if base.endswith(".exe") or base.endswith(".dll"):
                target = os.path.join(transcribe.WHISPER_DIR, base)
                with zf.open(member) as src, open(target, "wb") as dst:
                    dst.write(src.read())

    # Confirma que el binario quedó disponible (lanza error claro si no).
    binary = transcribe.whisper_bin_path()
    print(f"Binario listo: {binary}")


def main():
    download_ffmpeg()
    download_binary()
    print(f"Descargando modelo '{transcribe.DEFAULT_MODEL}' (puede tardar)...")
    model = transcribe.ensure_model(transcribe.DEFAULT_MODEL)
    print(f"Modelo listo: {model}")
    print("\nSetup completo. Ya puedes ejecutar: python app.py")


if __name__ == "__main__":
    main()
