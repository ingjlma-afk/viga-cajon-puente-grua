# modulo_freno.py
"""
Módulo de cálculo y selección del freno de retención estático de la carga.
Ubicado en el eje del motor (eje veloz) según DIN 15020 / FEM 9.511.
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
    frenos = [
        {"Modelo": "FE-050", "Par_Nominal_Nm": 50.0, "Peso_kg": 8.5},
        {"Modelo": "FE-100", "Par_Nominal_Nm": 100.0, "Peso_kg": 12.0},
        {"Modelo": "FE-200", "Par_Nominal_Nm": 200.0, "Peso_kg": 18.5},
        {"Modelo": "FE-400", "Par_Nominal_Nm": 400.0, "Peso_kg": 28.0},
        {"Modelo": "FE-800", "Par_Nominal_Nm": 800.0, "Peso_kg": 45.0},
        {"Modelo": "FE-1200", "Par_Nominal_Nm": 1200.0, "Peso_kg": 68.0},
        {"Modelo": "FE-2000", "Par_Nominal_Nm": 2000.0, "Peso_kg": 95.0},
    ]
    return pd.DataFrame(frenos)

def calcular_freno_carga(Q_kg: float, P_pasteca_kg: float, D_tambor_mm: float, i_reduccion: float, eta_mecanico: float = 0.90, grupo_fem: str = "2m (M5)"):
    kf = COEFICIENTES_KF_FEM.get(str(grupo_fem), 1.75)
    
    # Carga total suspendida en el gancho (kgf -> N)
    F_carga_N = (Q_kg + P_pasteca_kg) * 9.81
    
    # Par estático en el tambor por acción de la carga (N·m)
    R_tambor_m = (D_tambor_mm / 1000.0) / 2.0
    M_tambor_Nm = F_carga_N * R_tambor_m
    
    # Par transmitido al eje del motor a través del reductor
    M_carga_eje_motor_Nm = (M_tambor_Nm / i_reduccion) * eta_mecanico if i_reduccion > 0 else 0
    
    # Par mínimo de frenado requerido por norma
    M_freno_req_Nm = M_carga_eje_motor_Nm * kf

    df_frenos = obtener_catalogo_frenos()
    
    def clasificar_freno(row):
        par_freno = row["Par_Nominal_Nm"]
        if par_freno < M_freno_req_Nm:
            return "🔴 Insuficiente (Riesgo de Caída)"
        elif M_freno_req_Nm <= par_freno <= (M_freno_req_Nm * 1.8):
            return "🟢 Óptimo / Recomendado"
        else:
            return "🟡 Sobredimensionado"

    df_frenos["Estado_Freno"] = df_frenos.apply(clasificar_freno, axis=1)
    df_frenos["k_f_Real"] = (df_frenos["Par_Nominal_Nm"] / M_carga_eje_motor_Nm).round(2) if M_carga_eje_motor_Nm > 0 else 0

    return round(M_carga_eje_motor_Nm, 2), round(M_freno_req_Nm, 2), kf, df_frenos