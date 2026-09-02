# modulo_cables.py
"""
Módulo completo de base de datos y selección de cables de acero para puentes grúa.
Incluye catálogo exhaustivo de Verope y normas DIN 655 / DIN 656 con verificación según CS.
"""

import pandas as pd

def obtener_tabla_cables_completa():
    """
    Retorna la base de datos exhaustiva con todos los modelos Verope y tablas DIN.
    """
    registros = []

    # 1. VEROPE (ALTO RENDIMIENTO)
    verope_catalog = [
        ("Verotop", "Antigiratorio", "35x7 Compactado", "Grúas torre, móviles, elevación principal", [
            (8.0, 56.2, 61.5), (10.0, 88.0, 96.5), (12.0, 128.0, 140.0), (14.0, 175.0, 192.0),
            (16.0, 228.0, 250.0), (18.0, 289.0, 317.0), (20.0, 357.0, 391.0), (22.0, 432.0, 473.0),
            (24.0, 514.0, 563.0), (26.0, 603.0, 661.0), (28.0, 700.0, 767.0), (32.0, 914.0, 1002.0),
            (36.0, 1157.0, 1268.0), (40.0, 1428.0, 1565.0), (50.0, 2180.0, 2380.0)
        ]),
        ("Verotop E", "Antigiratorio", "35x7 No compactado", "Grúas torre y auxiliares", [
            (10.0, 82.1, 89.8), (12.0, 118.0, 129.0), (14.0, 161.0, 176.0), (16.0, 210.0, 230.0),
            (18.0, 266.0, 291.0), (20.0, 328.0, 359.0), (24.0, 473.0, 518.0), (28.0, 643.0, 704.0),
            (32.0, 840.0, 920.0), (40.0, 1300.0, 1420.0)
        ]),
        ("Verotop S", "Antigiratorio", "35x7 Swaged / Totalmente Compactado", "Trabajo pesado, perforadoras", [
            (10.0, 98.5, 108.0), (12.0, 142.0, 155.0), (14.0, 193.0, 211.0), (16.0, 252.0, 276.0),
            (18.0, 319.0, 349.0), (20.0, 394.0, 431.0), (24.0, 567.0, 621.0), (28.0, 772.0, 846.0),
            (32.0, 995.0, 1090.0)
        ]),
        ("Verotop P", "Antigiratorio", "35x7 Inserto Plástico / Compactado", "Grúas offshore y sobre orugas", [
            (12.0, 128.0, 140.0), (14.0, 175.0, 192.0), (16.0, 228.0, 250.0), (18.0, 289.0, 317.0),
            (20.0, 357.0, 391.0), (24.0, 514.0, 563.0), (28.0, 700.0, 767.0), (32.0, 914.0, 1002.0),
            (36.0, 1157.0, 1268.0), (40.0, 1428.0, 1565.0), (46.0, 1890.0, 2070.0)
        ]),
        ("Veropro 8", "No Antigiratorio 8C", "8x36 Alma Plastificada (EPIW)", "Grúas puente, portuarias", [
            (10.0, 88.4, 96.8), (12.0, 127.0, 139.0), (14.0, 173.0, 190.0), (16.0, 225.0, 247.0),
            (18.0, 286.0, 313.0), (20.0, 353.0, 387.0), (22.0, 427.0, 468.0), (24.0, 508.0, 557.0),
            (26.0, 597.0, 654.0), (28.0, 692.0, 759.0), (32.0, 904.0, 991.0), (36.0, 1144.0, 1254.0),
            (40.0, 1412.0, 1548.0), (46.0, 1868.0, 2047.0), (50.0, 2190.0, 2390.0)
        ]),
        ("Veropower 8", "No Antigiratorio 8C", "8x36 Totalmente Compactado", "Siderurgia, elevación pesada", [
            (14.0, 182.0, 199.0), (16.0, 238.0, 261.0), (18.0, 301.0, 330.0), (20.0, 372.0, 407.0),
            (22.0, 450.0, 493.0), (24.0, 535.0, 586.0), (26.0, 628.0, 688.0), (28.0, 729.0, 798.0),
            (32.0, 952.0, 1043.0), (36.0, 1205.0, 1320.0), (40.0, 1488.0, 1630.0), (50.0, 2325.0, 2548.0),
            (60.0, 3350.0, 3660.0)
        ]),
        ("Veropro 6", "No Antigiratorio 6C", "6x36 Alma Plastificada", "Excavadoras, tracción pesada", [
            (10.0, 81.2, 88.9), (12.0, 117.0, 128.0), (14.0, 159.0, 174.0), (16.0, 208.0, 228.0),
            (18.0, 263.0, 288.0), (20.0, 325.0, 356.0), (24.0, 468.0, 513.0), (28.0, 637.0, 698.0),
            (32.0, 832.0, 911.0), (36.0, 1053.0, 1153.0), (40.0, 1300.0, 1424.0), (46.0, 1710.0, 1870.0)
        ]),
        ("Verocoat 6", "No Antigiratorio 6C", "6x36 Recubrimiento Plástico Exterior", "Entornos abrasivos / corrosivos", [
            (8.0, 45.6, 50.0), (10.0, 71.2, 78.0), (12.0, 102.0, 112.0), (14.0, 139.0, 152.0),
            (16.0, 182.0, 199.0), (18.0, 230.0, 252.0), (20.0, 284.0, 311.0), (24.0, 409.0, 448.0),
            (28.0, 557.0, 610.0)
        ]),
    ]

    for modelo, tipo, constr, uso, diametros in verope_catalog:
        for d, r1960, r2160 in diametros:
            registros.append({
                "Norma_Marca": "Verope", "Tipo": tipo, "Composicion": modelo, "Construccion": constr,
                "Diametro_mm": d, "Peso_kg_m": None, "Rotura_kN_1960": r1960, "Rotura_kN_2160": r2160,
                "Uso_Principal": uso
            })

    # 2. DIN 655
    din_655_B = [
        (9.0, 0.40, 27.9, 0.26, 3650, 4450, 5000), (10.0, 0.45, 35.3, 0.34, 4600, 5650, 6350),
        (11.0, 0.50, 43.6, 0.41, 5650, 7000, 7850), (12.0, 0.55, 52.7, 0.50, 6850, 8450, 9500),
        (13.0, 0.60, 62.8, 0.59, 8150, 10050, 11300), (14.0, 0.65, 73.7, 0.70, 9600, 11800, 13250),
        (16.0, 0.75, 98.1, 0.93, 12750, 15700, 17650), (18.0, 0.80, 111.6, 1.06, 14500, 17850, 20100),
        (20.0, 0.90, 141.2, 1.34, 18350, 22600, 25400), (22.0, 1.00, 174.4, 1.65, 22650, 27900, 31400),
        (24.0, 1.10, 211.0, 2.00, 27450, 33750, 38000), (28.0, 1.20, 251.1, 2.38, 32650, 40200, 45200)
    ]
    for d, d_h, sec, peso, r130, r160, r180 in din_655_B:
        registros.append({
            "Norma_Marca": "DIN 655", "Tipo": "Convencional (Alma Textil)", "Composicion": "6x37 (222 hilos)",
            "Construccion": "Composición B", "Diametro_mm": d, "Peso_kg_m": peso,
            "Rotura_kN_1960": (r160 * 9.81) / 1000.0, "Rotura_kN_2160": (r180 * 9.81) / 1000.0,
            "Uso_Principal": "Puentes grúa / Siderurgia estándar"
        })

    # 3. DIN 656
    din_656_A = [
        (8.0, 26.7, 0.26, 3450, 4250, 4800), (10.0, 39.9, 0.38, 5150, 6350, 7150),
        (12.0, 57.8, 0.55, 7500, 9250, 10400), (14.0, 78.4, 0.75, 10150, 12550, 14100),
        (16.0, 104.5, 1.00, 13550, 16700, 18800), (18.0, 123.8, 1.18, 16050, 19800, 22250),
        (20.0, 159.9, 1.53, 20750, 25550, 28750), (22.0, 187.7, 1.79, 24400, 30000, 33800),
        (24.0, 231.5, 2.20, 30100, 37000, 41650)
    ]
    for d, sec, peso, r130, r160, r180 in din_656_A:
        registros.append({
            "Norma_Marca": "DIN 656", "Tipo": "Seal-Lay", "Composicion": "6x19 (114 hilos)",
            "Construccion": "Composición A", "Diametro_mm": d, "Peso_kg_m": peso,
            "Rotura_kN_1960": (r160 * 9.81) / 1000.0, "Rotura_kN_2160": (r180 * 9.81) / 1000.0,
            "Uso_Principal": "Tambores multicapa / Abrasión"
        })

    return pd.DataFrame(registros)


def verificar_tabla_cables(Q_kg: float = 5000.0, P_ap_kg: float = 150.0, num_ramales: int = 4, coeficiente_seguridad: float = 5.5, *args, **kwargs):
    """
    Evalúa TODOS los cables de la base de datos contra el tiro por ramal (S_max) 
    y categoriza el resultado en 'Óptimo', 'Sobredimensionado' o 'No Verifica'.
    """
    carga_total_kg = Q_kg + P_ap_kg
    S_max_kg = carga_total_kg / num_ramales
    S_max_kN = (S_max_kg * 9.81) / 1000.0
    F_req_kN = S_max_kN * coeficiente_seguridad

    df = obtener_tabla_cables_completa()

    def clasificar_cable(row):
        r_kn = row['Rotura_kN_1960']
        cs_real = r_kn / S_max_kN if S_max_kN > 0 else 0
        
        if cs_real < coeficiente_seguridad:
            estado = "🔴 No Verifica"
        elif cs_real <= (coeficiente_seguridad * 1.35):
            estado = "🟢 Óptimo / Recomendado"
        else:
            estado = "🟡 Sobredimensionado"
            
        return pd.Series([round(cs_real, 2), estado])

    df[['CS_Real', 'Estado_Verificacion']] = df.apply(clasificar_cable, axis=1)

    # Columnas con formato de visualización amigable
    df["Diámetro [mm]"] = df["Diametro_mm"]
    
    return round(S_max_kg, 2), round(F_req_kN, 2), df


# Alias de compatibilidad
seleccionar_cable_mecanismo = verificar_tabla_cables