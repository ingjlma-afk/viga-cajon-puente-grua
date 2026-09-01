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

def estimar_peso_pasteca(*args, **kwargs):
    """
    Estima el peso propio de la pasteca/aparejo de gancho.
    Acepta cualquier cantidad de parámetros enviados por app.py para evitar TypeError.
    """
    # Si app.py pasa la carga como primer argumento posicional
    carga = args[0] if args else kwargs.get('carga_nominal_tn', kwargs.get('Q', 5.0))
    
    # Si la carga viene en kg (mayor a 100), la convertimos a toneladas
    if carga > 100:
        carga_tn = carga / 1000.0
    else:
        carga_tn = carga
        
    # Estimación estándar: ~3% de la carga nominal
    peso_estimado_kg = carga_tn * 1000.0 * 0.03
    return round(peso_estimado_kg, 1)

# Alias de compatibilidad
calcular_peso_pasteca = estimar_peso_pasteca