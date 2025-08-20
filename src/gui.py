# gui.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os

from pathlib import Path

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Conciliador Inmobiliaria")
        self.geometry("720x250")
        self.resizable(False, False)

        # Variables de ruta
        self.dir_promesas = tk.StringVar()
        self.dir_certificados = tk.StringVar()
        self.status = tk.StringVar(value="Listo")

        self._build_ui()

    def _build_ui(self):

        padding = {"padx": 50, "pady": 35}

        ttk.Label(self, text="Carpeta Certificados:").grid(row=0, column=0, sticky="w", padx=30, pady=5)
        ttk.Entry(self, textvariable=self.dir_certificados, width=50).grid(row=1, column=0, sticky="w", padx=30)
        ttk.Button(self, text="Buscar Carpeta", command=self.browse_certificados).grid(row=1, column=1, sticky="w", padx=30)
        
        ttk.Label(self, text="").grid(row=2, column=0)

        ttk.Label(self, text="Carpeta Promesas de Compras:").grid(row=3, column=0, sticky="w", padx=30, pady=5)
        ttk.Entry(self, textvariable=self.dir_promesas, width=50).grid(row=4, column=0, sticky="w", padx=30)
        ttk.Button(self, text="Buscar Carpeta", command=self.browse_promesas).grid(row=4, column=1, sticky="w", padx=30)
        
        ttk.Label(self, text="").grid(row=5, column=0)

        ttk.Button(self, text="Ejecutar", command=self.run_process, width=20).grid(row=6, column=0, sticky="w", padx=30, pady=10)


    
    def browse_promesas(self):
        path = filedialog.askdirectory(title="Selecciona la carpeta de promesas")
        if path:
            self.dir_promesas.set(path)

    def browse_certificados(self):
        path = filedialog.askdirectory(title="Selecciona la carpeta de certificados")
        if path:
            self.dir_certificados.set(path)

    def run_process(self):
        prom_dir = Path(self.dir_promesas.get())
        cert_dir = Path(self.dir_certificados.get())

        if not prom_dir.is_dir() or not cert_dir.is_dir():
            messagebox.showerror("Error", "Debes seleccionar carpetas válidas")
            return

        self.status.set("Procesando…")
        self.update_idletasks()

        # Ejecutar en hilo separado para que la GUI no se congele
        thread = threading.Thread(target=self._process_worker, args=(prom_dir, cert_dir), daemon=True)
        thread.start()

    def _process_worker(self, prom_dir: Path, cert_dir: Path):
        try:
            from src.extractor import extract_info_from_text
            from src.matcher import build_report
            from src.reporter import export_to_excel
            from src.utils import load_text_from_pdf

            # 1. Recopilar promesas
            promesas = {}
            for pdf in prom_dir.rglob("*.pdf"):
                txt = load_text_from_pdf(pdf)
                data = extract_info_from_text(txt)
                key = f"{data.get('rut','')}_{data.get('departamento','')}"
                promesas[key] = data

            # 2. Recopilar certificados
            certificados = {}
            for pdf in cert_dir.rglob("*.pdf"):
                txt = load_text_from_pdf(pdf)
                data = extract_info_from_text(txt)
                key = f"{data.get('rut','')}_{data.get('departamento','')}"
                certificados[key] = data

            # 3. Comparar
            df = build_report(promesas, certificados)

            # 4. Exportar
            export_to_excel(df)

            self.status.set("Proceso terminado")
            messagebox.showinfo("Éxito", "El reporte se guardó en la carpeta 'reports'")
        except Exception as e:
            self.status.set("Error")
            messagebox.showerror("Error", str(e))

