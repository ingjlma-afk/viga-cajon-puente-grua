# modulo_rueda.py
"""
Dimensionamiento y verificación de ruedas de traslación según norma DIN 15070 / FEM 9.511.
"""
import pandas as pd
import math

def obtener_catalogo_rieles():
    return {
        "DIN 536 A45": {"b_cabeza_mm": 45.0, "b_util_mm": 37.0, "peso_kg_m": 22.1},
        "DIN 536 A55": {"b_cabeza_mm": 55.0, "b_util_mm": 45.0, "peso_kg_m": 31.8},
        "DIN 536 A65": {"b_cabeza_mm": 65.0, "b_util_mm": 55.0, "peso_kg_m": 43.1},
        "DIN 536 A75": {"b_cabeza_mm": 75.0, "b_util_mm": 65.0, "peso_kg_m": 56.2},
        "Cuadrado 50x50": {"b_cabeza_mm": 50.0, "b_util_mm": 44.0, "peso_kg_m": 19.6},
        "Cuadrado 60x60": {"b_cabeza_mm": 60.0, "b_util_mm": 52.0, "peso_kg_m": 28.3},
    }

def obtener_materiales_rueda():
    return {
        "Acero F-1140 / C45 (Normalizado)": {"pl_N_mm2": 6.0},
        "Fundición Nodular GGG-70": {"pl_N_mm2": 7.2},
        "Acero 42CrMo4 Bonificado": {"pl_N_mm2": 8.5},
        "Acero 42CrMo4 Temple Superficial": {"pl_N_mm2": 10.0},
    }

def evaluar_ruedas_traslacion(
    P_rueda_kg: float,
    v_traslacion_m_min: float = 25.0,
    grupo_din: str = "II",
    riel_sel_str: str = "DIN 536 A55",
    material_sel_str: str = "Fundición Nodular GGG-70"
):
    rieles = obtener_catalogo_rieles()
    materiales = obtener_materiales_rueda()
    
    b_u = rieles.get(riel_sel_str, rieles["DIN 536 A55"])["b_util_mm"]
    pl = materiales.get(material_sel_str, materiales["Fundición Nodular GGG-70"])["pl_N_mm2"]
    
    # Coeficiente c2 por grupo según DIN 15070
    c2_dict = {"I": 1.12, "II": 1.00, "III": 0.90, "IV": 0.80, "V": 0.71}
    c2 = c2_dict.get(grupo_din, 1.00)
    
    diametros_std = [200, 250, 315, 400, 500, 630]
    P_N = P_rueda_kg * 9.80665
    
    filas = []
    for D in diametros_std:
        n_rpm = (v_traslacion_m_min * 1000.0) / (math.pi * D)
        
        # Coeficiente c1 aproximado por velocidad de rotación
        if n_rpm <= 10:
            c1 = 1.17
        elif n_rpm <= 16:
            c1 = 1.12
        elif n_rpm <= 25:
            c1 = 1.06
        elif n_rpm <= 31.5:
            c1 = 1.00
        elif n_rpm <= 50:
            c1 = 0.94
        elif n_rpm <= 63:
            c1 = 0.89
        else:
            c1 = 0.83
            
        p_adm = pl * c1 * c2
        p_calc = P_N / (b_u * D)
        
        verifica = p_calc <= p_adm
        estado = "🟢 Verifica" if verifica else "🔴 No Verifica"
        
        filas.append({
            "Estado": estado,
            "Diametro_mm": D,
            "rpm_rueda": round(n_rpm, 1),
            "p_calculada_MPa": round(p_calc, 2),
            "p_admisible_MPa": round(p_adm, 2),
            "Factor_Uso_%": round((p_calc / p_adm) * 100.0, 1)
        })
        
    df = pd.DataFrame(filas)
    return df, b_u