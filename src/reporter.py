# reporter.py
import pandas as pd
from pathlib import Path
from config import REPORT_DIR
from datetime import datetime


def colorize(row):
    """
    Devuelve colores de fondo: rojo para discrepancias, verde si todo OK.
    """
    if row["missing_cert"]:
        return ["background-color: #ff9999"] * len(row)  # rojo claro
    elif row["mismatches"]:
        return ["background-color: #ffe6cc"] * len(row)  # naranja
    else:
        return ["background-color: #ccffcc"] * len(row)  # verde

def export_to_excel(df: pd.DataFrame, output_name: str,  output_dir: Path):
    """
    Exporta `df` a un archivo XLSX con estilos.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / output_name
    styled = df.style.apply(colorize, axis=1)
    
    # Guardar
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        styled.to_excel(writer, index=False, sheet_name="Reporte")
        
    print(f"Reporte guardado en: {path}")

