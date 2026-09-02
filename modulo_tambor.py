# modulo_tambor.py
"""
Módulo de cálculo para el tambor de arrollamiento y estimación de pesos reales.
"""

import math

def calcular_dimensiones_tambor(d_cable_mm: float, H_elevacion_m: float, num_ramales: int, peso_kg_m: float = 0.88, tipo_polipasto: str = 'Gemelo', vueltas_reserva: int = 3, *args, **kwargs):
    """
    Calcula la geometría real del tambor y el peso total exacto del cable instalado.
    """
    # Compatibilidad con llamadas sin peso explícito
    if 'd_cable_mm' in kwargs: d_cable_mm = kwargs['d_cable_mm']
    if 'H_elevacion_m' in kwargs: H_elevacion_m = kwargs['H_elevacion_m']
    if 'num_ramales' in kwargs: num_ramales = kwargs['num_ramales']
    
    diametro_tambor_mm = d_cable_mm * 20.0
    paso_ranura_mm = d_cable_mm * 1.15
    perimetro_tambor_m = (math.pi * diametro_tambor_mm) / 1000.0

    if "Gemelo" in str(tipo_polipasto):
        longitud_util_m = H_elevacion_m * (num_ramales / 2.0)
        vueltas_reserva_totales = vueltas_reserva * 2
    else:
        longitud_util_m = H_elevacion_m * num_ramales
        vueltas_reserva_totales = vueltas_reserva

    vueltas_utiles = longitud_util_m / perimetro_tambor_m if perimetro_tambor_m > 0 else 0
    vueltas_totales = vueltas_utiles + vueltas_reserva_totales
    
    longitud_total_cable_m = vueltas_totales * perimetro_tambor_m
    peso_cable_total_kg = round(longitud_total_cable_m * peso_kg_m, 1)
    
    longitud_tambor_mm = vueltas_totales * paso_ranura_mm * (2.0 if "Gemelo" in str(tipo_polipasto) else 1.0)
    peso_tambor_kg = round(math.pi * (diametro_tambor_mm / 1000.0) * (longitud_tambor_mm / 1000.0) * 0.012 * 7850.0, 1)

    return {
        "D_tambor_mm": round(diametro_tambor_mm, 1),
        "diametro_tambor_mm": round(diametro_tambor_mm, 1),
        "L_tambor_mm": round(longitud_tambor_mm, 1),
        "longitud_tambor_mm": round(longitud_tambor_mm, 1),
        "paso_ranura_mm": round(paso_ranura_mm, 2),
        "vueltas_totales": round(vueltas_totales, 1),
        "longitud_cable_m": round(longitud_total_cable_m, 2),
        "peso_cable_kg": peso_cable_total_kg,
        "peso_tambor_kg": peso_tambor_kg
    }

def estimar_peso_pasteca(Q: float = 5000.0, num_ramales: int = 4, *args, **kwargs):
    carga_tn = Q / 1000.0 if Q > 100 else Q
    return round(carga_tn * 1000.0 * 0.03, 1)

calcular_peso_pasteca = estimar_peso_pasteca