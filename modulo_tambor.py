# modulo_tambor.py
"""
Módulo de dimensionamiento de tambor y poleas para puentes grúa.
Aplica factor de flexibilidad c_flex para cables de alto rendimiento (Verope).
"""

import math

COEFICIENTES_H_MIN_FEM = {
    "1Bm (M3)": {"h1": 14.0, "h2": 16.0, "h3": 11.2},
    "1Am (M4)": {"h1": 16.0, "h2": 18.0, "h3": 12.5},
    "2m (M5)":  {"h1": 18.0, "h2": 20.0, "h3": 14.0},
    "3m (M6)":  {"h1": 20.0, "h2": 22.4, "h3": 16.0},
    "4m (M7)":  {"h1": 22.4, "h2": 25.0, "h3": 18.0},
    "5m (M8)":  {"h1": 25.0, "h2": 28.0, "h3": 20.0}
}

def calcular_dimensiones_tambor(
    d_cable_mm: float, 
    H_elevacion_m: float, 
    num_ramales: int, 
    peso_kg_m: float = 0.88, 
    tipo_polipasto: str = 'Gemelo', 
    vueltas_reserva: int = 3, 
    grupo_fem: str = "2m (M5)",
    h1_adoptado: float = 18.0,
    h2_adoptado: float = 20.0,
    h3_adoptado: float = 14.0,
    marca_cable: str = "DIN",
    *args, **kwargs
):
    """
    Calcula la geometría aplicando un descuento por flexibilidad si el cable es Verope.
    """
    h_base = COEFICIENTES_H_MIN_FEM.get(grupo_fem, {"h1": 18.0, "h2": 20.0, "h3": 14.0})

    # Factor de flexibilidad: Verope permite un 12% menos de diámetro por su construcción
    c_flex = 0.88 if "Verope" in str(marca_cable) else 1.00

    h1_min = round(h_base["h1"] * c_flex, 1)
    h2_min = round(h_base["h2"] * c_flex, 1)
    h3_min = round(h_base["h3"] * c_flex, 1)

    # Verificación
    h1_valido = h1_adoptado >= h1_min
    h2_valido = h2_adoptado >= h2_min
    h3_valido = h3_adoptado >= h3_min

    D_tambor_mm = d_cable_mm * h1_adoptado
    D_polea_mm = d_cable_mm * h2_adoptado
    D_reenvio_mm = d_cable_mm * h3_adoptado

    paso_ranura_mm = d_cable_mm * 1.15
    perimetro_tambor_m = (math.pi * D_tambor_mm) / 1000.0

    if "Gemelo" in str(tipo_polipasto):
        longitud_util_m = H_elevacion_m * (num_ramales / 2.0)
        vueltas_reserva_totales = vueltas_reserva * 2
        L_centro_mm = D_polea_mm
    else:
        longitud_util_m = H_elevacion_m * num_ramales
        vueltas_reserva_totales = vueltas_reserva
        L_centro_mm = 0.0

    vueltas_utiles = longitud_util_m / perimetro_tambor_m if perimetro_tambor_m > 0 else 0
    vueltas_totales = vueltas_utiles + vueltas_reserva_totales

    L_ranurada_lado_mm = (vueltas_totales / (2.0 if "Gemelo" in str(tipo_polipasto) else 1.0)) * paso_ranura_mm
    L_mangas_pestaña_mm = d_cable_mm * 4.0
    
    if "Gemelo" in str(tipo_polipasto):
        L_tambor_total_mm = (2.0 * L_ranurada_lado_mm) + L_centro_mm + L_mangas_pestaña_mm
    else:
        L_tambor_total_mm = L_ranurada_lado_mm + L_mangas_pestaña_mm

    longitud_total_cable_m = vueltas_totales * perimetro_tambor_m
    peso_cable_total_kg = round(longitud_total_cable_m * peso_kg_m, 1)
    peso_tambor_kg = round(math.pi * (D_tambor_mm / 1000.0) * (L_tambor_total_mm / 1000.0) * 0.012 * 7850.0, 1)

    return {
        "D_tambor_mm": round(D_tambor_mm, 1),
        "D_polea_mm": round(D_polea_mm, 1),
        "D_reenvio_mm": round(D_reenvio_mm, 1),
        "L_tambor_mm": round(L_tambor_total_mm, 1),
        "L_centro_mm": round(L_centro_mm, 1),
        "peso_cable_kg": peso_cable_total_kg,
        "peso_tambor_kg": peso_tambor_kg,
        "h1_min": h1_min, "h2_min": h2_min, "h3_min": h3_min,
        "h1_valido": h1_valido, "h2_valido": h2_valido, "h3_valido": h3_valido,
        "c_flex": c_flex
    }

def estimar_peso_pasteca(Q: float = 5000.0, num_ramales: int = 4, *args, **kwargs):
    carga_tn = Q / 1000.0 if Q > 100 else Q
    return round(carga_tn * 1000.0 * 0.03, 1)

calcular_peso_pasteca = estimar_peso_pasteca