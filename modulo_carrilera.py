# modulo_carrilera.py
"""
Dimensionamiento y verificación estructural de Vigas Carrileras de Alma Llena
según normas DIN 4132 / DIN 120 / CIRSOC 301.
Soporta vigas armadas soldadas, perfiles con refuerzo UPN o sección personalizada por DXF.
"""

import math
import pandas as pd

def obtener_catalogo_carrileras_estandar():
    """
    Catálogo de perfiles comerciales típicos para carrileras con refuerzo de flexión lateral (UPN en ala superior).
    """
    perfiles = [
        {"Nombre": "HEB 300 + UPN 260", "Ix_cm4": 30500.0, "Wx_cm3": 1850.0, "Iy_sup_cm4": 7500.0, "Wy_sup_cm3": 580.0, "h_mm": 300, "b_mm": 300, "Peso_kg_m": 155.0},
        {"Nombre": "HEB 360 + UPN 300", "Ix_cm4": 52400.0, "Wx_cm3": 2680.0, "Iy_sup_cm4": 12200.0, "Wy_sup_cm3": 810.0, "h_mm": 360, "b_mm": 300, "Peso_kg_m": 188.0},
        {"Nombre": "HEB 400 + UPN 300", "Ix_cm4": 69200.0, "Wx_cm3": 3220.0, "Iy_sup_cm4": 12800.0, "Wy_sup_cm3": 850.0, "h_mm": 400, "b_mm": 300, "Peso_kg_m": 201.0},
        {"Nombre": "HEB 450 + UPN 350", "Ix_cm4": 97800.0, "Wx_cm3": 4120.0, "Iy_sup_cm4": 16500.0, "Wy_sup_cm3": 1030.0, "h_mm": 450, "b_mm": 300, "Peso_kg_m": 232.0},
        {"Nombre": "HEB 500 + UPN 400", "Ix_cm4": 135000.0, "Wx_cm3": 5150.0, "Iy_sup_cm4": 24800.0, "Wy_sup_cm3": 1410.0, "h_mm": 500, "b_mm": 300, "Peso_kg_m": 272.0},
    ]
    return pd.DataFrame(perfiles)

def calcular_propiedades_viga_armada(hw_mm, tw_mm, bf_mm, tf_mm):
    """
    Calcula propiedades de una sección en Doble T simétrica armada soldada.
    """
    hw_cm, tw_cm = hw_mm / 10.0, tw_mm / 10.0
    bf_cm, tf_cm = bf_mm / 10.0, tf_mm / 10.0
    
    # Inercia X
    Ix_alma = (tw_cm * (hw_cm**3)) / 12.0
    Ix_alas = 2.0 * ((bf_cm * (tf_cm**3)) / 12.0 + (bf_cm * tf_cm * ((hw_cm/2.0 + tf_cm/2.0)**2)))
    Ix_cm4 = Ix_alma + Ix_alas
    h_total_cm = hw_cm + 2.0 * tf_cm
    Wx_cm3 = Ix_cm4 / (h_total_cm / 2.0)
    
    # Inercia Y del ala superior (para absorber corte lateral)
    Iy_sup_cm4 = (tf_cm * (bf_cm**3)) / 12.0
    Wy_sup_cm3 = Iy_sup_cm4 / (bf_cm / 2.0)
    
    # Inercia Y total
    Iy_total_cm4 = 2.0 * Iy_sup_cm4 + (hw_cm * (tw_cm**3)) / 12.0
    
    # Peso propio lineal
    Area_cm2 = tw_cm * hw_cm + 2.0 * (bf_cm * tf_cm)
    Peso_kg_m = (Area_cm2 / 10000.0) * 7850.0
    
    return {
        "Ix_cm4": Ix_cm4,
        "Wx_cm3": Wx_cm3,
        "Iy_sup_cm4": Iy_sup_cm4,
        "Wy_sup_cm3": Wy_sup_cm3,
        "Iy_total_cm4": Iy_total_cm4,
        "Peso_kg_m": Peso_kg_m,
        "h_mm": h_total_cm * 10.0,
        "b_mm": bf_mm
    }

def calcular_carrilera(
    Luz_columnas_m: float,
    batalla_testera_at_mm: float,
    P_rueda_max_kg: float,
    peso_riel_kg_m: float = 35.0,
    modo_seccion: str = "Perfil Comercial + UPN Refuerzo",
    perfil_comercial_str: str = "HEB 400 + UPN 300",
    prop_armada: dict = None,
    prop_dxf: dict = None,
    phi_carrilera: float = 1.20,
    sigma_adm_kgf_cm2: float = 1400.0,
    E_kgf_cm2: float = 2100000.0
):
    Lc_cm = Luz_columnas_m * 100.0
    at_cm = batalla_testera_at_mm / 10.0
    Pr_kg = P_rueda_max_kg
    
    # 1. Momento flector vertical debido a las ruedas móviles (Teorema de Barré)
    if at_cm < Lc_cm:
        # 2 ruedas de la testera entran en el vano
        # Posición pésima: resultante y una rueda equidistan del centro
        M_ruedas_kgf_cm = (2.0 * Pr_kg / Lc_cm) * ((Lc_cm / 2.0 - at_cm / 4.0)**2)
    else:
        # Batalla más larga que el vano: solo entra una rueda al centro
        M_ruedas_kgf_cm = (Pr_kg * Lc_cm) / 4.0
        
    # Momento vertical dinámico por ruedas
    M_v_din_kgf_cm = M_ruedas_kgf_cm * phi_carrilera

    # 2. Selección de propiedades resistentes de la sección
    if modo_seccion == "Perfil Comercial + UPN Refuerzo":
        df_cat = obtener_catalogo_carrileras_estandar()
        fila = df_cat[df_cat["Nombre"] == perfil_comercial_str]
        fila = fila.iloc[0] if not fila.empty else df_cat.iloc[2]
        Ix = float(fila["Ix_cm4"])
        Wx = float(fila["Wx_cm3"])
        Iy_sup = float(fila["Iy_sup_cm4"])
        Wy_sup = float(fila["Wy_sup_cm3"])
        Pp_carrilera = float(fila["Peso_kg_m"])
        nombre_sec = perfil_comercial_str
    elif modo_seccion == "Viga Armada Soldada (Doble T)" and prop_armada is not None:
        Ix = prop_armada["Ix_cm4"]
        Wx = prop_armada["Wx_cm3"]
        Iy_sup = prop_armada["Iy_sup_cm4"]
        Wy_sup = prop_armada["Wy_sup_cm3"]
        Pp_carrilera = prop_armada["Peso_kg_m"]
        nombre_sec = f"Soldada {prop_armada['h_mm']:.0f}x{prop_armada['b_mm']:.0f}"
    elif "DXF" in modo_seccion and prop_dxf is not None:
        Ix = prop_dxf["Jx"]
        Wx = prop_dxf["Wx"]
        Iy_sup = prop_dxf["Jy"] / 2.0  # Estimación aproximada del ala superior
        Wy_sup = prop_dxf["Wy"] / 1.5
        Pp_carrilera = prop_dxf["Pp"]
        nombre_sec = "Sección Especial CAD (DXF)"
    else:
        # Resguardo por defecto
        Ix, Wx, Iy_sup, Wy_sup, Pp_carrilera = 69200.0, 3220.0, 12800.0, 850.0, 201.0
        nombre_sec = "HEB 400 + UPN 300"

    # 3. Momento flector vertical por peso propio (viga carrilera + riel)
    q_propio_kg_m = Pp_carrilera + peso_riel_kg_m
    M_propio_kgf_cm = (q_propio_kg_m * (Luz_columnas_m**2) / 8.0) * 100.0

    # Momento vertical total
    M_v_total_kgf_cm = M_v_din_kgf_cm + M_propio_kgf_cm
    
    # 4. Solicitación horizontal transversal (guiado lateral / choque de pestaña DIN 4132)
    # Fuerza lateral por rueda = 1/10 de la carga vertical
    H_rueda_kg = Pr_kg / 10.0
    if at_cm < Lc_cm:
        M_h_total_kgf_cm = (2.0 * H_rueda_kg / Lc_cm) * ((Lc_cm / 2.0 - at_cm / 4.0)**2)
    else:
        M_h_total_kgf_cm = (H_rueda_kg * Lc_cm) / 4.0

    # 5. Tensiones normales en el ala superior (Flexión Biaxial)
    sigma_v = M_v_total_kgf_cm / Wx if Wx > 0 else 0.0
    sigma_h = M_h_total_kgf_cm / Wy_sup if Wy_sup > 0 else 0.0
    sigma_comb = sigma_v + sigma_h
    verifica_tension = sigma_comb <= sigma_adm_kgf_cm2

    # 6. Verificación de flechas de servicio elásticas
    # Flecha vertical (admisible L/600)
    # Para 2 cargas móviles simétricas en proximidad del centro
    f_adm_v_cm = Lc_cm / 600.0
    if at_cm < Lc_cm:
        # Fórmula clásica aproximada de 2 ruedas simétricas
        a_apoyo_cm = (Lc_cm - at_cm) / 2.0
        f_v_calc_cm = (Pr_kg * a_apoyo_cm / (24.0 * E_kgf_cm2 * Ix)) * (3.0 * (Lc_cm**2) - 4.0 * (a_apoyo_cm**2))
    else:
        f_v_calc_cm = (Pr_kg * (Lc_cm**3)) / (48.0 * E_kgf_cm2 * Ix)
        
    verifica_flecha_v = f_v_calc_cm <= f_adm_v_cm

    # Flecha horizontal (admisible L/1000)
    f_adm_h_cm = Lc_cm / 1000.0
    if at_cm < Lc_cm:
        a_apoyo_cm = (Lc_cm - at_cm) / 2.0
        f_h_calc_cm = (H_rueda_kg * a_apoyo_cm / (24.0 * E_kgf_cm2 * Iy_sup)) * (3.0 * (Lc_cm**2) - 4.0 * (a_apoyo_cm**2))
    else:
        f_h_calc_cm = (H_rueda_kg * (Lc_cm**3)) / (48.0 * E_kgf_cm2 * Iy_sup)
        
    verifica_flecha_h = f_h_calc_cm <= f_adm_h_cm

    return {
        "nombre_seccion": nombre_sec,
        "Ix_cm4": round(Ix, 1),
        "Wx_cm3": round(Wx, 1),
        "Iy_sup_cm4": round(Iy_sup, 1),
        "Wy_sup_cm3": round(Wy_sup, 1),
        "peso_lineal_total_kg_m": round(q_propio_kg_m, 1),
        "M_v_kNm": round((M_v_total_kgf_cm * 9.80665) / 100000.0, 2),
        "M_h_kNm": round((M_h_total_kgf_cm * 9.80665) / 100000.0, 2),
        "sigma_v_kgf_cm2": round(sigma_v, 1),
        "sigma_h_kgf_cm2": round(sigma_h, 1),
        "sigma_comb_kgf_cm2": round(sigma_comb, 1),
        "verifica_tension": verifica_tension,
        "f_v_calc_mm": round(f_v_calc_cm * 10.0, 2),
        "f_adm_v_mm": round(f_adm_v_cm * 10.0, 2),
        "verifica_flecha_v": verifica_flecha_v,
        "f_h_calc_mm": round(f_h_calc_cm * 10.0, 2),
        "f_adm_h_mm": round(f_adm_h_cm * 10.0, 2),
        "verifica_flecha_h": verifica_flecha_h,
    }