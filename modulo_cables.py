# modulo_cable.py
"""
Módulo de base de datos y selección de cables de acero para puentes grúa.
Incluye tecnología de alto rendimiento (Verope) y normas tradicionales (DIN 655 / DIN 656).
"""

import pandas as pd

def obtener_tabla_cables_completa():
    """
    Retorna la base de datos exhaustiva de cables en un DataFrame de Pandas.
    """
    registros = []

    # 1. CABLES DE ALTO RENDIMIENTO (VEROPE)
    # --------------------------------------------------------------------------
    verope_modelos = {
        "Verotop": {"tipo": "Antigiratorio", "constr": "35x7 Compactado", "uso": "Grúas torre, móviles, elevación principal", "datos": [(8, 56.2, 61.5), (50, 2180.0, 2380.0)]},
        "Verotop E": {"tipo": "Antigiratorio", "constr": "35x7 No compactado", "uso": "Grúas torre y auxiliares", "datos": [(10, 82.1, 89.8), (40, 1300.0, 1420.0)]},
        "Verotop S": {"tipo": "Antigiratorio", "constr": "35x7 Swaged", "uso": "Trabajo pesado, perforadoras", "datos": [(10, 98.5, 108.0), (32, 995.0, 1090.0)]},
        "Verotop P": {"tipo": "Antigiratorio", "constr": "35x7 Plástico/Compactado", "uso": "Grúas offshore, orugas", "datos": [(12, 128.0, 140.0), (46, 1890.0, 2070.0)]},
        "Veropro 8": {"tipo": "No Antigiratorio 8C", "constr": "8x36 Alma Plastificada", "uso": "Grúas puente, portuarias", "datos": [(10, 88.4, 96.8), (50, 2190.0, 2390.0)]},
        "Veropower 8": {"tipo": "No Antigiratorio 8C", "constr": "8x36 Totalmente Compactado", "uso": "Siderurgia, elevación pesada", "datos": [(14, 182.0, 199.0), (60, 3350.0, 3660.0)]},
        "Veropro 6": {"tipo": "No Antigiratorio 6C", "constr": "6x36 Alma Plastificada", "uso": "Excavadoras, tracción", "datos": [(10, 81.2, 88.9), (46, 1710.0, 1870.0)]},
    }

    for modelo, info in verope_modelos.items():
        for d, r1960, r2160 in info["datos"]:
            registros.append({
                "Norma_Marca": "Verope",
                "Tipo": info["tipo"],
                "Composicion": modelo,
                "Construccion": info["constr"],
                "Diametro_mm": d,
                "Peso_kg_m": None,
                "Rotura_kN_1960": r1960,
                "Rotura_kN_2160": r2160,
                "Uso_Principal": info["uso"]
            })

    # 2. CABLES TRADICIONALES DIN 655 (Alma Textil)
    # --------------------------------------------------------------------------
    din_655_A = [
        (6.5, 0.135, 1860, 2300, 2550), (8.0, 0.210, 2900, 3600, 4050),
        (9.5, 0.300, 4200, 5150, 5800), (11.0, 0.410, 5700, 7000, 7900),
        (12.5, 0.540, 7450, 9150, 10300), (14.0, 0.680, 9450, 11600, 13050),
        (16.0, 0.850, 11650, 14300, 16100), (19.0, 1.220, 16750, 20600, 23200),
        (22.0, 1.660, 22800, 28050, 31600)
    ]
    for d, peso, r130, r160, r180 in din_655_A:
        registros.append({
            "Norma_Marca": "DIN 655",
            "Tipo": "Convencional",
            "Composicion": "6x19 (114 hilos)",
            "Construccion": "Composición A",
            "Diametro_mm": d,
            "Peso_kg_m": peso,
            "Rotura_kN_1960": (r160 * 9.81) / 1000,  # Conversión kg a kN aproximada
            "Rotura_kN_2160": (r180 * 9.81) / 1000,
            "Uso_Principal": "Uso general / Puentes grúa pequeños"
        })

    # 3. CABLES TRADICIONALES DIN 656 (Seal-Lay / Warrington)
    # --------------------------------------------------------------------------
    din_656_A = [
        (8.0, 0.26, 3450, 4250, 4800), (10.0, 0.38, 5150, 6350, 7150),
        (12.0, 0.55, 7500, 9250, 10400), (14.0, 0.75, 10150, 12550, 14100),
        (16.0, 1.00, 13550, 16700, 18800), (20.0, 1.53, 20750, 25550, 28750)
    ]
    for d, peso, r130, r160, r180 in din_656_A:
        registros.append({
            "Norma_Marca": "DIN 656",
            "Tipo": "Seal-Lay",
            "Composicion": "6x19 (114 hilos)",
            "Construccion": "Composición A",
            "Diametro_mm": d,
            "Peso_kg_m": peso,
            "Rotura_kN_1960": (r160 * 9.81) / 1000,
            "Rotura_kN_2160": (r180 * 9.81) / 1000,
            "Uso_Principal": "Resistencia al desgaste / Tambores"
        })

    return pd.DataFrame(registros)


def seleccionar_cable_mecanismo(carga_tiro_directo_kg: float, coeficiente_seguridad: float = 5.5):
    """
    Filtra los cables que cumplen con el coeficiente de seguridad requerido.
    """
    fuerza_requerida_kN = (carga_tiro_directo_kg * 9.81 / 1000) * coeficiente_seguridad
    df = obtener_tabla_cables_completa()
    aptos = df[df['Rotura_kN_1960'] >= fuerza_requerida_kN]
    return fuerza_requerida_kN, aptos


if __name__ == "__main__":
    fuerza, tabla_aptos = seleccionar_cable_mecanismo(2500)
    print(f"--- Módulo modulo_cable.py Cargas de Rotura Requeridas: {fuerza:.2f} kN ---")
    print(tabla_aptos[["Norma_Marca", "Composicion", "Diametro_mm", "Rotura_kN_1960"]].to_string())