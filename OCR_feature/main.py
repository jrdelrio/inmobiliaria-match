import argparse
import subprocess
import sys
from pathlib import Path
import pdfplumber

def run_ocr(input_pdf: Path, ocr_pdf: Path, languages="spa+eng", pages=None, force=False):
    """
    Ejecuta OCRmyPDF vía CLI.
    -l spa+eng: español + inglés (ajusta a tus documentos)
    --rotate-pages, --deskew: corrige rotaciones y sesgos.
    --optimize 1: balance calidad/tamaño.
    """
    cmd = [
        "ocrmypdf",
        "--language", languages,
        "--rotate-pages",
        "--deskew",
        "--optimize", "1",
        "--output-type", "pdf",
        "--invalidate-digital-signatures",
        #"--skip-text",        # si ya tiene texto, no fuerza OCR (rápido y seguro)
        str(input_pdf),
        str(ocr_pdf),
    ]

    if pages:
        cmd += ["--pages", str(pages)]
    if force:
        cmd += ["--force-ocr"]
    else:
        cmd += ["--skip-text"]

    print(f"[INFO] Ejecutando: {' '.join(cmd)}")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("[ERROR] OCRmyPDF falló:\n", res.stderr)
        sys.exit(1)
    print("[INFO] OCR completo ✓")

def extract_text(ocr_pdf: Path) -> str:
    """
    Extrae texto con pdfplumber. Une páginas con dos saltos de línea.
    """
    chunks = []
    with pdfplumber.open(ocr_pdf) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            txt = page.extract_text() or ""
            chunks.append(txt.strip())
    return "\n\n".join(chunks).strip()

def main():
    parser = argparse.ArgumentParser(description="OCR + extracción de texto (y tablas opcional) de PDF.")
    parser.add_argument("--input", "-i", required=True, help="Ruta al PDF de entrada (escaneado o mixto).")
    parser.add_argument("--outdir", "-o", default="output", help="Carpeta de salida.")
    parser.add_argument("--lang", "-l", default="spa+eng", help="Idiomas Tesseract: ej. 'spa', 'eng', 'spa+eng'.")
    parser.add_argument("--pages", default=None, help="Rango de páginas para aplicar OCR, ej. '2-', '3-5', '1,3,5'.")
    args = parser.parse_args()

    input_pdf = Path(args.input).resolve()
    outdir = Path(args.outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    if not input_pdf.exists():
        print(f"[ERROR] No existe el archivo: {input_pdf}")
        sys.exit(1)

    ocr_pdf = outdir / f"{input_pdf.stem}_OCR.pdf"
    text_txt = outdir / f"{input_pdf.stem}_OCR.txt"

    # 1) OCR
    run_ocr(input_pdf, ocr_pdf, languages=args.lang)

    # 2) Texto → string + archivo .txt
    full_text = extract_text(ocr_pdf)
    text_txt.write_text(full_text, encoding="utf-8")
    print(f"[INFO] Texto extraído: {len(full_text)} caracteres → {text_txt}")

    # 4) Listo: también tienes 'full_text' en memoria por si quieres seguir procesando
    # (ej. pasar a un LLM, regex, etc.)

if __name__ == "__main__":
    main()
