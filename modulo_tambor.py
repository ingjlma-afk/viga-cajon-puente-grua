# modulo_tambor.py
"""
Módulo de cálculo para el tambor de arrollamiento y estimación de pasteca/aparejo.
"""

import math

def calcular_dimensiones_tambor(*args, **kwargs):
    """
    Calcula el diámetro principal, longitud del tambor y paso del acanalado.
    Soporta cualquier nombre de parámetro enviado por app.py (d_cable_mm, H_elevacion_m, etc.).
    """
    # Extraer variables contemplando distintos nombres posibles
    d_cable = kwargs.get('d_cable_mm', kwargs.get('diametro_cable_mm', args[0] if args else 12.0))
    H_elev = kwargs.get('H_elevacion_m', kwargs.get('altura_elevacion_m', args[1] if len(args) > 1 else 6.0))
    num_ramales = kwargs.get('num_ramales', kwargs.get('ramas_polipasto', args[2] if len(args) > 2 else 4))
    
    # Diámetro mínimo de tambor recomendado Dt >= d_cable * 20 (Criterio DIN / FEM)
    diametro_tambor_mm = d_cable * 20.0
    
    # Paso de la ranura (pitch)
    paso_ranura_mm = d_cable * 1.15
    
    # Longitud útil de cable a arrollar por lado
    longitud_cable_m = (H_elev * num_ramales) / 2.0
    
    # Número de vueltas útiles + 2 vueltas de seguridad por norma
    vueltas_utiles = (longitud_cable_m * 1000.0) / (math.pi * diametro_tambor_mm)
    vueltas_totales = vueltas_utiles + 2.0
    
    # Longitud acanalada útil del tambor (mm)
    longitud_tambor_mm = vueltas_totales * paso_ranura_mm
    
    return {
        "diametro_tambor_mm": round(diametro_tambor_mm, 1),
        "longitud_tambor_mm": round(longitud_tambor_mm, 1),
        "paso_ranura_mm": round(paso_ranura_mm, 2),
        "vueltas_totales": round(vueltas_totales, 1)
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