# modulo_cables.py
import pandas as pd
import os

def obtener_catalogo_cables_completo():
    ruta_csv = os.path.join(os.path.dirname(__file__), "catalogo_cables.csv")
    if os.path.exists(ruta_csv):
        return pd.read_csv(ruta_csv)
    else:
        # Resguardo por si aún no se generó el CSV
        return pd.DataFrame()

def verificar_cable_elevacion(S_tiro_max_kg: float, coef_seguridad_norma: float = 5.0):
    df = obtener_catalogo_cables_completo()
    if df.empty:
        return df
        
    df["Zp_Real"] = (df["Rotura_kgf"] / S_tiro_max_kg).round(2)
    
    def estado(row):
        if row["Zp_Real"] < coef_seguridad_norma:
            return "🔴 No Verifica (Inseguro)"
        elif coef_seguridad_norma <= row["Zp_Real"] <= (coef_seguridad_norma * 1.5):
            return "🟢 Verifica (Óptimo)"
        else:
            return "🟡 Sobredimensionado"

    df["Estado"] = df.apply(estado, axis=1)
    return df