# utils.py
import re
from pathlib import Path
import json

def clean_rut(rut: str) -> str:
    """Retorna RUT sin puntos ni guiones."""
    return re.sub(r"[^\dkK]", "", rut).lower()

def load_text_from_pdf(pdf_path: Path) -> str:
    """
    Devuelve todo el texto de un PDF.
    Si el PDF contiene imágenes se recurre a OCR.
    """
    import pdfplumber
    import pytesseract
    from PIL import Image

    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            txt = page.extract_text()
            if txt:
                text += txt + "\n"
            else:
                # Página sin texto: usar OCR
                img = page.to_image(resolution=300)
                pil_img = Image.frombytes(
                    mode="RGB",
                    size=img.original_image.size,
                    data=img.original_image.tobytes()
                )
                text += pytesseract.image_to_string(pil_img) + "\n"
    return text.strip()

def parse_json(text: str):
    """Intenta convertir la cadena JSON (con mayúsculas, etc.) a objeto Python."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Intentar con `eval` solo si no hay riesgo de código malicioso
        # (en producción, evita `eval`)
        return eval(text)

