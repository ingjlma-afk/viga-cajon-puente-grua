# modulo_direccion.py
"""
Cálculo del mecanismo de dirección / traslación transversal del carro o polipasto.
Normativa: DIN 15020 / FEM 9.511.
"""

import math

def calcular_motor_direccion_carro(
    Q_carga_kg: float,
    peso_carro_kg: float,
    v_direccion_m_min: float = 16.0,
    diametro_rueda_carro_mm: float = 250.0,
    tiempo_arranque_s: float = 2.5,
    n_motor_rpm: float = 1500.0,
    eta_mecanico: float = 0.85,
    es_birrail: bool = True
):
    # Masa total solicitante del carro
    peso_total_kg = Q_carga_kg + peso_carro_kg
    peso_total_ton = peso_total_kg / 1000.0

    # Cinemática
    v_ms = v_direccion_m_min / 60.0
    aceleracion_ms2 = v_ms / tiempo_arranque_s
    n_rueda_rpm = (v_direccion_m_min * 1000.0) / (math.pi * diametro_rueda_carro_mm)
    i_req = n_motor_rpm / n_rueda_rpm if n_rueda_rpm > 0 else 1.0

    # Resistencia específica al avance en carro (kgf/t)
    w_esp_carro = 9.0  # Típico ruedas de carro con rodamientos y pestañas
    W_rodamiento_kgf = peso_total_ton * w_esp_carro

    # Resistencia de inercia
    beta_rot = 1.15
    g = 9.80665
    W_acel_kgf = (peso_total_kg * aceleracion_ms2 * beta_rot) / g

    # Número de motores de traslación del carro:
    # Monoviga suele llevar 1 motorreductor; birraíl suele llevar 1 central o 2 directos
    num_motores = 2 if es_birrail else 1

    # Potencias
    P_regimen_kw = (W_rodamiento_kgf * v_direccion_m_min) / (6120.0 * eta_mecanico * num_motores)
    P_arranque_kw = ((W_rodamiento_kgf + W_acel_kgf) * v_direccion_m_min) / (6120.0 * eta_mecanico * num_motores)

    P_adopcion = max(P_regimen_kw, P_arranque_kw / 1.7)

    escalones_iec = [0.25, 0.37, 0.55, 0.75, 1.1, 1.5, 2.2, 3.0, 4.0, 5.5]
    pot_iec_kw = escalones_iec[-1]
    for p in escalones_iec:
        if p >= P_adopcion:
            pot_iec_kw = p
            break

    torque_rueda_Nm = ((W_rodamiento_kgf + W_acel_kgf) * g / (num_motores * 2.0)) * (diametro_rueda_carro_mm / 2000.0)

    return {
        "peso_total_ton": round(peso_total_ton, 2),
        "n_rueda_rpm": round(n_rueda_rpm, 1),
        "i_req": round(i_req, 1),
        "W_rodamiento_kgf": round(W_rodamiento_kgf, 1),
        "W_acel_kgf": round(W_acel_kgf, 1),
        "P_regimen_kw": round(P_regimen_kw, 2),
        "P_arranque_kw": round(P_arranque_kw, 2),
        "pot_iec_kw": pot_iec_kw,
        "num_motores": num_motores,
        "torque_rueda_Nm": round(torque_rueda_Nm, 1)
    }