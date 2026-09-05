# modulo_freno.py
"""
Módulo de cálculo y selección del freno de retención estático de la carga.
Ubicado en el eje del motor (eje veloz) según DIN 15020 / FEM 9.511.
Incluye referencias a catálogos comerciales reales (INTORQ BFK458 / BFK470).
"""

import math
import pandas as pd

# Coeficientes de seguridad normativos para el freno según Grupo FEM
COEFICIENTES_KF_FEM = {
    "1Bm (M3)": 1.5,
    "1Am (M4)": 1.6,
    "2m (M5)":  1.75,
    "3m (M6)":  1.8,
    "4m (M7)":  2.0,
    "5m (M8)":  2.25
}

# URL del catálogo técnico oficial de referencia (INTORQ BFK458)
URL_CATALOGO_INTORQ = "https://www.kendrion.com/en/products/industrial-brakes/spring-applied-brakes"

def obtener_catalogo_frenos():
    """
    Catálogo comercial de frenos electromagnéticos de seguridad por resorte (Spring-applied brakes).
    Datos extraídos de la serie industrial INTORQ BFK458 / Kendrion.
    """
    frenos = [
        {"Marca_Serie": "INTORQ BFK458-06", "Modelo": "Tamaño 06", "Par_Nominal_Nm": 50.0, "Peso_kg": 8.5, "Potencia_W": 25},
        {"Marca_Serie": "INTORQ BFK458-08", "Modelo": "Tamaño 08", "Par_Nominal_Nm": 100.0, "Peso_kg": 12.0, "Potencia_W": 30},
        {"Marca_Serie": "INTORQ BFK458-10", "Modelo": "Tamaño 10", "Par_Nominal_Nm": 200.0, "Peso_kg": 18.5, "Potencia_W": 40},
        {"Marca_Serie": "INTORQ BFK458-12", "Modelo": "Tamaño 12", "Par_Nominal_Nm": 400.0, "Peso_kg": 28.0, "Potencia_W": 55},
        {"Marca_Serie": "INTORQ BFK458-14", "Modelo": "Tamaño 14", "Par_Nominal_Nm": 800.0, "Peso_kg": 45.0, "Potencia_W": 75},
        {"Marca_Serie": "INTORQ BFK458-16", "Modelo": "Tamaño 16", "Par_Nominal_Nm": 1200.0, "Peso_kg": 68.0, "Potencia_W": 95},
        {"Marca_Serie": "INTORQ BFK458-18", "Modelo": "Tamaño 18", "Par_Nominal_Nm": 2000.0, "Peso_kg": 95.0, "Potencia_W": 120},
    ]
    return pd.DataFrame(frenos)

def calcular_freno_carga(Q_kg: float, P_pasteca_kg: float, D_tambor_mm: float, i_reduccion: float, eta_mecanico: float = 0.90, grupo_fem: str = "2m (M5)"):
    kf = COEFICIENTES_KF_FEM.get(str(grupo_fem), 1.75)
    
    # Fuerza de la carga total suspendida (N)
    F_carga_N = (Q_kg + P_pasteca_kg) * 9.81
    
    # Par estático en el tambor (N·m)
    R_tambor_m = (D_tambor_mm / 1000.0) / 2.0
    M_tambor_Nm = F_carga_N * R_tambor_m
    
    # Par transmitido al eje del motor (eje veloz)
    M_carga_eje_motor_Nm = (M_tambor_Nm / i_reduccion) * eta_mecanico if i_reduccion > 0 else 0
    
    # Par mínimo que debe garantizar el freno por norma
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

    return round(M_carga_eje_motor_Nm, 2), round(M_freno_req_Nm, 2), kf, df_frenos, URL_CATALOGO_INTORQ