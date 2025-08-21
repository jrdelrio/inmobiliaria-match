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
        self.geometry("750x300")
        self.resizable(False, False)

        # Variables de ruta
        self.dir_promesas = tk.StringVar()
        self.dir_certificados = tk.StringVar()
        self.status = tk.StringVar(value="Listo")
        self.dir_reporte = tk.StringVar()
        self.cancel_requested = False
        
        self.dir_certificados.trace_add("write", self.validate_inputs)
        self.dir_promesas.trace_add("write", self.validate_inputs)
        self.dir_reporte.trace_add("write", self.validate_inputs)


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
        
        ttk.Label(self, text="Carpeta de destino del reporte:").grid(row=6, column=0, sticky="w", padx=30, pady=5)
        ttk.Entry(self, textvariable=self.dir_reporte, width=50).grid(row=7, column=0, sticky="w", padx=30)
        ttk.Button(self, text="Seleccionar Carpeta", command=self.browse_reporte).grid(row=7, column=1, sticky="w", padx=30)

        frame_botones = ttk.Frame(self)
        frame_botones.grid(row=8, column=0, columnspan=2, sticky="w", padx=30, pady=10)
        
        self.boton_ejecutar = ttk.Button(frame_botones, text="Ejecutar", command=self.run_process, width=20, state="disabled")
        self.boton_ejecutar.grid(row=0, column=0, padx=(0, 10))
        
        self.boton_cancelar = ttk.Button(frame_botones, text="Interrumpir", command=self.cancel_process, width=20, state="disabled")
        self.boton_cancelar.grid(row=0, column=1)

    def browse_reporte(self):
        path = filedialog.askdirectory(title="Selecciona carpeta para guardar el reporte")
        if path:
            self.dir_reporte.set(path)
    
    def browse_promesas(self):
        path = filedialog.askdirectory(title="Selecciona la carpeta de promesas")
        if path:
            self.dir_promesas.set(path)

    def browse_certificados(self):
        path = filedialog.askdirectory(title="Selecciona la carpeta de certificados")
        if path:
            self.dir_certificados.set(path)

    def run_process(self):
        self.cancel_requested = False
        
        prom_dir = Path(self.dir_promesas.get())
        cert_dir = Path(self.dir_certificados.get())

        if not prom_dir.is_dir() or not cert_dir.is_dir():
            messagebox.showerror("Error", "Debes seleccionar carpetas válidas")
            return

        output_dir = Path(self.dir_reporte.get())
        if not output_dir.is_dir():
            messagebox.showerror("Error", "Debes seleccionar una carpeta válida para guardar el reporte")
            return

        self.status.set("Procesando…")
        self.update_idletasks()
        
        self.boton_ejecutar.config(state="disabled")
        self.boton_cancelar.config(state="normal")

        # Ejecutar en hilo separado para que la GUI no se congele
        thread = threading.Thread(target=self._process_worker, args=(prom_dir, cert_dir), daemon=True)
        thread.start()
    
    def cancel_process(self):
        self.cancel_requested = True
        self.status.set("Proceso cancelado por el usuario.")
        self.boton_cancelar.config(state="disabled")


    def _process_worker(self, prom_dir: Path, cert_dir: Path):
        try:
            from src.extractor import extract_info_from_text
            from src.matcher import build_report
            from src.reporter import export_to_excel
            from src.utils import load_text_from_pdf

            # 1. Recopilar promesas
            if not list(prom_dir.rglob("*.pdf")):
                messagebox.showerror("Error", "La carpeta de promesas no contiene archivos PDF.")
                return
            promesas = {}
            for pdf in prom_dir.rglob("*.pdf"):
                if self.cancel_requested:
                    self._finalize_process(cancelled=True)
                    return
                txt = load_text_from_pdf(pdf)
                data = extract_info_from_text(txt)
                key = f"{data.get('rut','')}_{data.get('departamento','')}"
                promesas[key] = data

            # 2. Recopilar certificados
            if not list(cert_dir.rglob("*.pdf")):
                messagebox.showerror("Error", "La carpeta de certificados no contiene archivos PDF.")
                return

            certificados = {}
            for pdf in cert_dir.rglob("*.pdf"):
                if self.cancel_requested:
                    self._finalize_process(cancelled=True)
                    return
                txt = load_text_from_pdf(pdf)
                data = extract_info_from_text(txt)
                key = f"{data.get('rut','')}_{data.get('departamento','')}"
                certificados[key] = data
            
            if self.cancel_requested:
                self._finalize_process(cancelled=True)
                return

            # 3. Comparar
            df = build_report(promesas, certificados)

            # 4. Exportar
            from datetime import datetime
            
            output_dir = Path(self.dir_reporte.get())
            timestamp = datetime.now().strftime("REPORTE_%Y_%m_%d-%Hh_%Mm.xlsx")
            export_to_excel(df, output_name=timestamp, output_dir=output_dir)

            self._finalize_process(success=True)
            self.status.set("Proceso terminado")
            messagebox.showinfo("Éxito", f"El reporte se guardó en:\n{self.dir_reporte.get()}")
        except Exception as e:
            self.status.set("Error")
            messagebox.showerror("Error", str(e))

    def _finalize_process(self, success=False, cancelled=False, error=None):
        if cancelled:
            self.status.set("❌ Proceso cancelado.")
            messagebox.showinfo("Cancelado", "El proceso fue interrumpido por el usuario.")
        elif error:
            self.status.set("❌ Error")
            messagebox.showerror("Error", str(error))
        elif success:
            self.status.set("✅ Proceso terminado")
            messagebox.showinfo("Éxito", "El reporte se guardó en la carpeta seleccionada.")

        # Restaurar estado de botones
        self.boton_ejecutar.config(state="normal")
        self.boton_cancelar.config(state="disabled")

    def validate_inputs(self, *args):
        if all(Path(p).is_dir() for p in [self.dir_certificados.get(), self.dir_promesas.get(), self.dir_reporte.get()]):
            self.boton_ejecutar.config(state="normal")
        else:
            self.boton_ejecutar.config(state="disabled")