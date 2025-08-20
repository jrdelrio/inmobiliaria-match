# matcher.py
from typing import Dict, List, Tuple
import pandas as pd

def compare_records(promesa: Dict, certificado: Dict) -> Tuple[Dict, List[str]]:
    """
    Devuelve:
    - record: diccionario con todos los campos de ambas fuentes.
    - mismatches: lista de nombres de campos que no coinciden.
    """
    record = {}
    mismatches = []

    # Campos comunes
    for key in ["nombre", "rut", "departamento", "monto_credito", "fecha"]:
        p_val = promesa.get(key)
        c_val = certificado.get(key)
        record[key] = {"promesa": p_val, "certificado": c_val}
        if p_val != c_val:
            mismatches.append(key)

    return record, mismatches

def build_report(promesas: Dict[str, Dict], certificados: Dict[str, Dict]) -> pd.DataFrame:
    """
    promesas y certificados son dicts {key: datos}
    key puede ser el RUT, el departamento, o un id combinado.
    """
    rows = []
    for key, prom in promesas.items():
        cert = certificados.get(key)
        if not cert:
            # No hay certificado para esta promesa
            record = {"departamento": prom.get("departamento"),
                      "nombre_promesa": prom.get("nombre"),
                      "rut_promesa": prom.get("rut"),
                      "missing_cert": True}
            rows.append(record)
            continue

        rec, mism = compare_records(prom, cert)
        row = {
            "departamento": rec["departamento"]["promesa"],
            "nombre_promesa": rec["nombre"]["promesa"],
            "rut_promesa": rec["rut"]["promesa"],
            "nombre_cert": rec["nombre"]["certificado"],
            "rut_cert": rec["rut"]["certificado"],
            "monto_promesa": rec["monto_credito"]["promesa"],
            "monto_cert": rec["monto_credito"]["certificado"],
            "fecha_promesa": rec["fecha"]["promesa"],
            "fecha_cert": rec["fecha"]["certificado"],
            "mismatches": ", ".join(mism) if mism else ""
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    return df
