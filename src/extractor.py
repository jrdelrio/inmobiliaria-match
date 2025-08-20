# extractor.py
import openai
from typing import Dict
from config import OPENAI_API_KEY, BASE_PROMPT
from utils import clean_rut

openai.api_key = OPENAI_API_KEY

def extract_info_from_text(text: str) -> Dict:
    """
    Envía `text` a GPT-4 y devuelve un dict con los campos esperados.
    """
    prompt = f"{BASE_PROMPT}\n\nText:\n{text}"
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,  # determinista
            max_tokens=512,
        )
        raw = resp.choices[0].message.content
        data = parse_json(raw)
    except Exception as e:
        print(f"Error en extracción: {e}")
        data = {}

    # Normalizar RUT
    if "rut" in data:
        data["rut"] = clean_rut(str(data["rut"]))

    return data
