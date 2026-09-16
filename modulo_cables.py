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
        df["Zp_Real"] = (df["Rotura_kgf"] / S_max).round(2)
        
        def clasificar(r):
            if r["Zp_Real"] < coef_seguridad:
                return "🔴 No Verifica (Inseguro)"
            elif coef_seguridad <= r["Zp_Real"] <= (coef_seguridad * 1.5):
                return "🟢 Verifica (Óptimo)"
            else:
                return "🟡 Sobredimensionado"
                
        # Definimos ambos nombres para asegurar compatibilidad con app.py
        df["Estado_Verificacion"] = df.apply(clasificar, axis=1)
        df["Estado"] = df["Estado_Verificacion"]
    
    return round(S_max, 2), round(F_req, 2), df

# Alias para que funcione con cualquier llamada que haga app.py
verificar_cable_elevacion = verificar_tabla_cables
obtener_tabla_cables_completa = obtener_catalogo_cables_completo