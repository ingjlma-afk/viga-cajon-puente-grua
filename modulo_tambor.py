import math

def calcular_dimensiones_tambor(d_cable_mm, H_elevacion_m, num_ramales=4, tipo_polipasto='Gemelo (2/2 o 4/2)', h1_factor=18):
    """
    Calcula el dimensionamiento geométrico del tambor ranurado y el peso del cable.
    """
    # 1. Diámetro mínimo de tambor
    D_min_tambor_mm = d_cable_mm * h1_factor
    # Normalización del diámetro del tambor al valor comercial superior
    diametros_std = [160, 200, 250, 315, 400, 500, 630, 710, 800, 1000]
    D_tambor_mm = min([d for d in diametros_std if d >= D_min_tambor_mm], default=D_min_tambor_mm)
    
    D_tambor_m = D_tambor_mm / 1000.0
    d_cable_m = d_cable_mm / 1000.0
    
    # 2. Configuración de ramales por salida de tambor
    es_gemelo = 'Gemelo' in tipo_polipasto
    ramales_por_salida = num_ramales / 2.0 if es_gemelo else num_ramales
    
    # Longitud de cable que se arrolla por lado
    L_arrollado_lado = H_elevacion_m * ramales_por_salida
    
    # Longitud total de cable en el sistema (incluyendo ramales fijos y aparejo)
    L_total_cable = (H_elevacion_m * num_ramales) + 5.0 # +5m para fijaciones y poleas
    
    # 3. Peso del cable
    # Peso específico promedio: q_m [kg/m] ≈ 0.0039 * d_mm²
    peso_metro_kg = 0.0039 * (d_cable_mm**2)
    peso_total_cable_kg = L_total_cable * peso_metro_kg
    
    # 4. Cálculo de espiras y longitud del tambor
    paso_ranura_mm = d_cable_mm * 1.15  # Paso estándar DIN
    espiras_utiles = L_arrollado_lado / (math.pi * D_tambor_m)
    espiras_totales = espiras_utiles + 3 # 3 espiras de seguridad
    
    longitud_ranurada_lado_mm = espiras_totales * paso_ranura_mm
    
    if es_gemelo:
        # Espacio central para libre paso del aparejo en posición superior
        L_centro_libre_mm = d_cable_mm * 10
        L_total_tambor_mm = (2 * longitud_ranurada_lado_mm) + L_centro_libre_mm
    else:
        L_total_tambor_mm = longitud_ranurada_lado_mm + (d_cable_mm * 5)
        
    # 5. Estimación del peso del tambor (espesor de pared estimado e ≈ 0.1 * D_tambor)
    espesor_mm = max(10.0, D_tambor_mm * 0.08)
    volumen_acero_m3 = math.pi * (D_tambor_m) * (espesor_mm/1000.0) * (L_total_tambor_mm/1000.0)
    peso_estimado_tambor_kg = volumen_acero_m3 * 7850.0  # Densidad acero kg/m³
    
    return {
        "D_tambor_mm": D_tambor_mm,
        "L_total_tambor_mm": round(L_total_tambor_mm, 1),
        "L_total_cable_m": round(L_total_cable, 2),
        "peso_cable_kg": round(peso_total_cable_kg, 2),
        "peso_tambor_kg": round(peso_estimado_tambor_kg, 2),
        "espiras_totales": round(espiras_totales, 1)
    }