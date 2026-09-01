import math

def calcular_motor_reductor(carga_total_kg, v_elev_m_min, D_tambor_mm, num_ramales=4, 
                            eta_poleas=0.97, eta_tambor=0.98, eta_reductor=0.93):
    """
    Calcula la potencia del motor trifásico considerando la cadena cinemática 
    de rendimientos (Poleas, Tambor y Reductor) según DIN 15020.
    """
    # 1. Rendimiento Global Acumulado
    eta_global = eta_poleas * eta_tambor * eta_reductor
    
    # 2. Potencia útil requerida en kW
    fuerza_N = carga_total_kg * 9.80665
    v_elev_m_s = v_elev_m_min / 60.0
    potencia_kw_util = (fuerza_N * v_elev_m_s) / 1000.0
    
    # Potencia necesaria en el eje del motor considerando pérdidas
    potencia_kw_teorica = potencia_kw_util / eta_global if eta_global > 0 else potencia_kw_util
    
    # Normalización a potencias comerciales de motores trifásicos IEC (kW)
    potencias_std = [3.0, 4.0, 5.5, 7.5, 11.0, 15.0, 18.5, 22.0, 30.0, 37.0, 45.0, 55.0, 75.0, 90.0]
    potencia_motor_kw = min([p for p in potencias_std if p >= potencia_kw_teorica], default=potencia_kw_teorica)
    
    # 3. RPM del tambor y relación de reducción (Motor 4 polos @ 50 Hz -> ~1450 rpm)
    D_tambor_m = D_tambor_mm / 1000.0
    ramales_por_salida = num_ramales / 2.0
    n_tambor_rpm = (v_elev_m_min * ramales_por_salida) / (math.pi * D_tambor_m) if D_tambor_m > 0 else 1.0
    
    n_motor_rpm = 1450.0
    i_reductor = n_motor_rpm / n_tambor_rpm if n_tambor_rpm > 0 else 1.0
    
    # 4. Torque en el eje de baja del reductor (eje del tambor)
    torque_tambor_Nm = (potencia_motor_kw * 1000.0 * 9.55) / n_tambor_rpm if n_tambor_rpm > 0 else 0.0
    
    return {
        "eta_global": round(eta_global * 100.0, 1),
        "potencia_util_kw": round(potencia_kw_util, 2),
        "potencia_teorica_kw": round(potencia_kw_teorica, 2),
        "potencia_motor_kw": potencia_motor_kw,
        "n_tambor_rpm": round(n_tambor_rpm, 2),
        "i_reductor": round(i_reductor, 2),
        "torque_tambor_Nm": round(torque_tambor_Nm, 1)
    }