import streamlit as st
import numpy as np
import plotly.graph_objects as io
from modulo_cables import verificar_tabla_cables
from modulo_tambor import calcular_dimensiones_tambor, estimar_peso_pasteca

# Configuración de página
st.set_page_config(page_title="Calculadora Puente Grúa | UTN FRRE", layout="wide", page_icon="🏗️")

st.title("🏗️ Plataforma de Cálculo e Ingeniería de Puentes Grúa")
st.caption("UTN Facultad Regional Resistencia — Cátedra de Máquinas y Equipos de Transporte")

# =======================================================
# 1. ENTRADAS ÚNICAS EN LA BARRA LATERAL (SIDEBAR)
# =======================================================
st.sidebar.header("📐 Parametría General")

# A. Carga Útil ÚNICA
Q_util = st.sidebar.number_input("Capacidad en Gancho (Q) [kgf]", value=10000.0, step=1000.0)

# B. Geometría del Puente
L_m = st.sidebar.number_input("Luz del puente (L) [m]", value=20.0, step=1.0)
al_mm = st.sidebar.number_input("Distancia ruedas carro (al) [mm]", value=1100.0, step=100.0)

# C. Mecanismo de Elevación
st.sidebar.subheader("⚙️ Configuración Polipasto")
num_ramales = st.sidebar.selectbox("Número de Ramales", [2, 4, 6, 8], index=1)
grupo_din = st.sidebar.selectbox("Grupo DIN 4130", ['I', 'II', 'III', 'IV', 'V'], index=2)
H_elevacion = st.sidebar.number_input("Altura de Elevación [m]", value=8.0, step=1.0)

# D. Geometría Viga Cajón
st.sidebar.subheader("📐 Geometría Viga Cajón")
b = st.sidebar.number_input("Ancho viga (b) [mm]", value=500.0)
h = st.sidebar.number_input("Altura viga (h) [mm]", value=1000.0)
e_ala = st.sidebar.number_input("Espesor de ala [mm]", value=9.53)
e_alma = st.sidebar.number_input("Espesor de almas [mm]", value=9.53)

# =======================================================
# 2. CÁLCULO MECÁNICO EN CADENA (Cables, Pasteca, Tambor)
# =======================================================
# A. Pasteca
peso_pasteca = estimar_peso_pasteca(Q_util, num_ramales)

# B. Cables
S_max, F_req, tabla_cables = verificar_tabla_cables(
    Q_kg=Q_util, 
    P_ap_kg=peso_pasteca, 
    num_ramales=num_ramales, 
    grupo_mecanismo=grupo_din,
    filtro_estado='Solo Recomendados'
)

# Toma el diámetro recomendado o usa 14mm por defecto
d_cable_optimo = tabla_cables[0]["Diámetro [mm]"] if len(tabla_cables) > 0 else 14.0

# C. Tambor
res_tambor = calcular_dimensiones_tambor(
    d_cable_mm=d_cable_optimo, 
    H_elevacion_m=H_elevacion, 
    num_ramales=num_ramales, 
    tipo_polipasto='Gemelo'
)

# =======================================================
# 3. BALANCE TOTAL DE PESOS Y FEEDBACK INTEGRADO
# =======================================================
peso_carro_mecanismos = peso_pasteca + res_tambor['peso_cable_kg'] + res_tambor['peso_tambor_kg'] + 350.0 # 350kg est. motor/reductor/est
CARGA_TOTAL_SOLICITANTE = Q_util + peso_carro_mecanismos

# =======================================================
# 4. CÁLCULO ESTRUCTURAL DE LA VIGA (Con la Carga Real)
# =======================================================
# Propiedades geométricas
area_cm2 = (2 * b * e_ala + 2 * (h - 2 * e_ala) * e_alma) / 100.0
Jx = (b * h**3 - (b - 2 * e_alma) * (h - 2 * e_ala)**3) / 12.0 / 10000.0
Wx = Jx / (h / 20.0)
Pp_viga = area_cm2 * 0.785  # kgf/m

# Solicitaciones estructurales usando CARGA_TOTAL_SOLICITANTE
P_rueda = CARGA_TOTAL_SOLICITANTE / 2.0  # Carga por lado del puente
M_max_kgfcm = (P_rueda * (L_m * 100.0)) / 4.0
sigma_v = M_max_kgfcm / Wx
sigma_adm = 1400.0  # kgf/cm² (Acero F-24)
verf_v = sigma_v <= sigma_adm

# =======================================================
# 5. PRESENTACIÓN EN PANTALLA
# =======================================================

# Resumen Maestra de Carga
st.success(f"""
🎯 **BALANCE TOTAL DE CARGA SOBRE EL PUENTE GRÚA**  
* **Capacidad Nominal en Gancho ($Q$):** {Q_util:.0f} kgf  
* **Mecanismos y Carro Calculados ($P_{{carro}}$):** {peso_carro_mecanismos:.1f} kgf *(Pasteca: {peso_pasteca:.0f}kg, Cable: {res_tambor['peso_cable_kg']:.1f}kg, Tambor: {res_tambor['peso_tambor_kg']:.1f}kg)*  
* ➔ **CARGA FINAL SOLICITANTE DE VIGA ($P_{{total}}$): {CARGA_TOTAL_SOLICITANTE:.1f} kgf**
""")

# Verificación Estructural
col_res1, col_res2 = st.columns(2)
with col_res1:
    st.subheader("📊 Verificación Estructural Viga Principal")
    st.metric("Tensión Flexión Vertical (σv)", f"{sigma_v:.2f} kgf/cm²", delta="VERIFICA" if verf_v else "NO CUMPLE")
    st.write(f"- **Momento Flector Máximo:** {M_max_kgfcm/100.0:.2f} kgf·m")
    st.write(f"- **Módulo Resistente Wx:** {Wx:.2f} cm³")

with col_res2:
    st.subheader("⚙️ Módulos Mecánicos Sincronizados")
    st.write(f"- **Tracción por Ramal ($S_{{max}}$):** {S_max:.2f} kgf")
    st.write(f"- **Diámetro Cable Seleccionado:** {d_cable_optimo} mm")
    st.write(f"- **Diámetro Tambor Normalizado:** {res_tambor['D_tambor_mm']} mm")

st.markdown("---")
st.subheader("📋 Tabla Comparativa de Cables (DIN 4130)")
st.dataframe(tabla_cables, use_container_width=True)