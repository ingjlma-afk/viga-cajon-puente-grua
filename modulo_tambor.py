# modulo_tambor.py
"""
Módulo de cálculo para el tambor de arrollamiento y estimación de pasteca/aparejo.
"""

import math

def calcular_dimensiones_tambor(*args, **kwargs):
    """
    Calcula las dimensiones del tambor y sus pesos asociados para el carro del puente grúa.
    """
    d_cable = kwargs.get('d_cable_mm', kwargs.get('diametro_cable_mm', args[0] if args else 12.0))
    H_elev = kwargs.get('H_elevacion_m', kwargs.get('altura_elevacion_m', args[1] if len(args) > 1 else 6.0))
    num_ramales = kwargs.get('num_ramales', kwargs.get('ramas_polipasto', args[2] if len(args) > 2 else 4))
    
    # Diámetro mínimo de tambor (Dt >= d_cable * 20)
    diametro_tambor_mm = d_cable * 20.0
    paso_ranura_mm = d_cable * 1.15
    longitud_cable_m = (H_elev * num_ramales) / 2.0
    
    vueltas_utiles = (longitud_cable_m * 1000.0) / (math.pi * diametro_tambor_mm)
    vueltas_totales = vueltas_utiles + 2.0
    longitud_tambor_mm = vueltas_totales * paso_ranura_mm
    
    # Estimación de pesos requeridos por app.py en la línea 295
    peso_cable_kg = round(longitud_cable_m * (d_cable ** 2) * 0.0038, 1)
    peso_tambor_kg = round(math.pi * (diametro_tambor_mm / 1000.0) * (longitud_tambor_mm / 1000.0) * 0.015 * 7850.0, 1)
    
    return {
        "diametro_tambor_mm": round(diametro_tambor_mm, 1),
        "longitud_tambor_mm": round(longitud_tambor_mm, 1),
        "paso_ranura_mm": round(paso_ranura_mm, 2),
        "vueltas_totales": round(vueltas_totales, 1),
        "peso_cable_kg": peso_cable_kg,
        "peso_tambor_kg": peso_tambor_kg
    }


def estimar_peso_pasteca(Q: float = 5000.0, num_ramales: int = 4, *args, **kwargs):
    """
    Estima el peso propio de la pasteca/aparejo de gancho.
    """
    if Q > 100:
        carga_tn = Q / 1000.0
    else:
        carga_tn = Q
        
    peso_estimado_kg = carga_tn * 1000.0 * 0.03
    return round(peso_estimado_kg, 1)


# Alias de compatibilidad
calcular_peso_pasteca = estimar_peso_pasteca