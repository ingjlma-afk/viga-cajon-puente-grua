import streamlit as st
import math
import plotly.graph_objects as go
import ezdxf

st.set_page_config(
    page_title="Calculadora Viga - Puente Grúa (DXF)",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏗️ Calculadora de Viga para Puente Grúa")
st.markdown("Cálculo estructural y mecánico (DIN 120 / DIN 4130 / DIN 655) con soporte para geometría arbitraria vía DXF.")

# --- SELECCIÓN DE MODO DE GEOMETRÍA ---
st.sidebar.header("📐 Modo de Geometría")
modo_geometria = st.sidebar.radio(
    "Seleccione el origen de la sección transversal:",
    ["Paramétrica (Viga Cajón estándar)", "Importar desde Archivo DXF"]
)

# Variables geométricas por defecto
Jx, Jy, Wx, Wy, Pp = 0.0, 0.0, 0.0, 0.0, 0.0
b_vis, h_vis = 500.0, 1000.0
fig = go.Figure()

# --- FUNCIONES DE LECTURA Y CÁLCULO DXF ---
def procesar_dxf(file_bytes):
    """
    Lee las polilíneas cerradas (LWPOLYLINE / POLYLINE) del DXF (en mm)
    y calcula A, Cx, Cy, Jx, Jy, Wx, Wy.
    """
    doc = ezdxf.read(file_bytes)
    msp = doc.modelspace()
    
    elementos = []
    
    # Recorrer polilíneas cerradas (que representan chapas de la viga)
    for entity in msp:
        if entity.dxftype() in ('LWPOLYLINE', 'POLYLINE'):
            points = [(p[0], p[1]) for p in entity.get_points()]
            if len(points) >= 3:
                # Calcular área y centroide de la chapa individual (Fórmula del Agrimensor)
                n = len(points)
                A_i = 0.0
                cx_i = 0.0
                cy_i = 0.0
                for i in range(n):
                    x0, y0 = points[i]
                    x1, y1 = points[(i + 1) % n]
                    cross = (x0 * y1 - x1 * y0)
                    A_i += cross
                    cx_i += (x0 + x1) * cross
                    cy_i += (y0 + y1) * cross
                
                A_i = abs(A_i) / 2.0
                if A_i > 0:
                    cx_i = cx_i / (6.0 * (A_i if cross >= 0 else -A_i))
                    cy_i = cy_i / (6.0 * (A_i if cross >= 0 else -A_i))
                    
                    # Inercias propias aproximadas respecto a su centroide
                    xs = [p[0] for p in points]
                    ys = [p[1] for p in points]
                    b_e = max(xs) - min(xs)
                    h_e = max(ys) - min(ys)
                    I_xo = (b_e * h_e**3) / 12.0
                    I_yo = (h_e * b_e**3) / 12.0
                    
                    elementos.append({
                        'A': A_i, 'cx': cx_i, 'cy': cy_i,
                        'Ixo': I_xo, 'Iyo': I_yo,
                        'pts': points
                    })

    if not elementos:
        return None

    # Baricentro Global de la Sección Compuesta (mm)
    A_total = sum(e['A'] for e in elementos)
    Cx_g = sum(e['A'] * e['cx'] for e in elementos) / A_total
    Cy_g = sum(e['A'] * e['cy'] for e in elementos) / A_total

    # Inercias Baricéntricas Globales con Steiner (convertidas a cm4)
    # 1 cm4 = 10,000 mm4
    Jx_mm4 = 0.0
    Jy_mm4 = 0.0
    
    for e in elementos:
        dy = e['cy'] - Cy_g
        dx = e['cx'] - Cx_g
        Jx_mm4 += e['Ixo'] + e['A'] * (dy**2)
        Jy_mm4 += e['Iyo'] + e['A'] * (dx**2)

    Jx_cm4 = Jx_mm4 / 10000.0
    Jy_cm4 = Jy_mm4 / 10000.0

    # Distancias a las fibras más alejadas (mm a cm)
    all_pts_x = [p[0] for e in elementos for p in e['pts']]
    all_pts_y = [p[1] for e in elementos for p in e['pts']]
    
    ymax_cm = (max(all_pts_y) - Cy_g) / 10.0
    xmax_cm = (max(all_pts_x) - Cx_g) / 10.0
    
    Wx_cm3 = Jx_cm4 / ymax_cm if ymax_cm > 0 else Jx_cm4
    Wy_cm3 = Jy_cm4 / xmax_cm if xmax_cm > 0 else Jy_cm4
    
    # Peso propio en kgf/m (A_total en mm2 -> m2)
    Pp_calc = (A_total / 1000000.0) * 7860.0

    return {
        'Jx': Jx_cm4, 'Jy': Jy_cm4, 'Wx': Wx_cm3, 'Wy': Wy_cm3,
        'Pp': Pp_calc, 'elementos': elementos, 'Cx': Cx_g, 'Cy': Cy_g
    }

# --- ENTRADA DE DATOS SEGÚN MODO ---
if modo_geometria == "Paramétrica (Viga Cajón estándar)":
    with st.sidebar.expander("📐 Geometría Cajón", expanded=True):
        b = st.number_input("Ancho viga (b) [mm]", value=500.0, step=10.0)
        h = st.number_input("Altura viga (h) [mm]", value=1000.0, step=10.0)
        esp_patin = st.number_input("Espesor de ala [mm]", value=9.525, step=0.1)
        esp_alma = st.number_input("Espesor de almas [mm]", value=9.525, step=0.1)
        dl = st.number_input("Retranqueo del alma (dl) [mm]", value=50.0, step=5.0)

    # Cálculos analíticos cajón
    b_cm, h_cm = b/10, h/10
    esp_p_cm, esp_a_cm = esp_patin/10, esp_alma/10
    dl_cm = dl/10
    
    Jx = 2 * ((esp_a_cm * (h_cm**3))/12 + (b_cm * (esp_p_cm**3))/12 + b_cm * esp_p_cm * ((h_cm + esp_p_cm)/2)**2)
    Wx = Jx / (h_cm/2 + esp_p_cm)
    Jy = 2 * ((esp_p_cm * (b_cm**3))/12 + (h_cm * (esp_a_cm**3))/12 + ((b_cm/2 - dl_cm - esp_a_cm/2)**2) * h_cm * esp_a_cm)
    Wy = Jy / (b_cm/2)
    Pp = (2 * (b/1000) * (esp_patin/1000) + 2 * (h/1000) * (esp_alma/1000)) * 7860.0

    # Dibujo Plotly
    fig.add_shape(type="rect", x0=-b/2, y0=h/2, x1=b/2, y1=h/2 + esp_patin, fillcolor="SteelBlue", line=dict(color="Black"))
    fig.add_shape(type="rect", x0=-b/2, y0=-h/2 - esp_patin, x1=b/2, y1=-h/2, fillcolor="SteelBlue", line=dict(color="Black"))
    fig.add_shape(type="rect", x0=-b/2 + dl, y0=-h/2, x1=-b/2 + dl + esp_alma, y1=h/2, fillcolor="LightSteelBlue", line=dict(color="Black"))
    fig.add_shape(type="rect", x0=b/2 - dl - esp_alma, y0=-h/2, x1=b/2 - dl, y1=h/2, fillcolor="LightSteelBlue", line=dict(color="Black"))
    fig.update_layout(xaxis=dict(range=[-b*0.7, b*0.7]), yaxis=dict(range=[-h*0.7, h*0.7]))

else:
    st.sidebar.subheader("📁 Cargar Archivo DXF")
    uploaded_dxf = st.sidebar.file_uploader("Seleccione el archivo .dxf dibujado en mm", type=["dxf"])
    
    if uploaded_dxf is not None:
        try:
            res = procesar_dxf(uploaded_dxf)
            if res:
                Jx, Jy, Wx, Wy, Pp = res['Jx'], res['Jy'], res['Wx'], res['Wy'], res['Pp']
                st.sidebar.success("✅ DXF procesado correctamente")
                
                # Renderizar geometría DXF en Plotly
                for elem in res['elementos']:
                    pts = elem['pts']
                    xs = [p[0] - res['Cx'] for p in pts] + [pts[0][0] - res['Cx']]
                    ys = [p[1] - res['Cy'] for p in pts] + [pts[0][1] - res['Cy']]
                    fig.add_trace(go.Scatter(x=xs, y=ys, fill="toself", mode="lines", name="Chapa"))
                fig.update_layout(showlegend=False)
            else:
                st.sidebar.error("No se encontraron polilíneas cerradas en el DXF.")
        except Exception as e:
            st.sidebar.error(f"Error al leer DXF: {e}")
    else:
        st.info("👈 Por favor cargue un archivo DXF desde la barra lateral para realizar los cálculos.")

# --- RESTO DE PARÁMETROS Y CÁLCULOS ESTÁNDAR ---
with st.sidebar.expander("🌉 Geometría del Puente y Cargas", expanded=True):
    Luz = st.number_input("Luz del puente (L) [m]", value=20.0, step=1.0)
    al = st.number_input("Distancia entre ruedas del carro (al) [mm]", value=1100.0, step=50.0)
    Q = st.number_input("Capacidad de carga útil (Q) [kgf]", value=18000.0, step=500.0)
    P = st.number_input("Peso estimado del carro (P) [kgf]", value=1000.0, step=100.0)
    
    Luz_cm_temp = Luz * 100.0
    divisor_flecha = st.selectbox("Divisor para Flecha Admisible (L / N)", options=list(range(400, 1201, 100)), index=4)
    f_adm = Luz_cm_temp / divisor_flecha

with st.sidebar.expander("⚙️ Elevación y Polipasto", expanded=True):
    num_ramales = st.slider("Número de ramales del polipasto", min_value=2, max_value=10, value=4, step=1)
    ve_m_min = st.number_input("Velocidad de elevación [m/min]", value=8.0, step=0.5)
    he = st.number_input("Altura de elevación [m]", value=8.0, step=1.0)
    phi = st.number_input("Coeficiente de choque (ϕ)", value=1.1, step=0.05)
    psi = st.number_input("Coeficiente de mayoración (ψ)", value=1.6, step=0.05)
    sigma_adm_v = st.number_input("σ admisible vertical [kgf/cm²]", value=1400.0)
    sigma_adm_hv = st.number_input("σ admisible combinada [kgf/cm²]", value=1600.0)
    E = st.number_input("Módulo elástico E [kgf/cm²]", value=2100000.0)

# Cargas y Verificaciones
Luz_cm, al_cm = Luz * 100.0, al / 10.0
Pr = (Q + P) / 4.0
Mpmax = Pr * ((Luz_cm - al_cm/2)**2) / (2 * Luz_cm)
ge = Pp + 40.0
Mg1 = (ge * (Luz**2) / 8.0) * 100.0
g2 = 700.0
Mg2 = (g2 * Luz / 4.0) * 100.0

sigma_v = (phi * (Mg1 + Mg2) + psi * Mpmax) / Wx if Wx > 0 else 0.0

Fih = Pr / 14.0
Mpmax_H = (Fih * ((Luz_cm - al_cm/2)**2)) / (2 * Luz_cm)
Mg1_H = Mg1 / 14.0
Mg2_H = Mg2 / 14.0

sigma_Hv = sigma_v + (Mpmax_H + Mg1_H + Mg2_H) / Wy if Wy > 0 else 0.0
f_real = (Pr * (Luz_cm - al_cm) * (Luz_cm**2 + (Luz_cm + al_cm)**2)) / (48 * E * Jx) if Jx > 0 else 0.0

# --- INTERFAZ DE RESULTADOS ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📊 Verificaciones Estructurales")
    
    # Card σv
    verf_v = sigma_v <= sigma_adm_v if sigma_v > 0 else False
    color_border_v = "#1e8e3e" if verf_v else "#d93025"
    st.markdown(f"""
    <div style="background-color: {'#e6f4ea' if verf_v else '#fce8e6'}; border: 2px solid {color_border_v}; border-radius: 8px; padding: 15px; margin-bottom: 10px;">
        <span style="font-size: 14px; font-weight: bold;">Tensión Flexión Vertical (σv)</span>
        <div style="font-size: 26px; font-weight: bold; color: {color_border_v};">{sigma_v:.2f} kgf/cm²</div>
        <div style="font-size: 14px; font-weight: bold; color: {color_border_v};">{'✅ VERIFICA' if verf_v else '❌ NO VERIFICA'}</div>
    </div>
    """, unsafe_allow_html=True)

    # Card σHv
    verf_hv = sigma_Hv <= sigma_adm_hv if sigma_Hv > 0 else False
    color_border_hv = "#1e8e3e" if verf_hv else "#d93025"
    st.markdown(f"""
    <div style="background-color: {'#e6f4ea' if verf_hv else '#fce8e6'}; border: 2px solid {color_border_hv}; border-radius: 8px; padding: 15px; margin-bottom: 10px;">
        <span style="font-size: 14px; font-weight: bold;">Tensión Combinada V+H (σHv)</span>
        <div style="font-size: 26px; font-weight: bold; color: {color_border_hv};">{sigma_Hv:.2f} kgf/cm²</div>
        <div style="font-size: 14px; font-weight: bold; color: {color_border_hv};">{'✅ VERIFICA' if verf_hv else '❌ NO VERIFICA'}</div>
    </div>
    """, unsafe_allow_html=True)

    # Propiedades
    st.markdown("**Propiedades Geométricas Calculadas:**")
    st.write(f"- **Jx:** {Jx:.2f} cm⁴ | **Wx:** {Wx:.2f} cm³")
    st.write(f"- **Jy:** {Jy:.2f} cm⁴ | **Wy:** {Wy:.2f} cm³")
    st.write(f"- **Peso propio viga:** {Pp:.2f} kgf/m")

with col2:
    st.subheader("📐 Geometría Transversal")
    st.plotly_chart(fig, use_container_width=True)
