# modulo_testera.py
"""
Módulo para dimensionamiento y verificación técnica de Testeras (End Carriages)
según normas DIN 120 / DIN 15020 / FEM 1001.
Soporta configuraciones Monoviga y Birraíl (Doble Viga).
"""

import math
import pandas as pd

def obtener_catalogo_perfiles_testera():
    """
    Catálogo de secciones estándar compuestas por 2 perfiles UPN enfrentados en cajón cerrado.
    """
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
    perfil_seleccionado_str: str = "2x UPN 300",
    sigma_adm_kgf_cm2: float = 1400.0
):
    L_mm = Luz_puente_m * 1000.0
    
    # 1. Batalla recomendada de ruedas (L/7 a L/6)
    at_min_norma_mm = L_mm / 7.0
    at_rec_norma_mm = L_mm / 6.0
    
    # 2. Cargas que descargan en la testera más solicitada (carro en acercamiento mínimo e)
    # Reacción estática debida a carga móvil (Q + Carro)
    P_movil_total = Q_carga_kg + peso_carro_total_kg
    e_mm = min(acercamiento_min_e_mm, L_mm / 2.0)
    
    R_movil_max_kg = P_movil_total * ((L_mm - e_mm) / L_mm)
    
    # Reacción por peso propio de vigas (si es birraíl son 2 vigas, si es monoviga es 1)
    num_vigas = 2 if es_birrail else 1
    peso_vigas_total_kg = num_vigas * (peso_lineal_viga_kg_m * Luz_puente_m)
    R_vigas_kg = peso_vigas_total_kg / 2.0  # Mitad a cada testera
    
    # Peso accesorio de pasarela, mecanismos de traslación en testera
    peso_accesorios_testera_kg = 500.0
    
    R_total_testera_kg = R_movil_max_kg + R_vigas_kg + (peso_accesorios_testera_kg / 2.0)
    
    # Carga por rueda de traslación del puente (2 ruedas por testera)
    P_rueda_max_kg = R_total_testera_kg / 2.0
    P_rueda_max_ton = P_rueda_max_kg / 1000.0
    
    # 3. Momento Flector en la testera
    at_cm = batalla_adoptada_at_mm / 10.0
    
    if es_birrail:
        # En Doble Viga: Las dos vigas cajón apoyan separadas a la trocha del carro (al)
        # La distancia desde cada rueda al apoyo de su respectiva viga es x = (at - al) / 2
        al_mm = distancia_ruedas_carro_al_mm
        if batalla_adoptada_at_mm > al_mm:
            brazo_x_cm = (batalla_adoptada_at_mm - al_mm) / 20.0
        else:
            brazo_x_cm = 15.0  # Valor de resguardo
        # Momento entre el apoyo de la viga y la rueda
        M_testera_kgf_cm = P_rueda_max_kg * brazo_x_cm
    else:
        # En Monoviga: Carga concentrada única en el centro de la testera
        # M = (R_total * at) / 4
        brazo_x_cm = at_cm / 2.0
        M_testera_kgf_cm = (R_total_testera_kg * at_cm) / 4.0

    # 4. Evaluación de perfiles
    df_perfiles = obtener_catalogo_perfiles_testera()
    df_perfiles["Tension_kgf_cm2"] = (M_testera_kgf_cm / df_perfiles["Wx_cm3"]).round(1)
    
    def estado(sigma):
        if sigma <= sigma_adm_kgf_cm2:
            return "🟢 Verifica"
        else:
            return "🔴 No Verifica"
            
    df_perfiles["Estado"] = df_perfiles["Tension_kgf_cm2"].apply(estado)
    
    # Perfil adoptado
    perfil_fila = df_perfiles[df_perfiles["Perfil"] == perfil_seleccionado_str]
    if perfil_fila.empty:
        perfil_fila = df_perfiles.iloc[2]  # Default 2x UPN 260
    else:
        perfil_fila = perfil_fila.iloc[0]
        
    sigma_real = float(perfil_fila["Tension_kgf_cm2"])
    peso_lineal_t = float(perfil_fila["Peso_kg_m"])
    peso_propio_testera_kg = (peso_lineal_t * (batalla_adoptada_at_mm / 1000.0)) + 350.0  # Incluye ruedas y ejes

    return {
        "at_min_norma_mm": round(at_min_norma_mm, 0),
        "at_rec_norma_mm": round(at_rec_norma_mm, 0),
        "R_total_testera_ton": round(R_total_testera_kg / 1000.0, 2),
        "P_rueda_max_kg": round(P_rueda_max_kg, 1),
        "P_rueda_max_ton": round(P_rueda_max_ton, 2),
        "M_testera_kNm": round((M_testera_kgf_cm * 9.80665) / 100000.0, 2),
        "sigma_real_kgf_cm2": sigma_real,
        "verifica_sigma": sigma_real <= sigma_adm_kgf_cm2,
        "peso_propio_testera_kg": round(peso_propio_testera_kg, 1),
        "tabla_perfiles": df_perfiles
    }