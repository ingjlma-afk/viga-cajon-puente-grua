import math

def obtener_catalogo_ampliado():
    diametros = [8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 32]
    catalogo = []
    
    for d in diametros:
        # Clásico 160 kg/mm² (Alma de fibra)
        f_rot_160 = round(0.54 * (d**2) * 160 * 0.00980665, 1)
        catalogo.append({"id": f"C160-{d}", "linea": "Clásico DIN 655 (160 kg/mm²)", "diam_mm": d, "F_rotura_kN": f_rot_160, "factor_h1": 20})
        
        # Clásico 180 kg/mm² (Alma de acero)
        f_rot_180 = round(0.58 * (d**2) * 180 * 0.00980665, 1)
        catalogo.append({"id": f"C180-{d}", "linea": "Clásico DIN 655 (180 kg/mm²)", "diam_mm": d, "F_rotura_kN": f_rot_180, "factor_h1": 20})
        
        # verope veropro 8 (200 kg/mm² - Compactado)
        f_rot_200 = round(0.68 * (d**2) * 200 * 0.00980665, 1)
        catalogo.append({"id": f"VERO200-{d}", "linea": "verope veropro 8 (200 kg/mm²)", "diam_mm": d, "F_rotura_kN": f_rot_200, "factor_h1": 16})
        
        # verope verotop (220 kg/mm² - Antigiratorio)
        f_rot_220 = round(0.72 * (d**2) * 220 * 0.00980665, 1)
        catalogo.append({"id": f"VERO220-{d}", "linea": "verope verotop (220 kg/mm²)", "diam_mm": d, "F_rotura_kN": f_rot_220, "factor_h1": 15})
        
    return catalogo

def verificar_tabla_cables(Q_kg, P_ap_kg, num_ramales, grupo_mecanismo='III', filtro_estado='Todos'):
    # Rangos de la TABLA 3 (DIN 4130) [v_min, v_max]
    rangos_din_4130 = {
        'I':   (5.5, 6.0),
        'II':  (5.5, 6.0),
        'III': (6.0, 7.0),
        'IV':  (7.0, 8.0),
        'V':   (8.0, 9.5)
    }
    
    v_min, v_max = rangos_din_4130.get(grupo_mecanismo, (6.0, 7.0))
    eta_polipasto = 0.95
    
    # Tracción real por ramal
    S_max_kgf = (Q_kg + P_ap_kg) / (num_ramales * eta_polipasto)
    S_max_kN = (S_max_kgf * 9.80665) / 1000.0
    
    catalogo = obtener_catalogo_ampliado()
    resultados = []
    
    for cable in catalogo:
        coef_real = round(cable["F_rotura_kN"] / S_max_kN, 2)
        
        # Evaluación en 3 estados
        if coef_real < v_min:
            estado = "❌ NO CUMPLE (Insuficiente)"
            categoria = "No Cumple"
        elif v_min <= coef_real <= v_max:
            estado = "✅ RECOMENDADO (Óptimo DIN)"
            categoria = "Recomendado"
        else:
            estado = "⚠️ NO CONVIENE (Sobredimensionado)"
            categoria = "Sobredimensionado"
            
        # Filtros para la vista del usuario
        if filtro_estado == 'Solo Recomendados' and categoria != 'Recomendado':
            continue
        elif filtro_estado == 'Verificados (Óptimos y Sobredimensionados)' and categoria == 'No Cumple':
            continue
            
        D_polea = cable["diam_mm"] * cable["factor_h1"]
        D_tambor = round(D_polea * 0.9, 0)
        
        resultados.append({
            "Línea / Tecnología": cable["linea"],
            "Diámetro [mm]": cable["diam_mm"],
            "F. Rotura Cat. [kN]": cable["F_rotura_kN"],
            "Coeff. Seg. Real": coef_real,
            "Rango DIN Búsqueda": f"{v_min} - {v_max}",
            "D_min Polea [mm]": D_polea,
            "D_min Tambor [mm]": D_tambor,
            "Evaluación": estado
        })
        
    return S_max_kgf, (S_max_kN * v_min), resultados