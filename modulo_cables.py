# modulo_cables.py
import os
import pandas as pd

def obtener_catalogo_cables_completo():
    ruta_csv = os.path.join(os.path.dirname(__file__), "catalogo_cables.csv")
    if os.path.exists(ruta_csv):
        df = pd.read_csv(ruta_csv)
    else:
        df = pd.DataFrame()
    return df

def verificar_tabla_cables(Q_kg: float, P_ap_kg: float, num_ramales: int, eta_poleas: float = 0.98, grupo_din: str = "II", coef_seguridad: float = 5.0, *args, **kwargs):
    """
    Función de compatibilidad con app.py para cálculo de tiro máximo y verificación.
    """
    n_poleas = max(1, num_ramales // 2)
    rend_mecanismo = eta_poleas ** n_poleas
    
    # Tiro máximo en el ramal más solicitado
    S_max = ((Q_kg + P_ap_kg) / (num_ramales * rend_mecanismo))
    F_req = S_max * coef_seguridad

    df = obtener_catalogo_cables_completo()
    if not df.empty:
        # Asignar columnas esperadas por app.py
        df["CS_Real"] = (df["Rotura_kgf"] / S_max).round(2)
        df["Zp_Real"] = df["CS_Real"]
        
        # Mapeo de rotura en kN y composición
        if "Rotura_kN" in df.columns and "Rotura_kN_1960" not in df.columns:
            df["Rotura_kN_1960"] = df["Rotura_kN"]
        elif "Rotura_kN_1960" in df.columns and "Rotura_kN" not in df.columns:
            df["Rotura_kN"] = df["Rotura_kN_1960"]

        if "Composicion" not in df.columns:
            df["Composicion"] = df["Norma_Marca"]

        def clasificar(r):
            if r["CS_Real"] < coef_seguridad:
                return "🔴 No Verifica (Inseguro)"
            elif coef_seguridad <= r["CS_Real"] <= (coef_seguridad * 1.5):
                return "🟢 Verifica (Óptimo)"
            else:
                return "🟡 Sobredimensionado"
                
        df["Estado_Verificacion"] = df.apply(clasificar, axis=1)
        df["Estado"] = df["Estado_Verificacion"]
    
    return round(S_max, 2), round(F_req, 2), df

# Alias de compatibilidad
verificar_cable_elevacion = verificar_tabla_cables
obtener_tabla_cables_completa = obtener_catalogo_cables_completo