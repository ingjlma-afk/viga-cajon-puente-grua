# modulo_tambor.py
"""
Módulo de cálculo para el tambor de arrollamiento y estimación de pasteca/aparejo
en sistemas de elevación para puentes grúa.
"""

import math

def calcular_dimensiones_tambor(diametro_cable_mm: float, altura_elevacion_m: float, ramas_polipasto: int = 4):
    """
    Calcula el diámetro principal, la longitud del tambor y el paso del acanalado.
    """
    # Diámetro mínimo de tambor recomendado Dt >= d_cable * 20 (Criterio DIN / FEM)
    diametro_tambor_mm = diametro_cable_mm * 20.0
    
    # Paso de la ranura (pitch)
    paso_ranura_mm = diametro_cable_mm * 1.15
    
    # Longitud útil de cable a arrollar por lado
    longitud_cable_m = (altura_elevacion_m * ramas_polipasto) / 2.0
    
    # Número de vueltas útiles + 2 vueltas de seguridad por norma
    vueltas_utiles = (longitud_cable_m * 1000) / (math.pi * diametro_tambor_mm)
    vueltas_totales = vueltas_utiles + 2.0
    
    # Longitud acanalada útil del tambor (mm)
    longitud_tambor_mm = vueltas_totales * paso_ranura_mm
    
    return {
        "diametro_tambor_mm": round(diametro_tambor_mm, 1),
        "longitud_tambor_mm": round(longitud_tambor_mm, 1),
        "paso_ranura_mm": round(paso_ranura_mm, 2),
        "vueltas_totales": round(vueltas_totales, 1)
    }


def estimar_peso_pasteca(carga_nominal_tn: float):
    """
    Estima el peso propio de la pasteca/aparejo de gancho según la capacidad.
    """
    # Estimación empírica estándar: ~2.5% a 3.5% de la carga nominal
    peso_estimado_kg = carga_nominal_tn * 1000 * 0.03
    return round(peso_estimado_kg, 1)


if __name__ == "__main__":
    res = calcular_dimensiones_tambor(12.0, 6.0)
    print("--- Módulo Tambor Cargado ---")
    print(f"Diámetro tambor: {res['diametro_tambor_mm']} mm")
    print(f"Peso estimado pasteca (5 Tn): {estimar_peso_pasteca(5.0)} kg")