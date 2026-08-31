import streamlit as st
import math
import plotly.graph_objects as go

st.set_page_config(
    page_title="Calculadora Viga Cajón - Puente Grúa",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏗️ Calculadora de Viga Cajón para Puente Grúa")
st.markdown("Automatización de cálculo estructural y mecánico según norma DIN 120 / DIN 4130 / DIN 655.")

# --- BARRA LATERAL: PARÁMETROS DE ENTRADA ---
st.sidebar.header("⚙️ Parámetros de Entrada")

with st.sidebar.expander("📐 Geometría de la Sección", expanded=True):
    b = st.number_input("Ancho viga (b) [mm]", value=500.0, step=10.0)
    h = st.number_input("Altura viga (h) [mm]", value=1000.0, step=10.0)
    esp_patin = st.number_input("Espesor de ala (superior/inferior) [mm]", value=9.525, step=0.1)
    esp_alma = st.number_input("Espesor de almas (verticales) [mm]", value=9.525, step=0.1)
    dl = st.number_input("Retranqueo del alma (dl) [mm]", value=50.0, step=5.0)

with st.sidebar.expander("🌉 Geometría del Puente y Cargas", expanded=True):
    Luz = st.number_input("Luz del puente (L) [m]", value=20.0, step=1.0)
    al = st.number_input("Distancia entre ruedas del carro (al) [mm]", value=1100.0, step=50.0)
    Q = st.number_input("Capacidad de carga útil (Q) [kgf]", value=18000.0, step=500.0)
    P = st.number_input("Peso estimado del carro (P) [kgf]", value=1000.0, step=100.0)
    
    # Cálculo del rango normativo de flecha (L/1200 a L/400)
    Luz_cm_temp = Luz * 100.0
    f_min_cm = Luz_cm_temp / 1200.0
    f_max_cm = Luz_cm_temp / 400.0
    
    st.info(f"💡 **Rango normativo de flecha:**\n- Mínima (L/1200): **{f_min_cm:.2f} cm**\n- Máxima (L/400): **{f_max_cm:.2f} cm**")
    
    divisor_flecha = st.selectbox(
        "Seleccione el divisor para la Flecha Admisible (L / N)",
        options=list(range(400, 1201, 100)),
        index=4  # Por defecto L/800
    )
    
    f_adm = Luz_cm_temp / divisor_flecha
    st.caption(f"Flecha Admisible seleccionada (L/{divisor_flecha}): **{f_adm:.2f} cm**")

with st.sidebar.expander("⚙️ Elevación y Polipasto", expanded=True):
    num_ramales = st.slider("Número de ramales del polipasto", min_value=2, max_value=10, value=4, step=1)
    ve_m_min = st.number_input("Velocidad de elevación [m/min]", value=8.0, step=0.5)
    he = st.number_input("Altura de elevación [m]", value=8.0, step=1.0)
    phi = st.number_input("Coeficiente de choque (ϕ)", value=1.1, step=0.05)
    psi = st.number_input("Coeficiente de mayoración (ψ)", value=1.6, step=0.05)
    sigma_adm_v = st.number_input("σ admisible vertical [kgf/cm²]", value=1400.0)
    sigma_adm_hv = st.number_input("σ admisible combinada [kgf/cm²]", value=1600.0)
    E = st.number_input("Módulo elástico E [kgf/cm²]", value=2100000.0)

# --- CÁLCULOS ESTRUCTURALES Y MECÁNICOS ---
b_cm, h_cm = b/10, h/10
esp_p_cm, esp_a_cm = esp_patin/10, esp_alma/10
dl_cm = dl/10
Luz_cm, al_cm = Luz * 100.0, al / 10.0

# 1. Propiedades geométricas
Jx = 2 * ((esp_a_cm * (h_cm**3))/12 + (b_cm * (esp_p_cm**3))/12 + b_cm * esp_p_cm * ((h_cm + esp_p_cm)/2)**2)
Wx = Jx / (h_cm/2 + esp_p_cm)

Jy = 2 * ((esp_p_cm * (b_cm**3))/12 + (h_cm * (esp_a_cm**3))/12 + ((b_cm/2 - dl_cm - esp_a_cm/2)**2) * h_cm * esp_a_cm)
Wy = Jy / (b_cm/2)

# 2. Cargas verticales y solicitaciones
Pr = (Q + P) / 4.0  # Carga por rueda (doble viga)
Mpmax = Pr * ((Luz_cm - al_cm/2)**2) / (2 * Luz_cm)

rho_acero = 7860.0  # kgf/m³
Pp = (2 * (b/1000) * (esp_patin/1000) + 2 * (h/1000) * (esp_alma/1000)) * rho_acero  # kgf/m
ge = Pp + 40.0  # +40 kgf/m por pasarela

Mg1 = (ge * (Luz**2) / 8.0) * 100.0
g2 = 700.0  # Accionamiento traslación [kgf]
Mg2 = (g2 * Luz / 4.0) * 100.0
Mg3 = 0.0

sigma_v = (phi * (Mg1 + Mg2 + Mg3) + psi * Mpmax) / Wx

# 3. Solicitaciones horizontales (DIN 120)
Fih = Pr / 14.0
Mpmax_H = (Fih * ((Luz_cm - al_cm/2)**2)) / (2 * Luz_cm)
Mg1_H = Mg1 / 14.0
Mg2_H = Mg2 / 14.0

sigma_Hv = sigma_v + (Mpmax_H + Mg1_H + Mg2_H) / Wy

# 4. Deformación (Flecha)
f_real = (Pr * (Luz_cm - al_cm) * (Luz_cm**2 + (Luz_cm + al_cm)**2)) / (48 * E * Jx)

# 5. Mecanismo de elevación
S = Q / num_ramales
d_cable_calc = 0.34 * math.sqrt(S)
d_cable_adoptado = 22.0

Dt_min = 7 * math.sqrt(S)
Dt_adoptado = 500.0

Dp_min = 8 * math.sqrt(S)
Dp_adoptado = 600.0

Dpc_min = 5 * math.sqrt(S)
Dpc_adoptado = 380.0

ve_m_s = ve_m_min / 60.0
n_espiras = (2 * he) / (math.pi * (Dt_adoptado/1000.0)) + 3
e_esp = d_cable_adoptado + 3.0
Lt_calc = (2 if num_ramales >= 4 else 1) * n_espiras * e_esp + 250.0

Pot_teorica_kW = (Q * ve_m_s) / 102.0
v_cable = (num_ramales / 2.0) * ve_m_min
n_tambor = v_cable / (math.pi * (Dt_adoptado/1000.0))
nm = 1470.0
i_total = nm / n_tambor

# --- INTERFAZ DE RESULTADOS ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📊 Verificaciones Estructurales")
    
    # --- CARD TENSIÓN VERTICAL ---
    verf_v = sigma_v <= sigma_adm_v
    color_bg_v = "#e6f4ea" if verf_v else "#fce8e6"
    color_border_v = "#1e8e3e" if verf_v else "#d93025"
    texto_estado_v = "✅ VERIFICA" if verf_v else "❌ NO VERIFICA"
    
    st.markdown(f"""
    <div style="background-color: {color_bg_v}; border: 2px solid {color_border_v}; border-radius: 8px; padding: 15px; margin-bottom: 15px;">
        <span style="font-size: 14px; color: #5f6368; font-weight: bold;">Tensión Flexión Vertical (σv)</span>
        <div style="font-size: 28px; font-weight: bold; color: {color_border_v}; margin: 5px 0;">{sigma_v:.2f} kgf/cm²</div>
        <div style="font-size: 12px; color: #3c4043;">Admisible: {sigma_adm_v:.2f} kgf/cm² | Margen: {sigma_adm_v - sigma_v:.2f} kgf/cm²</div>
        <div style="font-size: 16px; font-weight: bold; color: {color_border_v}; margin-top: 8px;">{texto_estado_v}</div>
    </div>
    """, unsafe_allow_html=True)

    # --- CARD TENSIÓN COMBINADA ---
    verf_hv = sigma_Hv <= sigma_adm_hv
    color_bg_hv = "#e6f4ea" if verf_hv else "#fce8e6"
    color_border_hv = "#1e8e3e" if verf_hv else "#d93025"
    texto_estado_hv = "✅ VERIFICA" if verf_hv else "❌ NO VERIFICA"

    st.markdown(f"""
    <div style="background-color: {color_bg_hv}; border: 2px solid {color_border_hv}; border-radius: 8px; padding: 15px; margin-bottom: 15px;">
        <span style="font-size: 14px; color: #5f6368; font-weight: bold;">Tensión Combinada Vertical + Horizontal (σHv)</span>
        <div style="font-size: 28px; font-weight: bold; color: {color_border_hv}; margin: 5px 0;">{sigma_Hv:.2f} kgf/cm²</div>
        <div style="font-size: 12px; color: #3c4043;">Admisible: {sigma_adm_hv:.2f} kgf/cm² | Margen: {sigma_adm_hv - sigma_Hv:.2f} kgf/cm²</div>
        <div style="font-size: 16px; font-weight: bold; color: {color_border_hv}; margin-top: 8px;">{texto_estado_hv}</div>
    </div>
    """, unsafe_allow_html=True)

    # --- CARD FLECHA ---
    verf_f = f_real <= f_adm
    color_bg_f = "#e6f4ea" if verf_f else "#fce8e6"
    color_border_f = "#1e8e3e" if verf_f else "#d93025"
    texto_estado_f = "✅ VERIFICA" if verf_f else "❌ NO VERIFICA"

    st.markdown(f"""
    <div style="background-color: {color_bg_f}; border: 2px solid {color_border_f}; border-radius: 8px; padding: 15px; margin-bottom: 15px;">
        <span style="font-size: 14px; color: #5f6368; font-weight: bold;">Flecha Máxima Calculada (f)</span>
        <div style="font-size: 28px; font-weight: bold; color: {color_border_f}; margin: 5px 0;">{f_real:.3f} cm</div>
        <div style="font-size: 12px; color: #3c4043;">Admisible (L/{divisor_flecha}): {f_adm:.2f} cm</div>
        <div style="font-size: 16px; font-weight: bold; color: {color_border_f}; margin-top: 8px;">{texto_estado_f}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Propiedades Geométricas Calculadas:**")
    st.write(f"- **Jx:** {Jx:.2f} cm⁴ | **Wx:** {Wx:.2f} cm³")
    st.write(f"- **Jy:** {Jy:.2f} cm⁴ | **Wy:** {Wy:.2f} cm³")
    st.write(f"- **Peso propio viga:** {Pp:.2f} kgf/m")

with col2:
    st.subheader("📐 Vista Esquematizada de la Sección Cajón")
    
    fig = go.Figure()

    # Patín Superior (Ala superior)
    fig.add_shape(type="rect", x0=-b/2, y0=h/2, x1=b/2, y1=h/2 + esp_patin, fillcolor="SteelBlue", line=dict(color="Black"))
    # Patín Inferior (Ala inferior)
    fig.add_shape(type="rect", x0=-b/2, y0=-h/2 - esp_patin, x1=b/2, y1=-h/2, fillcolor="SteelBlue", line=dict(color="Black"))
    # Alma Izquierda
    fig.add_shape(type="rect", x0=-b/2 + dl, y0=-h/2, x1=-b/2 + dl + esp_alma, y1=h/2, fillcolor="LightSteelBlue", line=dict(color="Black"))
    # Alma Derecha
    fig.add_shape(type="rect", x0=b/2 - dl - esp_alma, y0=-h/2, x1=b/2 - dl, y1=h/2, fillcolor="LightSteelBlue", line=dict(color="Black"))

    fig.update_layout(
        xaxis=dict(range=[-b*0.7, b*0.7], title="x [mm]"),
        yaxis=dict(range=[-h*0.7, h*0.7], title="y [mm]"),
        width=400,
        height=400,
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- SECCIÓN MECÁNICA DE ELEVACIÓN ---
st.subheader("⚙️ Dimensionamiento del Mecanismo de Elevación")

m_col1, m_col2, m_col3 = st.columns(3)

with m_col1:
    st.markdown("**Cable y Tambor**")
    st.write(f"- **Ramales seleccionados:** {num_ramales}")
    st.write(f"- **Tiro por ramal (S):** {S:.2f} kgf")
    st.write(f"- **Diámetro cable mín. calc.:** {d_cable_calc:.2f} mm")
    st.write(f"- **Diámetro cable adoptado:** {d_cable_adoptado:.0f} mm")

with m_col2:
    st.markdown("**Poleas**")
    st.write(f"- **Polea de reenvío mín. calc.:** {Dp_min:.2f} mm")
    st.write(f"- **Polea de reenvío adoptada:** {Dp_adoptado:.0f} mm")
    st.write(f"- **Polea compensadora mín. calc.:** {Dpc_min:.2f} mm")
    st.write(f"- **Polea compensadora adoptada:** {Dpc_adoptado:.0f} mm")

with m_col3:
    st.markdown("**Potencia y Reducción**")
    st.write(f"- **Potencia teórica requerida:** {Pot_teorica_kW:.2f} kW")
    st.write(f"- **RPM del tambor:** {n_tambor:.2f} rpm")
    st.write(f"- **Relación de transmisión total (i):** {i_total:.2f}")
    st.write(f"- **Longitud total tambor calc.:** {Lt_calc:.2f} mm")