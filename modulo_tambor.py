# modulo_tambor.py
"""
Módulo de cálculo para el tambor de arrollamiento y estimación de pasteca/aparejo.
"""

import math

def calcular_dimensiones_tambor(diametro_cable_mm: float, altura_elevacion_m: float, ramas_polipasto: int = 4):
    """Calcula el diámetro principal, longitud del tambor y paso del acanalado."""
    diametro_tambor_mm = diametro_cable_mm * 20.0
    paso_ranura_mm = diametro_cable_mm * 1.15
    longitud_cable_m = (altura_elevacion_m * ramas_polipasto) / 2.0
    
    vueltas_utiles = (longitud_cable_m * 1000) / (math.pi * diametro_tambor_mm)
    vueltas_totales = vueltas_utiles + 2.0
    longitud_tambor_mm = vueltas_totales * paso_ranura_mm
    
    return {
        "diametro_tambor_mm": round(diametro_tambor_mm, 1),
        "longitud_tambor_mm": round(longitud_tambor_mm, 1),
        "paso_ranura_mm": round(paso_ranura_mm, 2),
        "vueltas_totales": round(vueltas_totales, 1)
    }

def estimar_peso_pasteca(carga_nominal_tn: float):
    """Estima el peso propio de la pasteca/aparejo de gancho."""
    peso_estimado_kg = carga_nominal_tn * 1000 * 0.03
    return round(peso_estimado_kg, 1)

# Alias de compatibilidad por si app.py la requiere con otro nombre
calcular_peso_pasteca = estimar_peso_pasteca