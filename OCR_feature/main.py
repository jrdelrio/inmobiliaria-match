import sys
import subprocess
from pathlib import Path
import tempfile
import pdfplumber
import os
import shutil

LANG = "spa+eng"
OUTDIR = "output"

def run_ocr_to_temp_pdf(input_pdf: Path) -> Path:
    """Ejecuta ocrmypdf con force-ocr y devuelve la ruta a un PDF temporal."""
    if shutil.which("ocrmypdf") is None:
        print("[ERROR] No se encontró 'ocrmypdf' en el PATH. Instálalo con Homebrew: brew install ocrmypdf tesseract ghostscript")
        sys.exit(1)

    # PDF temporal para la salida del OCR
    tmp_fd, tmp_path = tempfile.mkstemp(suffix=".pdf")
    os.close(tmp_fd)  # no necesitamos mantener el descriptor abierto
    tmp_pdf = Path(tmp_path)

    cmd = [
        "ocrmypdf",
        "--language", LANG,
        "--rotate-pages",
        "--deskew",
        "--optimize", "1",
        "--output-type", "pdf",
        "--invalidate-digital-signatures",
        "--force-ocr",  # <- rasteriza siempre y rehace OCR
        str(input_pdf),
        str(tmp_pdf),
    ]

    print(f"[INFO] Ejecutando: {' '.join(cmd)}")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        # Limpia el temporal si falló
        try:
            tmp_pdf.unlink(missing_ok=True)
        except Exception:
            pass
        print("[ERROR] OCRmyPDF falló:\n", res.stderr.strip() or res.stdout.strip())
        sys.exit(1)

    print("[INFO] OCR completo ✓")
    return tmp_pdf

def extract_text(pdf_path: Path) -> str:
    """Extrae todo el texto con pdfplumber."""
    chunks = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            txt = page.extract_text() or ""
            chunks.append(txt.strip())
    return "\n\n".join(chunks).strip()

def main():
    if len(sys.argv) < 2:
        print("Uso: python main.py <ruta_al_pdf>")
        sys.exit(1)

    input_pdf = Path(sys.argv[1]).resolve()
    if not input_pdf.exists():
        print(f"[ERROR] No existe el archivo: {input_pdf}")
        sys.exit(1)

    outdir = Path(OUTDIR).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    text_txt = outdir / f"{input_pdf.stem}_OCR.txt"

    # 1) OCR a PDF temporal (no persistimos PDF final)
    ocr_tmp_pdf = run_ocr_to_temp_pdf(input_pdf)

    # 2) Extraer texto y guardar .txt
    full_text = extract_text(ocr_tmp_pdf)
    text_txt.write_text(full_text, encoding="utf-8")
    print(f"[INFO] Texto extraído: {len(full_text)} caracteres → {text_txt}")

    # 3) Borrar PDF temporal
    try:
        ocr_tmp_pdf.unlink(missing_ok=True)
    except Exception as e:
        print(f"[WARN] No se pudo borrar temporal: {ocr_tmp_pdf} ({e})")

if __name__ == "__main__":
    main()