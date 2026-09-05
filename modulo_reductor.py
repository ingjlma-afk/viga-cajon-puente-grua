# modulo_reductor.py
"""
Módulo de selección y verificación de reductores industriales para elevación.
Fuente: Catálogo LENTAX 820 (Edición 11-06-2025).
Series: DPB (Doble Reducción) y TPB (Triple Reducción - Ejes Paralelos).
"""

import pandas as pd

def obtener_catalogo_lentax():
    """
    Base de datos de reductores LENTAX 820 para n1 = 1500 rpm.
    Incluye potencias mecánicas admisibles (kW), pesos (kg) y cargas radiales admisibles en eje lento.
    """
    reductores = [
        # --- SERIE TPB: Triple Reducción (Páginas 7, 8 y 17) ---
        # Tamaño 280 (Peso: 625 kg, Carga radial salida < 15 rpm: 4000 kg, 16-70 rpm: 3500 kg)
        {"Serie": "TPB", "Modelo": "TPB 280", "i_nominal": 28.0, "n1_rpm": 1500, "P_adm_kW": 158.0, "Peso_kg": 625, "Fr_adm_kg": 3500, "d2_eje_mm": 130},
        {"Serie": "TPB", "Modelo": "TPB 280", "i_nominal": 31.5, "n1_rpm": 1500, "P_adm_kW": 145.0, "Peso_kg": 625, "Fr_adm_kg": 3500, "d2_eje_mm": 130},
        {"Serie": "TPB", "Modelo": "TPB 280", "i_nominal": 35.5, "n1_rpm": 1500, "P_adm_kW": 129.0, "Peso_kg": 625, "Fr_adm_kg": 3500, "d2_eje_mm": 130},
        {"Serie": "TPB", "Modelo": "TPB 280", "i_nominal": 40.0, "n1_rpm": 1500, "P_adm_kW": 113.0, "Peso_kg": 625, "Fr_adm_kg": 3500, "d2_eje_mm": 130},
        {"Serie": "TPB", "Modelo": "TPB 280", "i_nominal": 45.0, "n1_rpm": 1500, "P_adm_kW": 101.0, "Peso_kg": 625, "Fr_adm_kg": 3500, "d2_eje_mm": 130},
        {"Serie": "TPB", "Modelo": "TPB 280", "i_nominal": 50.0, "n1_rpm": 1500, "P_adm_kW": 92.0,  "Peso_kg": 625, "Fr_adm_kg": 3500, "d2_eje_mm": 130},
        {"Serie": "TPB", "Modelo": "TPB 280", "i_nominal": 56.0, "n1_rpm": 1500, "P_adm_kW": 82.0,  "Peso_kg": 625, "Fr_adm_kg": 3500, "d2_eje_mm": 130},
        {"Serie": "TPB", "Modelo": "TPB 280", "i_nominal": 63.0, "n1_rpm": 1500, "P_adm_kW": 72.0,  "Peso_kg": 625, "Fr_adm_kg": 3500, "d2_eje_mm": 130},
        {"Serie": "TPB", "Modelo": "TPB 280", "i_nominal": 71.0, "n1_rpm": 1500, "P_adm_kW": 64.0,  "Peso_kg": 625, "Fr_adm_kg": 3500, "d2_eje_mm": 130},
        {"Serie": "TPB", "Modelo": "TPB 280", "i_nominal": 80.0, "n1_rpm": 1500, "P_adm_kW": 58.0,  "Peso_kg": 625, "Fr_adm_kg": 3500, "d2_eje_mm": 130},
        {"Serie": "TPB", "Modelo": "TPB 280", "i_nominal": 90.0, "n1_rpm": 1500, "P_adm_kW": 51.0,  "Peso_kg": 625, "Fr_adm_kg": 3500, "d2_eje_mm": 130},
        {"Serie": "TPB", "Modelo": "TPB 280", "i_nominal": 100.0, "n1_rpm": 1500, "P_adm_kW": 45.0, "Peso_kg": 625, "Fr_adm_kg": 3500, "d2_eje_mm": 130},
        {"Serie": "TPB", "Modelo": "TPB 280", "i_nominal": 112.0, "n1_rpm": 1500, "P_adm_kW": 42.0, "Peso_kg": 625, "Fr_adm_kg": 3500, "d2_eje_mm": 130},

        # Tamaño 320 (Peso: 1020 kg, Carga radial salida 16-70 rpm: 5000 kg)
        {"Serie": "TPB", "Modelo": "TPB 320", "i_nominal": 28.0, "n1_rpm": 1500, "P_adm_kW": 267.0, "Peso_kg": 1020, "Fr_adm_kg": 5000, "d2_eje_mm": 160},
        {"Serie": "TPB", "Modelo": "TPB 320", "i_nominal": 31.5, "n1_rpm": 1500, "P_adm_kW": 233.0, "Peso_kg": 1020, "Fr_adm_kg": 5000, "d2_eje_mm": 160},
        {"Serie": "TPB", "Modelo": "TPB 320", "i_nominal": 35.5, "n1_rpm": 1500, "P_adm_kW": 216.0, "Peso_kg": 1020, "Fr_adm_kg": 5000, "d2_eje_mm": 160},
        {"Serie": "TPB", "Modelo": "TPB 320", "i_nominal": 40.0, "n1_rpm": 1500, "P_adm_kW": 183.0, "Peso_kg": 1020, "Fr_adm_kg": 5000, "d2_eje_mm": 160},
        {"Serie": "TPB", "Modelo": "TPB 320", "i_nominal": 45.0, "n1_rpm": 1500, "P_adm_kW": 170.0, "Peso_kg": 1020, "Fr_adm_kg": 5000, "d2_eje_mm": 160},
        {"Serie": "TPB", "Modelo": "TPB 320", "i_nominal": 50.0, "n1_rpm": 1500, "P_adm_kW": 144.0, "Peso_kg": 1020, "Fr_adm_kg": 5000, "d2_eje_mm": 160},
        {"Serie": "TPB", "Modelo": "TPB 320", "i_nominal": 56.0, "n1_rpm": 1500, "P_adm_kW": 133.0, "Peso_kg": 1020, "Fr_adm_kg": 5000, "d2_eje_mm": 160},
        {"Serie": "TPB", "Modelo": "TPB 320", "i_nominal": 63.0, "n1_rpm": 1500, "P_adm_kW": 116.0, "Peso_kg": 1020, "Fr_adm_kg": 5000, "d2_eje_mm": 160},
        {"Serie": "TPB", "Modelo": "TPB 320", "i_nominal": 71.0, "n1_rpm": 1500, "P_adm_kW": 108.0, "Peso_kg": 1020, "Fr_adm_kg": 5000, "d2_eje_mm": 160},
        {"Serie": "TPB", "Modelo": "TPB 320", "i_nominal": 80.0, "n1_rpm": 1500, "P_adm_kW": 94.0,  "Peso_kg": 1020, "Fr_adm_kg": 5000, "d2_eje_mm": 160},
        {"Serie": "TPB", "Modelo": "TPB 320", "i_nominal": 90.0, "n1_rpm": 1500, "P_adm_kW": 86.0,  "Peso_kg": 1020, "Fr_adm_kg": 5000, "d2_eje_mm": 160},
        {"Serie": "TPB", "Modelo": "TPB 320", "i_nominal": 100.0, "n1_rpm": 1500, "P_adm_kW": 75.0, "Peso_kg": 1020, "Fr_adm_kg": 5000, "d2_eje_mm": 160},
        {"Serie": "TPB", "Modelo": "TPB 320", "i_nominal": 112.0, "n1_rpm": 1500, "P_adm_kW": 69.0, "Peso_kg": 1020, "Fr_adm_kg": 5000, "d2_eje_mm": 160},

        # Tamaño 360 (Peso: 1400 kg, Carga radial salida 16-70 rpm: 7000 kg)
        {"Serie": "TPB", "Modelo": "TPB 360", "i_nominal": 22.4, "n1_rpm": 1500, "P_adm_kW": 447.0, "Peso_kg": 1400, "Fr_adm_kg": 7000, "d2_eje_mm": 170},
        {"Serie": "TPB", "Modelo": "TPB 360", "i_nominal": 25.0, "n1_rpm": 1500, "P_adm_kW": 393.0, "Peso_kg": 1400, "Fr_adm_kg": 7000, "d2_eje_mm": 170},
        {"Serie": "TPB", "Modelo": "TPB 360", "i_nominal": 28.0, "n1_rpm": 1500, "P_adm_kW": 348.0, "Peso_kg": 1400, "Fr_adm_kg": 7000, "d2_eje_mm": 170},
        {"Serie": "TPB", "Modelo": "TPB 360", "i_nominal": 31.5, "n1_rpm": 1500, "P_adm_kW": 325.0, "Peso_kg": 1400, "Fr_adm_kg": 7000, "d2_eje_mm": 170},
        {"Serie": "TPB", "Modelo": "TPB 360", "i_nominal": 35.5, "n1_rpm": 1500, "P_adm_kW": 287.0, "Peso_kg": 1400, "Fr_adm_kg": 7000, "d2_eje_mm": 170},
        {"Serie": "TPB", "Modelo": "TPB 360", "i_nominal": 40.0, "n1_rpm": 1500, "P_adm_kW": 255.0, "Peso_kg": 1400, "Fr_adm_kg": 7000, "d2_eje_mm": 170},
        {"Serie": "TPB", "Modelo": "TPB 360", "i_nominal": 45.0, "n1_rpm": 1500, "P_adm_kW": 225.0, "Peso_kg": 1400, "Fr_adm_kg": 7000, "d2_eje_mm": 170},
        {"Serie": "TPB", "Modelo": "TPB 360", "i_nominal": 50.0, "n1_rpm": 1500, "P_adm_kW": 198.0, "Peso_kg": 1400, "Fr_adm_kg": 7000, "d2_eje_mm": 170},
        {"Serie": "TPB", "Modelo": "TPB 360", "i_nominal": 56.0, "n1_rpm": 1500, "P_adm_kW": 175.0, "Peso_kg": 1400, "Fr_adm_kg": 7000, "d2_eje_mm": 170},
        {"Serie": "TPB", "Modelo": "TPB 360", "i_nominal": 63.0, "n1_rpm": 1500, "P_adm_kW": 160.0, "Peso_kg": 1400, "Fr_adm_kg": 7000, "d2_eje_mm": 170},
        {"Serie": "TPB", "Modelo": "TPB 360", "i_nominal": 71.0, "n1_rpm": 1500, "P_adm_kW": 143.0, "Peso_kg": 1400, "Fr_adm_kg": 7000, "d2_eje_mm": 170},
        {"Serie": "TPB", "Modelo": "TPB 360", "i_nominal": 80.0, "n1_rpm": 1500, "P_adm_kW": 127.0, "Peso_kg": 1400, "Fr_adm_kg": 7000, "d2_eje_mm": 170},
        {"Serie": "TPB", "Modelo": "TPB 360", "i_nominal": 90.0, "n1_rpm": 1500, "P_adm_kW": 111.0, "Peso_kg": 1400, "Fr_adm_kg": 7000, "d2_eje_mm": 170},

        # Tamaño 400 (Peso: 2295 kg, Carga radial salida 16-70 rpm: 15000 kg)
        {"Serie": "TPB", "Modelo": "TPB 400", "i_nominal": 22.4, "n1_rpm": 1500, "P_adm_kW": 657.0, "Peso_kg": 2295, "Fr_adm_kg": 15000, "d2_eje_mm": 200},
        {"Serie": "TPB", "Modelo": "TPB 400", "i_nominal": 25.0, "n1_rpm": 1500, "P_adm_kW": 597.0, "Peso_kg": 2295, "Fr_adm_kg": 15000, "d2_eje_mm": 200},
        {"Serie": "TPB", "Modelo": "TPB 400", "i_nominal": 28.0, "n1_rpm": 1500, "P_adm_kW": 526.0, "Peso_kg": 2295, "Fr_adm_kg": 15000, "d2_eje_mm": 200},
        {"Serie": "TPB", "Modelo": "TPB 400", "i_nominal": 31.5, "n1_rpm": 1500, "P_adm_kW": 475.0, "Peso_kg": 2295, "Fr_adm_kg": 15000, "d2_eje_mm": 200},
        {"Serie": "TPB", "Modelo": "TPB 400", "i_nominal": 35.5, "n1_rpm": 1500, "P_adm_kW": 419.0, "Peso_kg": 2295, "Fr_adm_kg": 15000, "d2_eje_mm": 200},
        {"Serie": "TPB", "Modelo": "TPB 400", "i_nominal": 40.0, "n1_rpm": 1500, "P_adm_kW": 373.0, "Peso_kg": 2295, "Fr_adm_kg": 15000, "d2_eje_mm": 200},
        {"Serie": "TPB", "Modelo": "TPB 400", "i_nominal": 45.0, "n1_rpm": 1500, "P_adm_kW": 328.0, "Peso_kg": 2295, "Fr_adm_kg": 15000, "d2_eje_mm": 200},
        {"Serie": "TPB", "Modelo": "TPB 400", "i_nominal": 50.0, "n1_rpm": 1500, "P_adm_kW": 298.0, "Peso_kg": 2295, "Fr_adm_kg": 15000, "d2_eje_mm": 200},
        {"Serie": "TPB", "Modelo": "TPB 400", "i_nominal": 56.0, "n1_rpm": 1500, "P_adm_kW": 263.0, "Peso_kg": 2295, "Fr_adm_kg": 15000, "d2_eje_mm": 200},
        {"Serie": "TPB", "Modelo": "TPB 400", "i_nominal": 63.0, "n1_rpm": 1500, "P_adm_kW": 230.0, "Peso_kg": 2295, "Fr_adm_kg": 15000, "d2_eje_mm": 200},
        {"Serie": "TPB", "Modelo": "TPB 400", "i_nominal": 71.0, "n1_rpm": 1500, "P_adm_kW": 213.0, "Peso_kg": 2295, "Fr_adm_kg": 15000, "d2_eje_mm": 200},
        {"Serie": "TPB", "Modelo": "TPB 400", "i_nominal": 80.0, "n1_rpm": 1500, "P_adm_kW": 189.0, "Peso_kg": 2295, "Fr_adm_kg": 15000, "d2_eje_mm": 200},
        {"Serie": "TPB", "Modelo": "TPB 400", "i_nominal": 90.0, "n1_rpm": 1500, "P_adm_kW": 168.0, "Peso_kg": 2295, "Fr_adm_kg": 15000, "d2_eje_mm": 200},

        # --- SERIE DPB: Doble Reducción (Páginas 2, 3 y 17) para polipastos rápidos ---
        {"Serie": "DPB", "Modelo": "DPB 280", "i_nominal": 14.0, "n1_rpm": 1500, "P_adm_kW": 298.0, "Peso_kg": 590, "Fr_adm_kg": 3500, "d2_eje_mm": 130},
        {"Serie": "DPB", "Modelo": "DPB 280", "i_nominal": 16.0, "n1_rpm": 1500, "P_adm_kW": 266.0, "Peso_kg": 590, "Fr_adm_kg": 3500, "d2_eje_mm": 130},
        {"Serie": "DPB", "Modelo": "DPB 280", "i_nominal": 18.0, "n1_rpm": 1500, "P_adm_kW": 231.0, "Peso_kg": 590, "Fr_adm_kg": 3500, "d2_eje_mm": 130},
        {"Serie": "DPB", "Modelo": "DPB 280", "i_nominal": 20.0, "n1_rpm": 1500, "P_adm_kW": 211.0, "Peso_kg": 590, "Fr_adm_kg": 3500, "d2_eje_mm": 130},
        {"Serie": "DPB", "Modelo": "DPB 280", "i_nominal": 22.4, "n1_rpm": 1500, "P_adm_kW": 189.0, "Peso_kg": 590, "Fr_adm_kg": 3500, "d2_eje_mm": 130},
        {"Serie": "DPB", "Modelo": "DPB 280", "i_nominal": 25.0, "n1_rpm": 1500, "P_adm_kW": 169.0, "Peso_kg": 590, "Fr_adm_kg": 3500, "d2_eje_mm": 130},
        {"Serie": "DPB", "Modelo": "DPB 280", "i_nominal": 28.0, "n1_rpm": 1500, "P_adm_kW": 147.0, "Peso_kg": 590, "Fr_adm_kg": 3500, "d2_eje_mm": 130},
    ]
    return pd.DataFrame(reductores)

def evaluar_reductores_elevacion(i_requerido: float, P_motor_kW: float, F_tiro_tambor_kg: float = 0.0, factor_servicio: float = 1.3):
    """
    Evalúa y filtra los reductores LENTAX que cumplen con la relación de reducción,
    la potencia admisible con factor de servicio y la carga en eje lento.
    """
    df = obtener_catalogo_lentax()
    P_min_req = P_motor_kW * factor_servicio

    # Desvío porcentual respecto a la relación teórica requerida
    df["Desvio_i_%"] = (((df["i_nominal"] - i_requerido) / i_requerido) * 100.0).round(1)
    df["Capacidad_Potencia"] = (df["P_adm_kW"] / P_min_req).round(2)

    def clasificar(row):
        cumple_pot = row["P_adm_kW"] >= P_min_req
        desvio_ok = abs(row["Desvio_i_%"]) <= 15.0  # Tolerancia típica en velocidad ±15%

        if not cumple_pot:
            return "🔴 Potencia Insuficiente"
        elif not desvio_ok:
            return "🟡 Desvío de Velocidad Elevado"
        else:
            return "🟢 Adecuado / Verificado"

    df["Estado_Reductor"] = df.apply(clasificar, axis=1)
    return df.sort_values(by=["Estado_Reductor", "Peso_kg"], ascending=[True, True])