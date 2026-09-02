# modulo_cables.py
"""
Módulo de base de datos y selección de cables de acero.
Evalúa según bandas de coeficientes de seguridad FEM/ISO (CS_min a CS_max).
"""

import pandas as pd

def obtener_tabla_cables_completa():
    registros = []

    # 1. VEROPE (ALTO RENDIMIENTO)
    verope_catalog = [
        ("Verotop", "Antigiratorio", "35x7 Compactado", [
            (8.0, 56.2, 61.5, 0.29), (10.0, 88.0, 96.5, 0.45), (12.0, 128.0, 140.0, 0.65), 
            (14.0, 175.0, 192.0, 0.88), (16.0, 228.0, 250.0, 1.15), (18.0, 289.0, 317.0, 1.46), 
            (20.0, 357.0, 391.0, 1.80), (22.0, 432.0, 473.0, 2.18), (24.0, 514.0, 563.0, 2.59), 
            (26.0, 603.0, 661.0, 3.04), (28.0, 700.0, 767.0, 3.53), (32.0, 914.0, 1002.0, 4.61), 
            (36.0, 1157.0, 1268.0, 5.83), (40.0, 1428.0, 1565.0, 7.20), (50.0, 2180.0, 2380.0, 11.25)
        ]),
        ("Veropro 8", "No Antigiratorio 8C", "8x36 Alma Plastificada", [
            (10.0, 88.4, 96.8, 0.44), (12.0, 127.0, 139.0, 0.63), (14.0, 173.0, 190.0, 0.86), 
            (16.0, 225.0, 247.0, 1.12), (18.0, 286.0, 313.0, 1.42), (20.0, 353.0, 387.0, 1.75), 
            (22.0, 427.0, 468.0, 2.12), (24.0, 508.0, 557.0, 2.52), (26.0, 597.0, 654.0, 2.96), 
            (28.0, 692.0, 759.0, 3.43), (32.0, 904.0, 991.0, 4.48), (36.0, 1144.0, 1254.0, 5.67), 
            (40.0, 1412.0, 1548.0, 7.00), (46.0, 1868.0, 2047.0, 9.25), (50.0, 2190.0, 2390.0, 10.93)
        ]),
        ("Veropower 8", "No Antigiratorio 8C", "8x36 Totalmente Compactado", [
            (14.0, 182.0, 199.0, 0.91), (16.0, 238.0, 261.0, 1.19), (18.0, 301.0, 330.0, 1.51), 
            (20.0, 372.0, 407.0, 1.86), (22.0, 450.0, 493.0, 2.25), (24.0, 535.0, 586.0, 2.68), 
            (26.0, 628.0, 688.0, 3.14), (28.0, 729.0, 798.0, 3.65), (32.0, 952.0, 1043.0, 4.76), 
            (36.0, 1205.0, 1320.0, 6.03), (40.0, 1488.0, 1630.0, 7.44), (50.0, 2325.0, 2548.0, 11.63), 
            (60.0, 3350.0, 3660.0, 16.74)
        ]),
    ]

    for modelo, tipo, constr, diametros in verope_catalog:
        for d, r1960, r2160, peso in diametros:
            registros.append({
                "Norma_Marca": "Verope", "Tipo": tipo, "Composicion": modelo, "Construccion": constr,
                "Diametro_mm": d, "Peso_kg_m": peso, "Rotura_kN_1960": r1960, "Rotura_kN_2160": r2160
            })

    # 2. DIN 655
    din_655_B = [
        (9.0, 0.26, 4450, 5000), (10.0, 0.34, 5650, 6350), (11.0, 0.41, 7000, 7850), 
        (12.0, 0.50, 8450, 9500), (13.0, 0.59, 10050, 11300), (14.0, 0.70, 11800, 13250), 
        (16.0, 0.93, 15700, 17650), (18.0, 1.06, 17850, 20100), (20.0, 1.34, 22600, 25400), 
        (22.0, 1.65, 27900, 31400), (24.0, 2.00, 33750, 38000), (28.0, 2.38, 40200, 45200)
    ]
    for d, peso, r160, r180 in din_655_B:
        registros.append({
            "Norma_Marca": "DIN 655", "Tipo": "Convencional (Alma Textil)", "Composicion": "6x37 (222 hilos)",
            "Construccion": "Composición B", "Diametro_mm": d, "Peso_kg_m": peso,
            "Rotura_kN_1960": (r160 * 9.81) / 1000.0, "Rotura_kN_2160": (r180 * 9.81) / 1000.0
        })

    # 3. DIN 656
    din_656_A = [
        (8.0, 0.26, 4250, 4800), (10.0, 0.38, 6350, 7150), (12.0, 0.55, 9250, 10400), 
        (14.0, 0.75, 12550, 14100), (16.0, 1.00, 16700, 18800), (18.0, 1.18, 19800, 22250), 
        (20.0, 1.53, 25550, 28750), (22.0, 1.79, 30000, 33800), (24.0, 2.20, 37000, 41650)
    ]
    for d, peso, r160, r180 in din_656_A:
        registros.append({
            "Norma_Marca": "DIN 656", "Tipo": "Seal-Lay", "Composicion": "6x19 (114 hilos)",
            "Construccion": "Composición A", "Diametro_mm": d, "Peso_kg_m": peso,
            "Rotura_kN_1960": (r160 * 9.81) / 1000.0, "Rotura_kN_2160": (r180 * 9.81) / 1000.0
        })

    return pd.DataFrame(registros)


def verificar_tabla_cables(Q_kg: float = 5000.0, P_ap_kg: float = 150.0, num_ramales: int = 4, cs_min: float = 5.0, cs_max: float = 5.7, *args, **kwargs):
    """
    Evalúa los cables según la banda admisible de CS_min a CS_max.
    Soporta que la llamada mande 'coeficiente_seguridad' para no romper retrocompatibilidad.
    """
    if 'coeficiente_seguridad' in kwargs and kwargs['coeficiente_seguridad'] is not None:
        cs_min = kwargs['coeficiente_seguridad']
        cs_max = cs_min * 1.15

    carga_total_kg = Q_kg + P_ap_kg
    S_max_kg = carga_total_kg / num_ramales
    S_max_kN = (S_max_kg * 9.81) / 1000.0
    F_req_kN = S_max_kN * cs_min

    df = obtener_tabla_cables_completa()

    def clasificar_cable(row):
        r_kn = row['Rotura_kN_1960']
        cs_real = r_kn / S_max_kN if S_max_kN > 0 else 0
        
        if cs_real < cs_min:
            estado = "🔴 No Verifica"
        elif cs_min <= cs_real <= cs_max:
            estado = "🟢 Óptimo / Recomendado"
        else:
            estado = "🟡 Sobredimensionado"
            
        return pd.Series([round(cs_real, 2), estado])

    df[['CS_Real', 'Estado_Verificacion']] = df.apply(clasificar_cable, axis=1)
    df["Diámetro [mm]"] = df["Diametro_mm"]
    
    return round(S_max_kg, 2), round(F_req_kN, 2), df


seleccionar_cable_mecanismo = verificar_tabla_cables