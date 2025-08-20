# config.py
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

api_key = load_dotenv(dotenv_path=BASE_DIR / ".env")




# Ruta donde se guardará el reporte
REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)

# API key de OpenAI (puedes guardarla en variable de entorno)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Prompt base que usaremos para convertir texto en JSON
BASE_PROMPT = """
You are an expert document analyst.  
The following text contains information about a real estate purchase promise or a credit certificate.  
Extract the data into a JSON object with the keys:

- nombre: Full name (string)
- rut: Chilean RUT, digits only (string)
- departamento: Department number (string)
- monto_credito: Credit amount in CLP (integer)
- fecha: Date in ISO format YYYY-MM-DD (string) [optional if present]

Ignore any extraneous information.  
Return only the JSON, no explanations.
"""

