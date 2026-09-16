# modulo_traslacion.py
"""
Cálculo de potencia motriz y relación de reducción para la traslación del puente grúa.
Normativa: DIN 120 / FEM 9.511. Sistema: Accionamiento bilateral (1 motor por testera).
"""

import math

def calcular_motorreductor_traslacion(
    peso_total_puente_ton: float,
    v_traslacion_m_min: float,
    diametro_rueda_mm: float,
    tiempo_arranque_s: float = 3.0,
    n_motor_rpm: float = 1500.0,
    eta_mecanico: float = 0.88,
    num_motores: int = 2
):
    # 1. Parámetros cinemáticos
    v_ms = v_traslacion_m_min / 60.0
    aceleracion_ms2 = v_ms / tiempo_arranque_s
    n_rueda_rpm = (v_traslacion_m_min * 1000.0) / (math.pi * diametro_rueda_mm)
    i_reduccion_req = n_motor_rpm / n_rueda_rpm if n_rueda_rpm > 0 else 1.0

    # 2. Resistencias al avance
    # Resistencia específica al rodamiento con pestaña (kgf/t)
    w_esp_kgf_ton = 7.0
    W_rodamiento_kgf = peso_total_puente_ton * w_esp_kgf_ton

    # Resistencia por aceleración de masas (kgf)
    g = 9.80665
    masa_kg = peso_total_puente_ton * 1000.0
    beta_rotantes = 1.15
    W_aceleracion_kgf = (masa_kg * aceleracion_ms2 * beta_rotantes) / g

    # 3. Potencias por motor (kW)
    # Régimen permanente
    P_regimen_kw = (W_rodamiento_kgf * v_traslacion_m_min) / (6120.0 * eta_mecanico * num_motores)
    # Régimen de arranque
    P_arranque_kw = ((W_rodamiento_kgf + W_aceleracion_kgf) * v_traslacion_m_min) / (6120.0 * eta_mecanico * num_motores)

    # 4. Potencia nominal normalizada IEC recomendada (considerando sobrecarga transitoria del 180%)
    P_min_termica = P_regimen_kw
    P_min_mecanica = P_arranque_kw / 1.7
    P_adopcion_teorica = max(P_min_termica, P_min_mecanica)

    escalones_iec_kw = [0.55, 0.75, 1.1, 1.5, 2.2, 3.0, 4.0, 5.5, 7.5, 11.0, 15.0]
    pot_motor_iec = escalones_iec_kw[-1]
    for pot in escalones_iec_kw:
        if pot >= P_adopcion_teorica:
            pot_motor_iec = pot
            break

    # Torque en el eje lento (eje de la rueda motriz)
    torque_rueda_Nm = ((W_rodamiento_kgf + W_aceleracion_kgf) * 9.80665 / num_motores) * (diametro_rueda_mm / 2000.0)

    # Coeficiente de adherencia requerido para evitar patinamiento
    # Dos ruedas motrices sobre 4 totales: peso adherente mínimo en vacío
    P_adherente_min_ton = (peso_total_puente_ton * 0.45) / 2.0
    fuerza_traccion_max_kgf = (W_rodamiento_kgf + W_aceleracion_kgf) / num_motores
    mu_calc = fuerza_traccion_max_kgf / (P_adherente_min_ton * 1000.0)
    verifica_adherencia = mu_calc <= 0.14  # Límite anti-patinamiento sin arena

    return {
        "n_rueda_rpm": round(n_rueda_rpm, 1),
        "i_requerido": round(i_reduccion_req, 1),
        "W_rodamiento_kgf": round(W_rodamiento_kgf, 1),
        "W_aceleracion_kgf": round(W_aceleracion_kgf, 1),
        "P_regimen_kw": round(P_regimen_kw, 2),
        "P_arranque_kw": round(P_arranque_kw, 2),
        "pot_motor_iec_kw": pot_motor_iec,
        "torque_rueda_Nm": round(torque_rueda_Nm, 1),
        "mu_calc": round(mu_calc, 3),
        "verifica_adherencia": verifica_adherencia
    }