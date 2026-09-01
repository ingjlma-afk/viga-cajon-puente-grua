import math

def estimar_peso_pasteca(carga_q_kg, num_ramales):
    """
    Estima el peso del aparejo/pasteca (gancho + poleas de carga)
    según la capacidad nominal Q y el número de ramales (DIN 15401).
    """
    carga_ton = carga_q_kg / 1000.0
    if carga_ton <= 5:
        peso_base = 120 + (num_ramales * 12)
    elif carga_ton <= 10:
        peso_base = 220 + (num_ramales * 20)
    elif carga_ton <= 20:
        peso_base = 450 + (num_ramales * 35)
    elif carga_ton <= 35:
        peso_base = 750 + (num_ramales * 50)
    else:
        peso_base = 1100 + (num_ramales * 70)
    return float(peso_base)

def calcular_dimensiones_tambor(d_cable_mm, H_elevacion_m, num_ramales=4, tipo_polipasto='Gemelo (4/2 o 2/2)', h1_factor=18):
    """
    Calcula el dimensionamiento geométrico del tambor ranurado, 
    longitud y peso del cable de acero.
    """
    # 1. Diámetro mínimo y normalizado del tambor
    D_min_tambor_mm = d_cable_mm * h1_factor
    diametros_std = [160, 200, 250, 315, 400, 500, 630, 710, 800, 1000]
    D_tambor_mm = min([d for d in diametros_std if d >= D_min_tambor_mm], default=D_min_tambor_mm)
    
    D_tambor_m = D_tambor_mm / 1000.0
    
    # 2. Arrollamiento y longitud total de cable
    es_gemelo = 'Gemelo' in tipo_polipasto
    ramales_por_salida = num_ramales / 2.0 if es_gemelo else num_ramales
    
    L_arrollado_lado = H_elevacion_m * ramales_por_salida
    L_total_cable = (H_elevacion_m * num_ramales) + 6.0  # +6m para vueltas muertas, fijación y poleas
    
    # 3. Masa del cable (kg/m ≈ 0.0039 * d²)
    peso_metro_kg = 0.0039 * (d_cable_mm**2)
    peso_total_cable_kg = L_total_cable * peso_metro_kg
    
    # 4. Geometría del tambor (DIN 15061)
    paso_ranura_mm = d_cable_mm * 1.15
    espiras_utiles = L_arrollado_lado / (math.pi * D_tambor_m)
    espiras_totales = espiras_utiles + 3  # 3 espiras fijas de seguridad
    
    longitud_ranurada_lado_mm = espiras_totales * paso_ranura_mm
    
    if es_gemelo:
        L_centro_libre_mm = d_cable_mm * 10
        L_total_tambor_mm = (2 * longitud_ranurada_lado_mm) + L_centro_libre_mm
    else:
        L_total_tambor_mm = longitud_ranurada_lado_mm + (d_cable_mm * 5)
        
    # 5. Peso del tambor de acero
    espesor_mm = max(10.0, D_tambor_mm * 0.08)
    volumen_acero_m3 = math.pi * D_tambor_m * (espesor_mm / 1000.0) * (L_total_tambor_mm / 1000.0)
    peso_estimado_tambor_kg = volumen_acero_m3 * 7850.0
    
    return {
        "D_tambor_mm": D_tambor_mm,
        "L_total_tambor_mm": round(L_total_tambor_mm, 1),
        "L_total_cable_m": round(L_total_cable, 2),
        "peso_cable_kg": round(peso_total_cable_kg, 2),
        "peso_tambor_kg": round(peso_estimado_tambor_kg, 2),
        "espiras_totales": round(espiras_totales, 1)
    }