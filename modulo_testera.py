# modulo_testera.py
import math
import pandas as pd

def obtener_catalogo_perfiles_testera():
    perfiles = [
        {"Perfil": "2x UPN 220", "h_mm": 220, "b_mm": 160, "Ix_cm4": 5380,  "Wx_cm3": 490,  "Iy_cm4": 4100,  "Wy_cm3": 380,  "Peso_kg_m": 58.8},
        {"Perfil": "2x UPN 240", "h_mm": 240, "b_mm": 170, "Ix_cm4": 7200,  "Wx_cm3": 600,  "Iy_cm4": 5600,  "Wy_cm3": 470,  "Peso_kg_m": 66.4},
        {"Perfil": "2x UPN 260", "h_mm": 260, "b_mm": 180, "Ix_cm4": 9640,  "Wx_cm3": 742,  "Iy_cm4": 7500,  "Wy_cm3": 580,  "Peso_kg_m": 75.8},
        {"Perfil": "2x UPN 300", "h_mm": 300, "b_mm": 200, "Ix_cm4": 16060, "Wx_cm3": 1070, "Iy_cm4": 12200, "Wy_cm3": 810,  "Peso_kg_m": 92.4},
        {"Perfil": "2x UPN 350", "h_mm": 350, "b_mm": 200, "Ix_cm4": 25680, "Wx_cm3": 1468, "Iy_cm4": 16500, "Wy_cm3": 1030, "Peso_kg_m": 121.2},
        {"Perfil": "2x UPN 400", "h_mm": 400, "b_mm": 220, "Ix_cm4": 40700, "Wx_cm3": 2040, "Iy_cm4": 24800, "Wy_cm3": 1410, "Peso_kg_m": 143.6},
    ]
    return pd.DataFrame(perfiles)

def calcular_testera(
    Luz_puente_m: float,
    es_birrail: bool,
    distancia_ruedas_carro_al_mm: float,
    peso_lineal_viga_kg_m: float,
    peso_carro_total_kg: float,
    Q_carga_kg: float,
    acercamiento_min_e_mm: float = 1200.0,
    batalla_adoptada_at_mm: float = 3000.0,
    modo_seccion: str = "Catálogo Comercial (2x UPN en Cajón)",
    perfil_seleccionado_str: str = "2x UPN 260",
    prop_dxf: dict = None,
    sigma_adm_kgf_cm2: float = 1400.0
):
    L_mm = Luz_puente_m * 1000.0
    at_min_norma_mm = L_mm / 7.0
    at_rec_norma_mm = L_mm / 6.0
    
    # Cargas en juego
    P_movil_total = Q_carga_kg + peso_carro_total_kg
    num_vigas = 2 if es_birrail else 1
    peso_vigas_total_kg = num_vigas * (peso_lineal_viga_kg_m * Luz_puente_m)
    
    # Peso estático de pasarelas y accesorios en testeras
    peso_accesorios_kg = 500.0
    
    # Peso total absoluto del conjunto completo sobre las 2 testeras
    Peso_total_puente_cargado_kg = P_movil_total + peso_vigas_total_kg + peso_accesorios_kg
    
    # Distribución estática entre apoyos (Testera 1 próxima al carro vs Testera 2 lejana)
    e_mm = min(acercamiento_min_e_mm, L_mm / 2.0)
    
    # Testera A (Crítica): Carro al extremo
    R_movil_max_kg = P_movil_total * ((L_mm - e_mm) / L_mm)
    R_vigas_por_testera_kg = peso_vigas_total_kg / 2.0
    R_max_testera_kg = R_movil_max_kg + R_vigas_por_testera_kg + (peso_accesorios_kg / 2.0)
    
    # Testera B (Descargada en ese mismo instante)
    R_min_testera_kg = (P_movil_total - R_movil_max_kg) + R_vigas_por_testera_kg + (peso_accesorios_kg / 2.0)
    
    # Carga por rueda en la testera crítica (2 ruedas por testera)
    P_rueda_max_kg = R_max_testera_kg / 2.0
    P_rueda_min_kg = R_min_testera_kg / 2.0
    
    # Momento Flector en la testera crítica
    at_cm = batalla_adoptada_at_mm / 10.0
    if es_birrail:
        al_mm = distancia_ruedas_carro_al_mm
        brazo_x_cm = max(10.0, (batalla_adoptada_at_mm - al_mm) / 20.0)
        M_testera_kgf_cm = P_rueda_max_kg * brazo_x_cm
    else:
        M_testera_kgf_cm = (R_max_testera_kg * at_cm) / 4.0

    # Propiedades resistentes
    df_perfiles = obtener_catalogo_perfiles_testera()
    df_perfiles["Tension_kgf_cm2"] = (M_testera_kgf_cm / df_perfiles["Wx_cm3"]).round(1)
    df_perfiles["Estado"] = df_perfiles["Tension_kgf_cm2"].apply(lambda s: "🟢 Verifica" if s <= sigma_adm_kgf_cm2 else "🔴 No Verifica")

    if "DXF" in modo_seccion and prop_dxf is not None:
        Wx_real = prop_dxf['Wx']
        peso_lineal_t = prop_dxf['Pp']
        nombre_seccion = "Sección Especial DXF"
    else:
        perfil_fila = df_perfiles[df_perfiles["Perfil"] == perfil_seleccionado_str]
        perfil_fila = perfil_fila.iloc[0] if not perfil_fila.empty else df_perfiles.iloc[2]
        Wx_real = float(perfil_fila["Wx_cm3"])
        peso_lineal_t = float(perfil_fila["Peso_kg_m"])
        nombre_seccion = perfil_seleccionado_str

    sigma_real = (M_testera_kgf_cm / Wx_real) if Wx_real > 0 else 0.0
    peso_propio_testera_kg = (peso_lineal_t * (batalla_adoptada_at_mm / 1000.0)) + 350.0

    return {
        "at_min_norma_mm": round(at_min_norma_mm, 0),
        "at_rec_norma_mm": round(at_rec_norma_mm, 0),
        "Peso_total_puente_cargado_ton": round(Peso_total_puente_cargado_kg / 1000.0, 2),
        "R_max_testera_ton": round(R_max_testera_kg / 1000.0, 2),
        "R_min_testera_ton": round(R_min_testera_kg / 1000.0, 2),
        "P_rueda_max_ton": round(P_rueda_max_kg / 1000.0, 2),
        "P_rueda_max_kg": round(P_rueda_max_kg, 1),
        "P_rueda_min_ton": round(P_rueda_min_kg / 1000.0, 2),
        "M_testera_kNm": round((M_testera_kgf_cm * 9.80665) / 100000.0, 2),
        "sigma_real_kgf_cm2": round(sigma_real, 1),
        "verifica_sigma": sigma_real <= sigma_adm_kgf_cm2,
        "peso_propio_testera_kg": round(peso_propio_testera_kg, 1),
        "Wx_cm3": round(Wx_real, 1),
        "peso_lineal_kg_m": round(peso_lineal_t, 2),
        "tabla_perfiles": df_perfiles
    }