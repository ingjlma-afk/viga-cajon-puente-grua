# modulo_cables.py
import pandas as pd

def obtener_catalogo_cables_completo():
    cables = [
        # DIN 655 Comp. A (6x19)
        {"Norma_Marca": "DIN 655 (6x19)", "Composicion": "6x19 + 1 AT", "Diametro_mm": 8.0,  "Peso_kg_m": 0.21, "Rotura_kgf": 3600,  "Rotura_kN_1960": 35.32},
        {"Norma_Marca": "DIN 655 (6x19)", "Composicion": "6x19 + 1 AT", "Diametro_mm": 10.0, "Peso_kg_m": 0.30, "Rotura_kgf": 5150,  "Rotura_kN_1960": 50.52},
        {"Norma_Marca": "DIN 655 (6x19)", "Composicion": "6x19 + 1 AT", "Diametro_mm": 12.5, "Peso_kg_m": 0.54, "Rotura_kgf": 9150,  "Rotura_kN_1960": 89.76},
        {"Norma_Marca": "DIN 655 (6x19)", "Composicion": "6x19 + 1 AT", "Diametro_mm": 14.0, "Peso_kg_m": 0.68, "Rotura_kgf": 11600, "Rotura_kN_1960": 113.80},
        {"Norma_Marca": "DIN 655 (6x19)", "Composicion": "6x19 + 1 AT", "Diametro_mm": 16.0, "Peso_kg_m": 0.85, "Rotura_kgf": 14300, "Rotura_kN_1960": 140.29},
        {"Norma_Marca": "DIN 655 (6x19)", "Composicion": "6x19 + 1 AT", "Diametro_mm": 17.5, "Peso_kg_m": 1.02, "Rotura_kgf": 17350, "Rotura_kN_1960": 170.20},
        {"Norma_Marca": "DIN 655 (6x19)", "Composicion": "6x19 + 1 AT", "Diametro_mm": 19.0, "Peso_kg_m": 1.22, "Rotura_kgf": 20600, "Rotura_kN_1960": 202.09},
        {"Norma_Marca": "DIN 655 (6x19)", "Composicion": "6x19 + 1 AT", "Diametro_mm": 20.0, "Peso_kg_m": 1.43, "Rotura_kgf": 24200, "Rotura_kN_1960": 237.40},
        {"Norma_Marca": "DIN 655 (6x19)", "Composicion": "6x19 + 1 AT", "Diametro_mm": 22.0, "Peso_kg_m": 1.66, "Rotura_kgf": 28050, "Rotura_kN_1960": 275.17},

        # DIN 655 Comp. B (6x37)
        {"Norma_Marca": "DIN 655 (6x37)", "Composicion": "6x37 + 1 AT", "Diametro_mm": 12.0, "Peso_kg_m": 0.50, "Rotura_kgf": 8450,  "Rotura_kN_1960": 82.89},
        {"Norma_Marca": "DIN 655 (6x37)", "Composicion": "6x37 + 1 AT", "Diametro_mm": 14.0, "Peso_kg_m": 0.70, "Rotura_kgf": 11800, "Rotura_kN_1960": 115.76},
        {"Norma_Marca": "DIN 655 (6x37)", "Composicion": "6x37 + 1 AT", "Diametro_mm": 16.0, "Peso_kg_m": 0.93, "Rotura_kgf": 15700, "Rotura_kN_1960": 154.02},
        {"Norma_Marca": "DIN 655 (6x37)", "Composicion": "6x37 + 1 AT", "Diametro_mm": 18.0, "Peso_kg_m": 1.14, "Rotura_kgf": 19300, "Rotura_kN_1960": 189.33},
        {"Norma_Marca": "DIN 655 (6x37)", "Composicion": "6x37 + 1 AT", "Diametro_mm": 20.0, "Peso_kg_m": 1.34, "Rotura_kgf": 22600, "Rotura_kN_1960": 221.71},
        {"Norma_Marca": "DIN 655 (6x37)", "Composicion": "6x37 + 1 AT", "Diametro_mm": 24.0, "Peso_kg_m": 2.00, "Rotura_kgf": 33750, "Rotura_kN_1960": 331.09},
        {"Norma_Marca": "DIN 655 (6x37)", "Composicion": "6x37 + 1 AT", "Diametro_mm": 28.0, "Peso_kg_m": 2.80, "Rotura_kgf": 47150, "Rotura_kN_1960": 462.54},
        {"Norma_Marca": "DIN 655 (6x37)", "Composicion": "6x37 + 1 AT", "Diametro_mm": 32.0, "Peso_kg_m": 3.72, "Rotura_kgf": 62750, "Rotura_kN_1960": 615.58},

        # Verope Veropro 8[cite: 2]
        {"Norma_Marca": "Verope Veropro 8", "Composicion": "8 compactados + alma plástica", "Diametro_mm": 10.0, "Peso_kg_m": 0.450, "Rotura_kgf": 9185,  "Rotura_kN_1960": 90.1},
        {"Norma_Marca": "Verope Veropro 8", "Composicion": "8 compactados + alma plástica", "Diametro_mm": 12.0, "Peso_kg_m": 0.648, "Rotura_kgf": 13231, "Rotura_kN_1960": 129.8},
        {"Norma_Marca": "Verope Veropro 8", "Composicion": "8 compactados + alma plástica", "Diametro_mm": 14.0, "Peso_kg_m": 0.882, "Rotura_kgf": 18012, "Rotura_kN_1960": 176.7},
        {"Norma_Marca": "Verope Veropro 8", "Composicion": "8 compactados + alma plástica", "Diametro_mm": 16.0, "Peso_kg_m": 1.152, "Rotura_kgf": 23517, "Rotura_kN_1960": 230.7},
        {"Norma_Marca": "Verope Veropro 8", "Composicion": "8 compactados + alma plástica", "Diametro_mm": 18.0, "Peso_kg_m": 1.457, "Rotura_kgf": 29766, "Rotura_kN_1960": 292.0},
        {"Norma_Marca": "Verope Veropro 8", "Composicion": "8 compactados + alma plástica", "Diametro_mm": 20.0, "Peso_kg_m": 1.799, "Rotura_kgf": 36748, "Rotura_kN_1960": 360.5},
        {"Norma_Marca": "Verope Veropro 8", "Composicion": "8 compactados + alma plástica", "Diametro_mm": 22.0, "Peso_kg_m": 2.177, "Rotura_kgf": 44465, "Rotura_kN_1960": 436.2},
        {"Norma_Marca": "Verope Veropro 8", "Composicion": "8 compactados + alma plástica", "Diametro_mm": 24.0, "Peso_kg_m": 2.591, "Rotura_kgf": 52915, "Rotura_kN_1960": 519.1},
        {"Norma_Marca": "Verope Veropro 8", "Composicion": "8 compactados + alma plástica", "Diametro_mm": 26.0, "Peso_kg_m": 3.041, "Rotura_kgf": 62110, "Rotura_kN_1960": 609.3},
        {"Norma_Marca": "Verope Veropro 8", "Composicion": "8 compactados + alma plástica", "Diametro_mm": 28.0, "Peso_kg_m": 3.527, "Rotura_kgf": 72029, "Rotura_kN_1960": 706.6},

        # Verope Veropower 8[cite: 2]
        {"Norma_Marca": "Verope Veropower 8", "Composicion": "8 martillados paralelos", "Diametro_mm": 12.0, "Peso_kg_m": 0.717, "Rotura_kgf": 15025, "Rotura_kN_1960": 147.4},
        {"Norma_Marca": "Verope Veropower 8", "Composicion": "8 martillados paralelos", "Diametro_mm": 14.0, "Peso_kg_m": 0.976, "Rotura_kgf": 20448, "Rotura_kN_1960": 200.6},
        {"Norma_Marca": "Verope Veropower 8", "Composicion": "8 martillados paralelos", "Diametro_mm": 16.0, "Peso_kg_m": 1.275, "Rotura_kgf": 26707, "Rotura_kN_1960": 262.0},
        {"Norma_Marca": "Verope Veropower 8", "Composicion": "8 martillados paralelos", "Diametro_mm": 18.0, "Peso_kg_m": 1.614, "Rotura_kgf": 33802, "Rotura_kN_1960": 331.6},
        {"Norma_Marca": "Verope Veropower 8", "Composicion": "8 martillados paralelos", "Diametro_mm": 20.0, "Peso_kg_m": 1.992, "Rotura_kgf": 41733, "Rotura_kN_1960": 409.4},
        {"Norma_Marca": "Verope Veropower 8", "Composicion": "8 martillados paralelos", "Diametro_mm": 22.0, "Peso_kg_m": 2.411, "Rotura_kgf": 50489, "Rotura_kN_1960": 495.3},
        {"Norma_Marca": "Verope Veropower 8", "Composicion": "8 martillados paralelos", "Diametro_mm": 24.0, "Peso_kg_m": 2.869, "Rotura_kgf": 60092, "Rotura_kN_1960": 589.5},

        # Verope Verotop Antigiratorio[cite: 2]
        {"Norma_Marca": "Verope Verotop", "Composicion": "Antigiratorio multitorón", "Diametro_mm": 10.0, "Peso_kg_m": 0.490, "Rotura_kgf": 9725,  "Rotura_kN_1960": 95.4},
        {"Norma_Marca": "Verope Verotop", "Composicion": "Antigiratorio multitorón", "Diametro_mm": 12.0, "Peso_kg_m": 0.705, "Rotura_kgf": 14006, "Rotura_kN_1960": 137.4},
        {"Norma_Marca": "Verope Verotop", "Composicion": "Antigiratorio multitorón", "Diametro_mm": 14.0, "Peso_kg_m": 0.960, "Rotura_kgf": 19062, "Rotura_kN_1960": 187.0},
        {"Norma_Marca": "Verope Verotop", "Composicion": "Antigiratorio multitorón", "Diametro_mm": 16.0, "Peso_kg_m": 1.254, "Rotura_kgf": 24903, "Rotura_kN_1960": 244.3},
        {"Norma_Marca": "Verope Verotop", "Composicion": "Antigiratorio multitorón", "Diametro_mm": 18.0, "Peso_kg_m": 1.587, "Rotura_kgf": 31519, "Rotura_kN_1960": 309.2},
        {"Norma_Marca": "Verope Verotop", "Composicion": "Antigiratorio multitorón", "Diametro_mm": 20.0, "Peso_kg_m": 1.959, "Rotura_kgf": 38909, "Rotura_kN_1960": 381.7},
        {"Norma_Marca": "Verope Verotop", "Composicion": "Antigiratorio multitorón", "Diametro_mm": 22.0, "Peso_kg_m": 2.371, "Rotura_kgf": 47085, "Rotura_kN_1960": 461.9},
        {"Norma_Marca": "Verope Verotop", "Composicion": "Antigiratorio multitorón", "Diametro_mm": 24.0, "Peso_kg_m": 2.821, "Rotura_kgf": 56035, "Rotura_kN_1960": 549.7},
    ]
    return pd.DataFrame(cables)

def verificar_tabla_cables(Q_kg: float, P_ap_kg: float, num_ramales: int, eta_poleas: float = 0.98, grupo_din: str = "II", coef_seguridad: float = 5.0, *args, **kwargs):
    n_poleas = max(1, num_ramales // 2)
    rend_mecanismo = eta_poleas ** n_poleas
    
    # Tiro máximo en el cable
    S_max = ((Q_kg + P_ap_kg) / (num_ramales * rend_mecanismo))
    F_req = S_max * coef_seguridad

    df = obtener_catalogo_cables_completo()
    
    # Cálculo del coeficiente de seguridad real
    df["CS_Real"] = (df["Rotura_kgf"] / S_max).round(2)
    df["Zp_Real"] = df["CS_Real"]

    # Criterio de clasificación según norma
    def clasificar(r):
        cs = r["CS_Real"]
        if cs < coef_seguridad:
            return "🔴 No Verifica (Inseguro)"
        elif coef_seguridad <= cs <= (coef_seguridad * 1.8):
            return "🟢 Óptimo / Recomendado"
        else:
            return "🟡 Sobredimensionado"

    df["Estado_Verificacion"] = df.apply(clasificar, axis=1)
    df["Estado"] = df["Estado_Verificacion"]
    
    return round(S_max, 2), round(F_req, 2), df

verificar_cable_elevacion = verificar_tabla_cables
obtener_tabla_cables_completa = obtener_catalogo_cables_completo