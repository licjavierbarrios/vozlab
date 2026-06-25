# VozLab — Audio ↔ Texto ↔ Audio

**VozLab** es una plataforma local para **transcribir audio**, **extraer texto de PDF**, editarlo y **generar audio nuevo**. Combina:

- [Supertonic](https://github.com/supertone-inc/supertonic) — TTS (Texto → Audio) rápido y local sobre ONNX Runtime.
- [whisper.cpp](https://github.com/ggerganov/whisper.cpp) — STT (Audio → Texto) local, vía binario nativo.

Todo en CPU, sin PyTorch.

## Flujo

```
Audio  ─(whisper.cpp)──►  Texto  ─(editar)─►  Supertonic  ─►  Audio nuevo
PDF    ─(extraer)─────►   Texto  ─(editar)─►  Supertonic  ─►  Audiolibro
```

Casos de uso: doblaje básico, cambiar de locutor, regenerar audios, narraciones y audiolibros desde PDF.

## Requisitos

- Python 3.10+

`ffmpeg.exe` (para exportar MP3 y normalizar el audio de Whisper) y el binario de whisper.cpp
**no se versionan** por su tamaño, pero `setup_whisper.py` los descarga automáticamente (ver
Instalación). No necesitás bajar nada a mano.

## Instalación

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python setup_whisper.py
```

`setup_whisper.py` descarga `ffmpeg.exe` a la raíz del proyecto, el binario de whisper.cpp para
Windows x64 y el modelo `small`. (Los modelos de Supertonic, ~500 MB, se descargan de Hugging
Face la primera vez que se ejecuta la app.)

> También podés ejecutar **`instalar.bat`**, que hace todo: crea el venv, instala las
> dependencias y corre `setup_whisper.py`.

> **Descarga manual de ffmpeg** (alternativa): baja `ffmpeg-release-essentials.zip` desde
> [gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/) y copia `bin\ffmpeg.exe` a la
> raíz del proyecto (junto a `app.py`).

> **Descarga manual del binario de whisper.cpp** (alternativa): baja `whisper-bin-x64.zip`
> desde los [releases de whisper.cpp](https://github.com/ggerganov/whisper.cpp/releases) y copia
> `whisper-cli.exe` + sus `.dll` a la carpeta `whisper/`.

## Uso

Doble clic en **`ejecutar.bat`** (arranca la app sin tocar la consola), o desde la terminal:

```bash
python app.py
```

La app abre el navegador sola en `http://127.0.0.1:7860`. Hay tres pestañas independientes:

1. **Audio → Texto**: sube un audio, elige modelo e idioma y pulsa *Transcribir*. El texto
   aparece en la sección *Texto → Audio* de esa misma pestaña, listo para editar y generar.
2. **PDF → Texto**: sube un PDF y pulsa *Extraer texto*. El texto cae igual en la sección
   *Texto → Audio* de abajo.
3. **Texto → Audio**: pega texto directamente y genera audio, sin pasos de importación.

En las tres pestañas, debajo tienes el editor + controles de voz/idioma/calidad/velocidad y el
botón *Generar Audio*.

## Características

- **STT** con whisper.cpp: modelos `tiny`, `base`, `small`, `medium`; autodetección de idioma.
- **PDF → audiolibro**: extracción de texto con pypdf.
- Tres pestañas independientes (Audio→Texto, PDF→Texto, Texto→Audio), cada una con su propia
  generación de audio.
- 10 idiomas (español por defecto) y 10 voces TTS: M1–M5 (masculinas), F1–F5 (femeninas).
- Control de calidad (pasos de difusión) y velocidad.
- Exporta en **MP3** compatible con WhatsApp.

## Idiomas soportados

| Código | Idioma |
|--------|--------|
| es | Español |
| en | English |
| hi | हिन्दी (Hindi) |
| ar | العربية (Arabic) |
| fr | Français |
| ru | Русский (Russian) |
| pt | Português |
| id | Bahasa Indonesia |
| de | Deutsch |
| ja | 日本語 (Japanese) |
