import streamlit as st
import math
import io
import plotly.graph_objects as go
import ezdxf

# Importación de módulos propios
from modulo_cables import verificar_tabla_cables
from modulo_tambor import calcular_dimensiones_tambor, estimar_peso_pasteca

# Configuración de página con título e icono
st.set_page_config(
    page_title="Calculadora Viga - Puente Grúa | UTN FRRE",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inyección de CSS para personalizar el diseño
st.markdown("""
    <style>
    .stApp {
        background-color: #f8fafc;
    }
    .header-utn {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    div[data-testid="stMetricValue"] {
        font-size: 22px;
        color: #1e3a8a;
        font-weight: bold;
    }
    .footer-utn {
        text-align: center;
        padding: 15px;
        margin-top: 50px;
        border-top: 1px solid #e2e8f0;
        color: #64748b;
        font-size: 13px;
    }
    </style>
""", unsafe_allow_html=True)

# Encabezado visual en pantalla
st.markdown("""
    <div class="header-utn">
        <h1 style="margin:0; font-size: 28px;">🏗️ Plataforma de Cálculo e Ingeniería de Puentes Grúa</h1>
        <p style="margin:5px 0 0 0; opacity: 0.9;">
            Desarrollado por Electromecánicos — <strong>UTN Facultad Regional Resistencia</strong>
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown("Cálculo estructural y mecánico (DIN 120 / DIN 4130 / DIN 655) con soporte para geometría arbitraria vía DXF.")

# --- SELECCIÓN DE MODO DE GEOMETRÍA ---
st.sidebar.header("📐 Modo de Geometría")
modo_geometria = st.sidebar.radio(
    "Seleccione el origen de la sección transversal:",
    ["Paramétrica (Viga Cajón estándar)", "Importar desde Archivo DXF"]
)

# Variables geométricas
Jx, Jy, Wx, Wy, Pp = 0.0, 0.0, 0.0, 0.0, 0.0
fig = go.Figure()

import tempfile
import os

# --- CÁLCULO DE PROPIEDADES GEOMÉTRICAS DXF (SOPORTE TOTAL BINARIO / SOLIDWORKS) ---
def procesar_dxf(uploaded_file):
    # Guardamos temporalmente el archivo subido para que ezdxf lo procese de forma nativa
    with tempfile.NamedTemporaryFile(delete=False, suffix=".dxf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name

    try:
        # Intento 1: Lectura nativa directa desde archivo (detecta ASCII o Binario de SolidWorks)
        doc = ezdxf.readfile(tmp_path)
    except Exception:
        try:
            # Intento 2: Recuperación de archivos complejos o corruptos
            from ezdxf import recover
            doc, _ = recover.readfile(tmp_path)
        except Exception as e:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise e
    finally:
        # Limpieza del archivo temporal
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    msp = doc.modelspace()
    poligonos = []
    
    # Extraer polilíneas cerradas del DXF
    for entity in msp:
        if entity.dxftype() in ('LWPOLYLINE', 'POLYLINE'):
            points = [(p[0], p[1]) for p in entity.get_points()]
            if len(points) >= 3:
                n = len(points)
                A_i, cx_i, cy_i = 0.0, 0.0, 0.0
                for i in range(n):
                    x0, y0 = points[i]
                    x1, y1 = points[(i + 1) % n]
                    cross = (x0 * y1 - x1 * y0)
                    A_i += cross
                    cx_i += (x0 + x1) * cross
                    cy_i += (y0 + y1) * cross
                
                A_calc = A_i / 2.0
                A_abs = abs(A_calc)
                
                if A_abs > 0:
                    cross_tot = sum((points[i][0]*points[(i+1)%n][1] - points[(i+1)%n][0]*points[i][1]) for i in range(n))
                    div = (3.0 * cross_tot) if cross_tot != 0 else 1.0
                    cx_i = cx_i / div
                    cy_i = cy_i / div
                    
                    Ixo, Iyo = 0.0, 0.0
                    for i in range(n):
                        x0, y0 = points[i][0] - cx_i, points[i][1] - cy_i
                        x1, y1 = points[(i + 1) % n][0] - cx_i, points[(i + 1) % n][1] - cy_i
                        cross = (x0 * y1 - x1 * y0)
                        Ixo += (y0**2 + y0*y1 + y1**2) * cross
                        Iyo += (x0**2 + x0*x1 + x1**2) * cross
                    
                    Ixo = abs(Ixo) / 12.0
                    Iyo = abs(Iyo) / 12.0
                    
                    poligonos.append({
                        'A': A_abs, 'cx': cx_i, 'cy': cy_i,
                        'Ixo': Ixo, 'Iyo': Iyo, 'pts': points
                    })

    if not poligonos:
        return None

    poligonos.sort(key=lambda p: p['A'], reverse=True)

    if len(poligonos) >= 2:
        A_neto = poligonos[0]['A'] - sum(p['A'] for p in poligonos[1:])
        Cx_g = (poligonos[0]['A']*poligonos[0]['cx'] - sum(p['A']*p['cx'] for p in poligonos[1:])) / A_neto
        Cy_g = (poligonos[0]['A']*poligonos[0]['cy'] - sum(p['A']*p['cy'] for p in poligonos[1:])) / A_neto
        
        Jx_mm4 = (poligonos[0]['Ixo'] + poligonos[0]['A'] * ((poligonos[0]['cy'] - Cy_g)**2)) - \
                 sum(p['Ixo'] + p['A'] * ((p['cy'] - Cy_g)**2) for p in poligonos[1:])
                 
        Jy_mm4 = (poligonos[0]['Iyo'] + poligonos[0]['A'] * ((poligonos[0]['cx'] - Cx_g)**2)) - \
                 sum(p['Iyo'] + p['A'] * ((p['cx'] - Cx_g)**2) for p in poligonos[1:])
    else:
        A_neto = poligonos[0]['A']
        Cx_g = poligonos[0]['cx']
        Cy_g = poligonos[0]['cy']
        Jx_mm4 = poligonos[0]['Ixo']
        Jy_mm4 = poligonos[0]['Iyo']

    Jx_cm4 = abs(Jx_mm4) / 10000.0
    Jy_cm4 = abs(Jy_mm4) / 10000.0

    all_pts_x = [p[0] for poly in poligonos for p in poly['pts']]
    all_pts_y = [p[1] for poly in poligonos for p in poly['pts']]
    
    ymax_cm = max(abs(max(all_pts_y) - Cy_g), abs(min(all_pts_y) - Cy_g)) / 10.0
    xmax_cm = max(abs(max(all_pts_x) - Cx_g), abs(min(all_pts_x) - Cx_g)) / 10.0
    
    Wx_cm3 = Jx_cm4 / ymax_cm if ymax_cm > 0 else Jx_cm4
    Wy_cm3 = Jy_cm4 / xmax_cm if xmax_cm > 0 else Jy_cm4
    
    Pp_calc = (A_neto / 1000000.0) * 7860.0

    return {
        'Jx': Jx_cm4, 'Jy': Jy_cm4, 'Wx': Wx_cm3, 'Wy': Wy_cm3,
        'Pp': Pp_calc, 'poligonos': poligonos, 'Cx': Cx_g, 'Cy': Cy_g
    }
# --- PARÁMETROS DE CARGA ÚNICA Y PARÁMETROS GENERALES ---
with st.sidebar.expander("🌉 Geometría del Puente y Cargas", expanded=True):
    Luz = st.number_input("Luz del puente (L) [m]", value=20.0, step=1.0)
    al = st.number_input("Distancia entre ruedas del carro (al) [mm]", value=1100.0, step=50.0)
    Q = st.number_input("Capacidad de carga útil en Gancho (Q) [kgf]", value=18000.0, step=500.0)
    
    Luz_cm_temp = Luz * 100.0
    divisor_flecha = st.selectbox("Divisor para Flecha Admisible (L / N)", options=list(range(400, 1201, 100)), index=4)
    f_adm = Luz_cm_temp / divisor_flecha

with st.sidebar.expander("⚙️ Elevación y Polipasto", expanded=True):
    num_ramales = st.slider("Número de ramales del polipasto", min_value=2, max_value=10, value=4, step=1)
    grupo_din = st.selectbox("Grupo DIN 4130", ['I', 'II', 'III', 'IV', 'V'], index=2)
    ve_m_min = st.number_input("Velocidad de elevación [m/min]", value=8.0, step=0.5)
    he = st.number_input("Altura de elevación [m]", value=8.0, step=1.0)
    phi = st.number_input("Coeficiente de choque (ϕ)", value=1.1, step=0.05)
    psi = st.number_input("Coeficiente de mayoración (ψ)", value=1.6, step=0.05)
    sigma_adm_v = st.number_input("σ admisible vertical [kgf/cm²]", value=1400.0)
    sigma_adm_hv = st.number_input("σ admisible combinada [kgf/cm²]", value=1600.0)
    E = st.number_input("Módulo elástico E [kgf/cm²]", value=2100000.0)

# =======================================================
# CÁLCULOS MECÁNICOS AUTOMÁTICOS (Pasteca, Cables, Tambor)
# =======================================================
peso_pasteca = estimar_peso_pasteca(Q, num_ramales)

S_max, F_req, tabla_cables = verificar_tabla_cables(
    Q_kg=Q, 
    P_ap_kg=peso_pasteca, 
    num_ramales=num_ramales, 
    grupo_mecanismo=grupo_din,
    filtro_estado='Solo Recomendados'
)

d_cable_sel = tabla_cables[0]["Diámetro [mm]"] if len(tabla_cables) > 0 else 14.0

res_tambor = calcular_dimensiones_tambor(
    d_cable_mm=d_cable_sel, 
    H_elevacion_m=he, 
    num_ramales=num_ramales, 
    tipo_polipasto='Gemelo'
)

peso_mecanismos_est = 350.0
P_carro_real = peso_pasteca + res_tambor['peso_cable_kg'] + res_tambor['peso_tambor_kg'] + peso_mecanismos_est
CARGA_TOTAL_ACTUANTE = Q + P_carro_real

# =======================================================
# CÁLCULO ESTRUCTURAL DE LA VIGA CON CARGA TOTAL
# =======================================================
Luz_cm, al_cm = Luz * 100.0, al / 10.0
Pr = CARGA_TOTAL_ACTUANTE / 4.0
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
    
    verf_v = sigma_v <= sigma_adm_v if sigma_v > 0 else False
    color_border_v = "#1e8e3e" if verf_v else "#d93025"
    st.markdown(f"""
    <div style="background-color: {'#e6f4ea' if verf_v else '#fce8e6'}; border: 2px solid {color_border_v}; border-radius: 8px; padding: 15px; margin-bottom: 10px;">
        <span style="font-size: 14px; font-weight: bold;">Tensión Flexión Vertical (σv)</span>
        <div style="font-size: 26px; font-weight: bold; color: {color_border_v};">{sigma_v:.2f} kgf/cm²</div>
        <div style="font-size: 14px; font-weight: bold; color: {color_border_v};">{'✅ VERIFICA' if verf_v else '❌ NO VERIFICA'}</div>
    </div>
    """, unsafe_allow_html=True)

    verf_hv = sigma_Hv <= sigma_adm_hv if sigma_Hv > 0 else False
    color_border_hv = "#1e8e3e" if verf_hv else "#d93025"
    st.markdown(f"""
    <div style="background-color: {'#e6f4ea' if verf_hv else '#fce8e6'}; border: 2px solid {color_border_hv}; border-radius: 8px; padding: 15px; margin-bottom: 10px;">
        <span style="font-size: 14px; font-weight: bold;">Tensión Combinada V+H (σHv)</span>
        <div style="font-size: 26px; font-weight: bold; color: {color_border_hv};">{sigma_Hv:.2f} kgf/cm²</div>
        <div style="font-size: 14px; font-weight: bold; color: {color_border_hv};">{'✅ VERIFICA' if verf_hv else '❌ NO VERIFICA'}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Propiedades Geométricas Calculadas:**")
    st.write(f"- **Jx:** {Jx:.2f} cm⁴ | **Wx:** {Wx:.2f} cm³")
    st.write(f"- **Jy:** {Jy:.2f} cm⁴ | **Wy:** {Wy:.2f} cm³")
    st.write(f"- **Peso propio viga:** {Pp:.2f} kgf/m")

with col2:
    st.subheader("📐 Geometría Transversal")
    st.plotly_chart(fig, use_container_width=True)

# =======================================================
# MOSTRAR DESGLOSE DE PESOS Y MÓDULO MECÁNICO
# =======================================================
st.markdown("---")
st.header("🛞 Dimensionamiento del Tambor y Balance Acumulado de Cargas")

st.success(f"""
⚖️ **Carga Total Centralizada Solicitante de la Viga Principal:**  
* **Carga Útil Nominal ($Q$):** {Q:.0f} kgf  
* **Peso Propio Calculado del Carro y Mecanismos ($P_{{carro}}$):** {P_carro_real:.1f} kgf  
  *(Pasteca/Gancho: {peso_pasteca:.0f} kgf | Cable de Acero: {res_tambor['peso_cable_kg']:.1f} kgf | Tambor Ranurado: {res_tambor['peso_tambor_kg']:.1f} kgf | Motor/Freno: 350 kgf)*  
* ➔ **CARGA TOTAL SOLICITANTE DE VIGA ($P_{{total}}$): {CARGA_TOTAL_ACTUANTE:.1f} kgf**
""")

st.markdown("---")
st.header("⚙️ Selección y Evaluación Técnica de Cables (DIN 4130)")
st.subheader(f"Tracción Máxima por Ramal ($S_{{max}}$): {S_max:.2f} kgf | Cable Recomendado: {d_cable_sel} mm")
st.dataframe(tabla_cables, use_container_width=True)

# Pie de Página Institucional
st.markdown("""
    <div class="footer-utn">
        <strong>Universidad Tecnológica Nacional — Facultad Regional Resistencia</strong><br>
        Departamento de Ingeniería Electromecánica | Cátedra de Máquinas y Equipos de Transporte
    </div>
""", unsafe_allow_html=True)