"""
Extracción de texto de PDF para generar audiolibros.

Usa pypdf (Python puro, sin binarios). Devuelve el texto listo para editar
en el editor compartido antes de pasarlo al TTS.
"""
import os
import re

from pypdf import PdfReader


def extract_text(pdf_path):
    """Extrae el texto de un PDF y lo normaliza para lectura en voz alta."""
    if not pdf_path or not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"No se encontró el PDF: {pdf_path}")

    reader = PdfReader(pdf_path)
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            pages.append(text.strip())

    full = "\n\n".join(pages)
    # Une palabras cortadas con guion al final de línea: "exa-\nmple" -> "example".
    full = re.sub(r"-\n(\w)", r"\1", full)
    # Normaliza espacios sin colapsar los saltos de párrafo.
    full = re.sub(r"[ \t]+", " ", full)
    full = re.sub(r"\n{3,}", "\n\n", full)
    return full.strip()
