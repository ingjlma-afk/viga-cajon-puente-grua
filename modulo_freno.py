# modulo_freno.py
"""
Módulo de selección y verificación de frenos electromagnéticos de seguridad 
para el eje veloz (eje del motor) en mecanismos de elevación.
Normativa DIN 15020 / FEM 9.511.
"""

import math
import pandas as pd

COEFICIENTES_KF_FEM = {
    "1Bm (M3)": 1.5,
    "1Am (M4)": 1.6,
    "2m (M5)":  1.75,
    "3m (M6)":  1.8,
    "4m (M7)":  2.0,
    "5m (M8)":  2.25
}

def obtener_catalogo_frenos():
    """
    Catálogo estándar de frenos electromagnéticos de disco/zapata para eje de motor.
    Par nominal en N·m y peso propio del conjunto.
    """
    frenos = [
        {"Modelo": "FE-050", "Par_Nominal_Nm": 50.0, "Peso_kg": 8.5, "Diametro_disco_mm": 150},
        {"Modelo": "FE-100", "Par_Nominal_Nm": 100.0, "Peso_kg": 12.0, "Diametro_disco_mm": 180},
        {"Modelo": "FE-200", "Par_Nominal_Nm": 200.0, "Peso_kg": 18.5, "Diametro_disco_mm": 220},
        {"Modelo": "FE-400", "Par_Nominal_Nm": 400.0, "Peso_kg": 28.0, "Diametro_disco_mm": 280},
        {"Modelo": "FE-800", "Par_Nominal_Nm": 800.0, "Peso_kg": 45.0, "Diametro_disco_mm": 350},
        {"Modelo": "FE-1200", "Par_Nominal_Nm": 1200.0, "Peso_kg": 68.0, "Diametro_disco_mm": 420},
        {"Modelo": "FE-2000", "Par_Nominal_Nm": 2000.0, "Peso_kg": 95.0, "Diametro_disco_mm": 500},
    ]
    return pd.DataFrame(frenos)

def seleccionar_freno_motor(P_motor_kW: float, n_motor_rpm: float = 1450.0, grupo_fem: str = "2m (M5)"):
    """
    Calcula el par motor y selecciona los frenos que verifican el par de retención estático.
    """
    kf = COEFICIENTES_KF_FEM.get(str(grupo_fem), 1.75)
    
    # Par nominal del motor en el eje veloz (N·m)
    M_motor_Nm = (9550.0 * P_motor_kW) / n_motor_rpm if n_motor_rpm > 0 else 0
    M_freno_req_Nm = M_motor_Nm * kf

    df_frenos = obtener_catalogo_frenos()
    
    # Clasificación de verificación
    def verificar(row):
        par_freno = row["Par_Nominal_Nm"]
        if par_freno < M_freno_req_Nm:
            return "🔴 Insuficiente"
        elif M_freno_req_Nm <= par_freno <= (M_freno_req_Nm * 1.8):
            return "🟢 Óptimo / Recomendado"
        else:
            return "🟡 Sobredimensionado"

    df_frenos["Estado_Freno"] = df_frenos.apply(verificar, axis=1)
    df_frenos["k_f_Real"] = (df_frenos["Par_Nominal_Nm"] / M_motor_Nm).round(2)

    return round(M_motor_Nm, 2), round(M_freno_req_Nm, 2), kf, df_frenos