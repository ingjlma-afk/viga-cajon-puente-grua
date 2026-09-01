import math

def calcular_dimensiones_tambor(d_cable_mm, H_elevacion_m, num_ramales=4, tipo_polipasto='Gemelo'):
    """
    Calcula las dimensiones del tambor y el peso REAL del cable según DIN 15020.
    Incluye vueltas de seguridad, fijación y ramales de aparejo.
    """
    # 1. Diámetro mínimo del tambor (Relación D/d ≈ 20 para Grupo III)
    D_tambor_mm = math.ceil((d_cable_mm * 20.0) / 5.0) * 5.0  # Normalizado a múltiplos de 5
    D_tambor_m = D_tambor_mm / 1000.0
    
    # 2. Longitud Total de Cable Requerida
    # Ramales activos que bajan y suben
    L_util = H_elevacion_m * num_ramales
    
    # Vueltas de seguridad en el tambor (Mínimo 3 vueltas por lado que nunca se desenrollan)
    vueltas_seguridad_lado = 3
    salidas_tambor = 2 if tipo_polipasto == 'Gemelo' else 1
    L_seguridad = salidas_tambor * (vueltas_seguridad_lado + 1) * math.pi * D_tambor_m
    
    # Tramo adicional para fijaciones y paso por poleas superiores
    L_extra_mecanismo = 4.0 
    
    L_cable_total_m = L_util + L_seguridad + L_extra_mecanismo
    
    # 3. Peso Específico Real del Cable de Acero (kg/m)
    # Para cables norma DIN/verope con alma de acero: q ≈ 0.0042 * d^2 [kg/m]
    peso_lineal_kg_m = 0.0042 * (d_cable_mm ** 2)  # Para d=14mm -> ~0.823 kg/m
    peso_cable_kg = L_cable_total_m * peso_lineal_kg_m
    
    # 4. Dimensionamiento del Tambor Ranurado
    vueltas_utiles_lado = (H_elevacion_m * (num_ramales / salidas_tambor)) / (math.pi * D_tambor_m)
    vueltas_totales_lado = vueltas_utiles_lado + vueltas_seguridad_lado + 1
    
    paso_p = d_cable_mm * 1.15  # Paso de la ranura
    L_ranurada_lado_mm = vueltas_totales_lado * paso_p
    
    if tipo_polipasto == 'Gemelo':
        L_central_libre_mm = d_cable_mm * 10.0  # Zona neutra central
        L_total_tambor_mm = (2 * L_ranurada_lado_mm) + L_central_libre_mm + (2 * d_cable_mm * 3)
    else:
        L_total_tambor_mm = L_ranurada_lado_mm + (2 * d_cable_mm * 5)
        
    # Estimación de Peso del Tambor de Chapa de Acero Espesores Estándar
    # Tubo de acero con tapas de acoplamiento
    espesor_tubo_mm = max(10.0, d_cable_mm * 0.8)
    volumen_tubo_cm3 = math.pi * (D_tambor_mm / 10.0) * (espesor_tubo_mm / 10.0) * (L_total_tambor_mm / 10.0)
    peso_tambor_kg = (volumen_tubo_cm3 * 0.00785) * 1.35  # Coeficiente por tapas y eje
    
    return {
        "D_tambor_mm": D_tambor_mm,
        "L_total_tambor_mm": round(L_total_tambor_mm, 1),
        "L_cable_total_m": round(L_cable_total_m, 2),
        "peso_lineal_kg_m": round(peso_lineal_kg_m, 3),
        "peso_cable_kg": round(peso_cable_kg, 1),
        "peso_tambor_kg": round(peso_tambor_kg, 1)
    }