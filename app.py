import streamlit as st
import math
import io
import tempfile
import os
import plotly.graph_objects as go
import ezdxf
from ezdxf import recover

# ------------------------------------------------------------------------------
# IMPORTACIÓN DE MÓDULOS PROPIOS
# ------------------------------------------------------------------------------
from modulo_cables import verificar_cable_elevacion, obtener_catalogo_cables_completo
from modulo_tambor import calcular_dimensiones_tambor, estimar_peso_pasteca
from modulo_motor import calcular_motor_reductor
from modulo_reductor import evaluar_reductores_elevacion
from modulo_freno import calcular_freno_carga
from modulo_esquema import generar_diagrama_cinematico

# Alias de compatibilidad retroactiva
verificar_tabla_cables = verificar_cable_elevacion
obtener_tabla_cables_completa = obtener_catalogo_cables_completo

# ------------------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA Y ESTILO CONSOLA DE CONTROL TÉCNICA (UTN FRRE)
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Calculadora Integral Puente Grúa | UTN FRRE",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Fondo principal de consola con marca de agua discreta del escudo UTN */
    .stApp {
        background-color: #0b111e;
        background-image: radial-gradient(rgba(14, 165, 233, 0.12) 1px, transparent 0),
                          url("https://upload.wikimedia.org/wikipedia/commons/6/67/UTN_logo.jpg");
        background-size: 24px 24px, 180px auto;
        background-position: 0 0, calc(100% - 25px) calc(100% - 25px);
        background-repeat: repeat, no-repeat;
        background-attachment: fixed;
        color: #e2e8f0;
    }

    /* Barra lateral técnica */
    section[data-testid="stSidebar"] {
        background-color: #070d18 !important;
        border-right: 1px solid #1e293b;
    }

    /* Cabecera institucional */
    .header-utn {
        background: linear-gradient(135deg, #070d18 0%, #111c30 100%);
        border: 1px solid #1e3a5f;
        border-left: 6px solid #f59e0b;
        color: white;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
    }

    /* Títulos técnicos */
    h1, h2, h3, h4 {
        color: #38bdf8 !important;
        font-family: 'Consolas', 'Courier New', monospace;
        letter-spacing: 0.5px;
    }

    /* Tarjetas de métricas tipo display digital */
    div[data-testid="stMetric"] {
        background-color: #111c30;
        border: 1px solid #1e3a5f;
        border-left: 5px solid #f59e0b !important;
        border-radius: 6px;
        padding: 10px 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
    }
    
    div[data-testid="stMetric"] label {
        color: #94a3b8 !important;
        font-size: 0.85rem !important;
        text-transform: uppercase;
    }
    
    div[data-testid="stMetricValue"] {
        color: #f8fafc !important;
        font-family: 'Consolas', monospace;
        font-size: 22px !important;
        font-weight: bold;
    }

    /* Alertas técnicas */
    div[data-testid="stAlert"] {
        background-color: #0f233a !important;
        border: 1px solid #0284c7 !important;
        color: #e0f2fe !important;
        border-radius: 6px;
    }

    /* Tablas de catálogo */
    div[data-testid="stDataFrame"] {
        border: 1px solid #1e3a8a;
        border-radius: 6px;
        background-color: #0c1524;
    }

    /* Pie de página institucional */
    .footer-utn {
        text-align: center;
        padding: 15px;
        margin-top: 50px;
        border-top: 1px solid #1e293b;
        color: #64748b;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)

# Encabezado visual en pantalla
st.markdown("""
    <div class="header-utn">
        <h1 style="margin:0; font-size: 26px;">🏗️ Plataforma de Cálculo e Ingeniería de Puentes Grúa</h1>
        <p style="margin:5px 0 0 0; opacity: 0.9;">
            Dimensionamiento Integral Mecánico y Estructural (DIN 120 / DIN 4130 / DIN 15020 / FEM 9.511) — <strong>UTN Facultad Regional Resistencia</strong>
        </p>
    </div>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# PARÁMETROS EN BARRA LATERAL (SIDEBAR)
# ------------------------------------------------------------------------------
st.sidebar.header("📐 Modo de Geometría de Viga")
modo_geometria = st.sidebar.radio(
    "Origen de la sección transversal:",
    ["Paramétrica (Viga Cajón estándar)", "Importar desde Archivo DXF"]
)

Jx, Jy, Wx, Wy, Pp = 0.0, 0.0, 0.0, 0.0, 0.0
fig_geom = go.Figure()

# Función lectora de DXF con rotación y cálculo inercial
def procesar_dxf(uploaded_file, angulo_deg=0):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.dxf') as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    try:
        doc, auditor = recover.readfile(tmp_path)
    except Exception:
        doc = ezdxf.readfile(tmp_path)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
            
    msp = doc.modelspace()
    poligonos = []
    rad = math.radians(angulo_deg)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    
    for entity in msp:
        if entity.dxftype() in ('LWPOLYLINE', 'POLYLINE'):
            pts_orig = [(p[0], p[1]) for p in entity.get_points()]
            if len(pts_orig) >= 3:
                points = [(x * cos_a - y * sin_a, x * sin_a + y * cos_a) for x, y in pts_orig]
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

if modo_geometria == "Paramétrica (Viga Cajón estándar)":
    with st.sidebar.expander("📐 Geometría Cajón", expanded=True):
        b = st.number_input("Ancho viga (b) [mm]", value=500.0, step=10.0)
        h = st.number_input("Altura viga (h) [mm]", value=1000.0, step=10.0)
        esp_patin = st.number_input("Espesor de ala [mm]", value=9.525, step=0.1)
        esp_alma = st.number_input("Espesor de almas [mm]", value=9.525, step=0.1)
        dl = st.number_input("Retranqueo del alma (dl) [mm]", value=50.0, step=5.0)

    b_cm, h_cm = b/10, h/10
    esp_p_cm, esp_a_cm = esp_patin/10, esp_alma/10
    dl_cm = dl/10
    
    Jx = 2 * ((esp_a_cm * (h_cm**3))/12 + (b_cm * (esp_p_cm**3))/12 + b_cm * esp_p_cm * ((h_cm + esp_p_cm)/2)**2)
    Wx = Jx / (h_cm/2 + esp_p_cm)
    Jy = 2 * ((esp_p_cm * (b_cm**3))/12 + (h_cm * (esp_a_cm**3))/12 + ((b_cm/2 - dl_cm - esp_a_cm/2)**2) * h_cm * esp_a_cm)
    Wy = Jy / (b_cm/2)
    Pp = (2 * (b/1000) * (esp_patin/1000) + 2 * (h/1000) * (esp_alma/1000)) * 7860.0

    fig_geom.add_shape(type="rect", x0=-b/2, y0=h/2, x1=b/2, y1=h/2 + esp_patin, fillcolor="SteelBlue", line=dict(color="Black"))
    fig_geom.add_shape(type="rect", x0=-b/2, y0=-h/2 - esp_patin, x1=b/2, y1=-h/2, fillcolor="SteelBlue", line=dict(color="Black"))
    fig_geom.add_shape(type="rect", x0=-b/2 + dl, y0=-h/2, x1=-b/2 + dl + esp_alma, y1=h/2, fillcolor="LightSteelBlue", line=dict(color="Black"))
    fig_geom.add_shape(type="rect", x0=b/2 - dl - esp_alma, y0=-h/2, x1=b/2 - dl, y1=h/2, fillcolor="LightSteelBlue", line=dict(color="Black"))
    fig_geom.update_layout(xaxis=dict(range=[-b*0.7, b*0.7]), yaxis=dict(range=[-h*0.7, h*0.7]))

else:
    st.sidebar.subheader("📁 Cargar Archivo DXF")
    uploaded_dxf = st.sidebar.file_uploader("Seleccione el archivo .dxf en mm", type=["dxf"])
    rotacion_deg = st.sidebar.selectbox("🔄 Rotar Sección Transversal", [0, 90, 180, 270], index=1)
    
    if uploaded_dxf is not None:
        try:
            res_dxf = procesar_dxf(uploaded_dxf, angulo_deg=rotacion_deg)
            if res_dxf:
                Jx = res_dxf['Jx']
                Jy = res_dxf['Jy']
                Wx = res_dxf['Wx']
                Wy = res_dxf['Wy']
                Pp = res_dxf['Pp']
                st.sidebar.success("✅ DXF procesado correctamente")
                
                for idx, poly in enumerate(res_dxf['poligonos']):
                    pts = poly['pts']
                    xs = [p[0] - res_dxf['Cx'] for p in pts] + [pts[0][0] - res_dxf['Cx']]
                    ys = [p[1] - res_dxf['Cy'] for p in pts] + [pts[0][1] - res_dxf['Cy']]
                    fill_type = "toself" if idx == 0 else "none"
                    color_line = "Black" if idx == 0 else "Red"
                    fig_geom.add_trace(go.Scatter(
                        x=xs, y=ys, fill=fill_type, fillcolor="LightSteelBlue",
                        line=dict(color=color_line), mode="lines", name=f"Polígono {idx+1}"
                    ))
                
                fig_geom.update_layout(
                    showlegend=False,
                    yaxis=dict(scaleanchor="x", scaleratio=1),
                    xaxis=dict(constrain="domain")
                )
        except Exception as e:
            st.sidebar.error(f"Error al procesar DXF: {e}")

with st.sidebar.expander("🌉 Geometría del Puente y Cargas", expanded=True):
    tipo_puente = st.radio(
        "Tipología Estructural del Puente:",
        ["Doble Viga (Birraíl - Carro Apoyado)", "Monoviga (Viga Simple - Polipasto Suspendido)"],
        index=0
    )
    es_birrail = "Doble Viga" in tipo_puente

    Luz = st.number_input("Luz del puente (L) [m]", value=20.0, step=1.0)
    al = st.number_input("Distancia entre ruedas del carro (al) [mm]", value=1100.0, step=50.0)
    Q = st.number_input("Capacidad de carga útil en Gancho (Q) [kgf]", value=10000.0, step=500.0)
    
    divisor_flecha = st.selectbox("Divisor para Flecha Admisible (L / N)", options=list(range(400, 1201, 100)), index=4)
    f_adm = (Luz * 100.0) / divisor_flecha

with st.sidebar.expander("⚙️ Elevación y Polipasto", expanded=True):
    num_ramales = st.slider("Número de ramales del polipasto", min_value=2, max_value=10, value=4, step=1)
    grupo_din = st.selectbox("Grupo DIN 4130", ['I', 'II', 'III', 'IV', 'V'], index=2)
    ve_m_min = st.number_input("Velocidad de elevación [m/min]", value=8.0, step=0.5)
    he = st.number_input("Altura de elevación [m]", value=8.0, step=1.0)
    
    st.markdown("---")
    st.markdown("**📉 Rendimientos Mecánicos**")
    eta_poleas = st.number_input("Rendimiento Aparejo/Poleas (η_p)", value=0.97, min_value=0.80, max_value=0.99, step=0.01)
    eta_tambor = st.number_input("Rendimiento Tambor (η_t)", value=0.98, min_value=0.90, max_value=1.00, step=0.01)
    eta_reductor = st.number_input("Rendimiento Reductor (η_r)", value=0.93, min_value=0.50, max_value=0.98, step=0.01)

    phi = st.number_input("Coeficiente de choque (ϕ)", value=1.1, step=0.05)
    psi = st.number_input("Coeficiente de mayoración (ψ)", value=1.6, step=0.05)
    sigma_adm_v = st.number_input("σ admisible vertical [kgf/cm²]", value=1400.0)
    sigma_adm_hv = st.number_input("σ admisible combinada [kgf/cm²]", value=1600.0)
    E = st.number_input("Módulo elástico E [kgf/cm²]", value=2100000.0)

# ==============================================================================
# 1. SELECCIÓN TÉCNICA DEL CABLE (DIN 655 / VEROPRO)
# ==============================================================================
peso_pasteca = estimar_peso_pasteca(Q, num_ramales)

S_max, F_req, tabla_cables = verificar_cable_elevacion(
    Q_kg=Q,
    P_ap_kg=peso_pasteca,
    num_ramales=num_ramales
)

st.markdown("---")
st.subheader("🧵 Selección del Cable y Configuración del Polipasto")

col_p1, col_p2 = st.columns(2)
with col_p1:
    tipo_polipasto = st.radio("Tipo de Polipasto:", ["Gemelo (Doble arrollamiento)", "Simple (Un solo ramal al tambor)"], index=0)
with col_p2:
    vueltas_reserva = st.number_input("Vueltas de seguridad en tambor por lado:", min_value=2, max_value=5, value=3)

opcion_filtro = st.radio(
    "Filtrar catálogo de cables:",
    ["🟢 Ver solo Óptimos / Recomendados", "🟡 Ver Óptimos y Sobredimensionados", "📋 Ver Catálogo Completo"],
    horizontal=True
)

if "🟢 Ver solo Óptimos" in opcion_filtro:
    tabla_mostrar = tabla_cables[tabla_cables['Estado_Verificacion'] == "🟢 Óptimo / Recomendado"]
elif "🟡 Ver Óptimos y Sobredimensionados" in opcion_filtro:
    tabla_mostrar = tabla_cables[tabla_cables['Estado_Verificacion'].isin(["🟢 Óptimo / Recomendado", "🟡 Sobredimensionado"])]
else:
    tabla_mostrar = tabla_cables

st.dataframe(
    tabla_mostrar[[
        "Estado_Verificacion", "Norma_Marca", "Composicion", 
        "Diametro_mm", "CS_Real", "Rotura_kN_1960", "Peso_kg_m"
    ]],
    use_container_width=True
)

opc_cables = [
    f"{row['Norma_Marca']} - {row['Composicion']} | Ø{row['Diametro_mm']} mm ({row['Peso_kg_m']} kg/m)" 
    for _, row in tabla_mostrar.iterrows()
]

if len(opc_cables) > 0:
    cable_elegido_str = st.selectbox("👉 Seleccione el Cable a instalar en la grúa:", opc_cables)
    idx_sel = opc_cables.index(cable_elegido_str)
    cable_sel = tabla_mostrar.iloc[idx_sel]
    d_cable_sel = float(cable_sel["Diametro_mm"])
    peso_unitario_sel = float(cable_sel["Peso_kg_m"])
else:
    d_cable_sel = 14.0
    peso_unitario_sel = 0.88

# ==============================================================================
# 2. ADOPCIÓN DE COEFICIENTES h1, h2, h3 Y TAMBOR (DIN 15020)
# ==============================================================================
st.markdown("---")
st.subheader("📐 Adopción de Coeficientes para Tambor y Poleas (DIN 15020)")

MAPA_GRUPOS = {
    "I": "1Am (M4)", "II": "2m (M5)", "III": "3m (M6)", "IV": "4m (M7)", "V": "5m (M8)"
}
grupo_fem = MAPA_GRUPOS.get(str(grupo_din), "2m (M5)")

h_min_dict = {
    "1Bm (M3)": {"h1": 14.0, "h2": 16.0, "h3": 11.2},
    "1Am (M4)": {"h1": 16.0, "h2": 18.0, "h3": 12.5},
    "2m (M5)":  {"h1": 18.0, "h2": 20.0, "h3": 14.0},
    "3m (M6)":  {"h1": 20.0, "h2": 22.4, "h3": 16.0},
    "4m (M7)":  {"h1": 22.4, "h2": 25.0, "h3": 18.0},
    "5m (M8)":  {"h1": 25.0, "h2": 28.0, "h3": 20.0}
}
h_actual = h_min_dict.get(grupo_fem, {"h1": 18.0, "h2": 20.0, "h3": 14.0})

st.warning(f"**Mínimos normativos FEM ({grupo_fem}):** "
           f"**$h_{{1,min}} = {h_actual['h1']}$** (Tambor) | "
           f"**$h_{{2,min}} = {h_actual['h2']}$** (Pasteca) | "
           f"**$h_{{3,min}} = {h_actual['h3']}$** (Reenvío).")

col_h1, col_h2, col_h3 = st.columns(3)
with col_h1:
    h1_user = st.number_input("Adoptar $h_1$ (Tambor):", value=float(h_actual['h1']), step=0.5)
with col_h2:
    h2_user = st.number_input("Adoptar $h_2$ (Poleas Pasteca):", value=float(h_actual['h2']), step=0.5)
with col_h3:
    h3_user = st.number_input("Adoptar $h_3$ (Polea Reenvío):", value=float(h_actual['h3']), step=0.5)

marca_cable_sel = str(cable_sel["Norma_Marca"]) if 'cable_sel' in locals() else "DIN"

res_tambor = calcular_dimensiones_tambor(
    d_cable_mm=d_cable_sel,
    H_elevacion_m=he,
    num_ramales=num_ramales,
    peso_kg_m=peso_unitario_sel,
    tipo_polipasto=tipo_polipasto,
    vueltas_reserva=vueltas_reserva,
    grupo_fem=grupo_fem,
    h1_adoptado=h1_user,
    h2_adoptado=h2_user,
    h3_adoptado=h3_user,
    marca_cable=marca_cable_sel
)

if not (res_tambor['h1_valido'] and res_tambor['h2_valido'] and res_tambor['h3_valido']):
    st.error("❌ Uno o más coeficientes adoptados están por debajo del mínimo exigido por norma.")
else:
    st.success("✅ Coeficientes verificados conforme a DIN 15020.")

col_t1, col_t2, col_t3, col_t4 = st.columns(4)
col_t1.metric("Ø Tambor ($D_t$)", f"{res_tambor['D_tambor_mm']} mm")
col_t2.metric("Ancho Tambor ($L_t$)", f"{res_tambor['L_tambor_mm']} mm")
col_t3.metric("Ø Poleas Pasteca ($D_p$)", f"{res_tambor['D_polea_mm']} mm")
col_t4.metric("Ø Polea Reenvío ($D_r$)", f"{res_tambor['D_reenvio_mm']} mm")

# ==============================================================================
# 3. MOTORIZACIÓN Y SELECCIÓN DE REDUCTOR LENTAX 820
# ==============================================================================
st.markdown("---")
st.header("⚡ Selección del Grupo Motorreductor de Elevación")

# Cálculo preliminar de potencia con la carga en gancho y peso preliminar de aparejo y tambor
peso_mecanico_previo = peso_pasteca + res_tambor['peso_cable_kg'] + res_tambor['peso_tambor_kg']
res_motor = calcular_motor_reductor(
    carga_total_kg=Q + peso_mecanico_previo,
    v_elev_m_min=ve_m_min,
    D_tambor_mm=res_tambor['D_tambor_mm'],
    num_ramales=num_ramales,
    eta_poleas=eta_poleas,
    eta_tambor=eta_tambor,
    eta_reductor=eta_reductor
)

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("Rendimiento Global (η)", f"{res_motor['eta_global']} %")
col_m2.metric("Potencia Absorbida", f"{res_motor['potencia_teorica_kw']} kW")
col_m3.metric("Motor IEC Recomendado", f"{res_motor['potencia_motor_kw']} kW")
col_m4.metric("Velocidad Tambor", f"{res_motor['n_tambor_rpm']} rpm")

# Estimación del peso propio del motor eléctrico normalizado IEC
pot_kw = res_motor['potencia_motor_kw']
if pot_kw <= 7.5:
    peso_motor_iec_kg = 75.0
elif pot_kw <= 15.0:
    peso_motor_iec_kg = 135.0
elif pot_kw <= 22.0:
    peso_motor_iec_kg = 190.0
elif pot_kw <= 30.0:
    peso_motor_iec_kg = 245.0
elif pot_kw <= 45.0:
    peso_motor_iec_kg = 330.0
else:
    peso_motor_iec_kg = 480.0

st.markdown("---")
st.subheader("⚙️ Selección del Reductor Industrial (Catálogo LENTAX 820)")

n_motor_std = 1500.0
n_t = res_motor['n_tambor_rpm'] if res_motor['n_tambor_rpm'] > 0 else 15.0
i_teorico_req = n_motor_std / n_t

tabla_reductores = evaluar_reductores_elevacion(
    i_requerido=i_teorico_req,
    P_motor_kW=res_motor['potencia_motor_kw'],
    factor_servicio=1.3
)

st.dataframe(
    tabla_reductores[["Estado_Reductor", "Modelo", "Serie", "i_nominal", "Desvio_i_%", "P_adm_kW", "Capacidad_Potencia", "Peso_kg", "d2_eje_mm"]],
    use_container_width=True
)

reductores_validos = tabla_reductores[tabla_reductores["Estado_Reductor"] == "🟢 Adecuado / Verificado"]

if not reductores_validos.empty:
    opc_red = [
        f"{r['Modelo']} (i={r['i_nominal']}:1 | P_adm={r['P_adm_kW']} kW | Peso={r['Peso_kg']} kg)"
        for _, r in reductores_validos.iterrows()
    ]
    red_sel_str = st.selectbox("👉 Seleccionar Modelo de Reductor LENTAX:", opc_red)
    idx_r = opc_red.index(red_sel_str)
    reductor_elegido = reductores_validos.iloc[idx_r]
else:
    opc_todas = [
        f"{r['Modelo']} (i={r['i_nominal']}:1 | Desvío={r['Desvio_i_%']}%)"
        for _, r in tabla_reductores.iterrows()
    ]
    red_sel_str = st.selectbox("👉 Seleccionar Modelo Alternativo LENTAX:", opc_todas)
    idx_r = opc_todas.index(red_sel_str)
    reductor_elegido = tabla_reductores.iloc[idx_r]

i_reductor_real = float(reductor_elegido["i_nominal"])
peso_reductor_real = float(reductor_elegido["Peso_kg"])
res_motor['i_reductor'] = i_reductor_real

v_elev_real = (ve_m_min * (i_teorico_req / i_reductor_real))
st.success(f"✅ **Reductor Adoptado:** {reductor_elegido['Modelo']} (Peso: **{peso_reductor_real:.0f} kg**) | Velocidad real resultante: **{v_elev_real:.2f} m/min**")

# ==============================================================================
# 4. FRENO DE RETENCIÓN DE CARGA (EJE MOTOR)
# ==============================================================================
st.markdown("---")
st.subheader("🛑 Freno de Seguridad y Retención de Carga (Eje Veloz)")

M_carga_motor, M_freno_req, kf_aplicado, tabla_frenos, url_catalogo = calcular_freno_carga(
    Q_kg=Q,
    P_pasteca_kg=peso_pasteca,
    D_tambor_mm=res_tambor['D_tambor_mm'],
    i_reduccion=res_motor['i_reductor'],
    grupo_fem=grupo_fem
)

st.warning(
    f"🔒 **Par de Carga en Eje Motor:** {M_carga_motor} N·m | "
    f"**Coeficiente $k_f$ ({grupo_fem}):** {kf_aplicado} | "
    f"**Par Mínimo Requerido:** **{M_freno_req} N·m**"
)

st.dataframe(
    tabla_frenos[["Estado_Freno", "Marca_Serie", "Modelo", "Par_Nominal_Nm", "k_f_Real", "Peso_kg", "Potencia_W"]],
    use_container_width=True
)

opc_frenos = [
    f"{row['Marca_Serie']} ({row['Modelo']}) | Par: {row['Par_Nominal_Nm']} N·m | Peso: {row['Peso_kg']} kg"
    for _, row in tabla_frenos[~tabla_frenos["Estado_Freno"].str.contains("Insuficiente")].iterrows()
]

if len(opc_frenos) > 0:
    freno_elegido_str = st.selectbox("👉 Seleccione el Freno comercial a instalar:", opc_frenos)
    idx_fr = opc_frenos.index(freno_elegido_str)
    freno_sel = tabla_frenos[~tabla_frenos["Estado_Freno"].str.contains("Insuficiente")].iloc[idx_fr]
    peso_freno_real = float(freno_sel["Peso_kg"])
else:
    peso_freno_real = 25.0

st.success(f"✅ **Freno Seleccionado:** {freno_sel['Modelo']} (Peso: **{peso_freno_real:.1f} kg**)")

# ==============================================================================
# 5. ESQUEMA KINEMÁTICO DEL CARRO
# ==============================================================================
st.markdown("---")
st.subheader("🗺️ Esquema Kinemático y Distribución de Componentes en el Carro")

fig_croquis = generar_diagrama_cinematico(
    D_tambor_mm=res_tambor['D_tambor_mm'],
    L_tambor_mm=res_tambor['L_tambor_mm'],
    D_polea_mm=res_tambor['D_polea_mm'],
    num_ramales=num_ramales,
    tipo_polipasto=tipo_polipasto
)
st.plotly_chart(fig_croquis, use_container_width=True)

# ==============================================================================
# 6. BALANCE CONSOLIDADO DE CARGAS Y CÁLCULO ESTRUCTURAL DE LA VIGA CAJÓN
# ==============================================================================
st.markdown("---")
st.header("🏗️ Cálculo y Verificación Estructural de la Viga Principal (DIN 120 / DIN 4132)")

# Bastidor estructural estimado del carro
peso_bastidor_carro_kg = 400.0

# Sumatoria exacta de todos los pesos de catálogo y componentes
P_carro_consolidado = (
    peso_pasteca 
    + res_tambor['peso_cable_kg'] 
    + res_tambor['peso_tambor_kg'] 
    + peso_motor_iec_kg 
    + peso_reductor_real 
    + peso_freno_real 
    + peso_bastidor_carro_kg
)

CARGA_TOTAL_ACTUANTE = Q + P_carro_consolidado

st.info(f"""
⚖️ **Desglose de Cargas Reales de Componentes:**
* **Carga Útil ($Q$):** {Q:.0f} kgf
* **Pasteca y Gancho:** {peso_pasteca:.1f} kgf
* **Cable de Elevación:** {res_tambor['peso_cable_kg']:.1f} kgf
* **Tambor Ranurado:** {res_tambor['peso_tambor_kg']:.1f} kgf
* **Motor IEC ({pot_kw} kW):** {peso_motor_iec_kg:.1f} kgf
* **Reductor LENTAX ({reductor_elegido['Modelo']}):** {peso_reductor_real:.1f} kgf
* **Freno INTORQ ({freno_sel['Modelo']}):** {peso_freno_real:.1f} kgf
* **Chasis / Estructura del Carro:** {peso_bastidor_carro_kg:.1f} kgf
* ➔ **PESO TOTAL DEL CARRO ($P_{{carro}}$): {P_carro_consolidado:.1f} kgf**
* ➔ **CARGA TOTAL MÓVIL SOBRE EL PUENTE ($P_{{total}}$): {CARGA_TOTAL_ACTUANTE:.1f} kgf**
""")

# Parámetros mecánicos y estáticos de la viga
Luz_cm, al_cm = Luz * 100.0, al / 10.0

if es_birrail:
    num_vigas_puente = 2
    Pr = CARGA_TOTAL_ACTUANTE / 4.0  # Carga por rueda sobre una viga cajón (4 ruedas totales)
    st.info(f"ℹ️ **Configuración Birraíl (Doble Viga):** La carga se reparte entre 2 vigas. Carga de cálculo por rueda: **$P_r = {Pr:.1f}$ kgf**.")
else:
    num_vigas_puente = 1
    Pr = CARGA_TOTAL_ACTUANTE / 2.0  # Carga por tándem de ruedas sobre la viga única suspendida
    st.info(f"ℹ️ **Configuración Monoviga (Viga Simple):** El 100% de la carga gravita sobre una única viga. Carga de cálculo por apoyo de eje: **$P_r = {Pr:.1f}$ kgf**.")

# Momento flector vertical máximo (Teorema de Barré simplificado)
Mpmax = Pr * ((Luz_cm - al_cm/2.0)**2) / (2.0 * Luz_cm)
ge = Pp + 40.0  # Peso viga + riel / pasarela
Mg1 = (ge * (Luz**2) / 8.0) * 100.0
g2 = 700.0  # Carga puntual central de mecanismos de traslación
Mg2 = (g2 * Luz / 4.0) * 100.0

sigma_v = (phi * (Mg1 + Mg2) + psi * Mpmax) / Wx if Wx > 0 else 0.0

# Solicitación lateral horizontal (1/14 de Pr según DIN 120)
Fih = Pr / 14.0
Mpmax_H = (Fih * ((Luz_cm - al_cm/2.0)**2)) / (2.0 * Luz_cm)
Mg1_H = Mg1 / 14.0
Mg2_H = Mg2 / 14.0

sigma_Hv = sigma_v + (Mpmax_H + Mg1_H + Mg2_H) / Wy if Wy > 0 else 0.0
f_real = (Pr * (Luz_cm - al_cm) * (Luz_cm**2 + (Luz_cm + al_cm)**2)) / (48.0 * E * Jx) if Jx > 0 else 0.0

# Despliegue de resultados estructurales
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📊 Verificaciones Estructurales")
    
    verf_v = sigma_v <= sigma_adm_v if sigma_v > 0 else False
    color_border_v = "#1e8e3e" if verf_v else "#d93025"
    st.markdown(f"""
    <div style="background-color: {'#064e3b' if verf_v else '#7f1d1d'}; border: 2px solid {color_border_v}; border-radius: 8px; padding: 15px; margin-bottom: 10px;">
        <span style="font-size: 14px; font-weight: bold; color: #f8fafc;">Tensión Flexión Vertical (σv)</span>
        <div style="font-size: 24px; font-weight: bold; color: #ffffff;">{sigma_v:.2f} kgf/cm²</div>
        <div style="font-size: 13px; font-weight: bold; color: {'#34d399' if verf_v else '#f87171'};">{'✅ VERIFICA (σv ≤ ' + str(sigma_adm_v) + ')' if verf_v else '❌ NO VERIFICA'}</div>
    </div>
    """, unsafe_allow_html=True)

    verf_hv = sigma_Hv <= sigma_adm_hv if sigma_Hv > 0 else False
    color_border_hv = "#1e8e3e" if verf_hv else "#d93025"
    st.markdown(f"""
    <div style="background-color: {'#064e3b' if verf_hv else '#7f1d1d'}; border: 2px solid {color_border_hv}; border-radius: 8px; padding: 15px; margin-bottom: 10px;">
        <span style="font-size: 14px; font-weight: bold; color: #f8fafc;">Tensión Combinada V+H (σHv)</span>
        <div style="font-size: 24px; font-weight: bold; color: #ffffff;">{sigma_Hv:.2f} kgf/cm²</div>
        <div style="font-size: 13px; font-weight: bold; color: {'#34d399' if verf_hv else '#f87171'};">{'✅ VERIFICA (σHv ≤ ' + str(sigma_adm_hv) + ')' if verf_hv else '❌ NO VERIFICA'}</div>
    </div>
    """, unsafe_allow_html=True)

    verf_f = f_real <= f_adm if f_real > 0 else False
    st.metric("Flecha Elástica Calculada", f"{f_real:.2f} cm", delta=f"Límite L/{divisor_flecha}: {f_adm:.2f} cm", delta_color="normal" if verf_f else "inverse")

    st.markdown("**Propiedades Geométricas de la Sección Adoptada:**")
    st.write(f"- **Jx:** {Jx:.2f} cm⁴ | **Wx:** {Wx:.2f} cm³")
    st.write(f"- **Jy:** {Jy:.2f} cm⁴ | **Wy:** {Wy:.2f} cm³")
    st.write(f"- **Peso lineal viga:** {Pp:.2f} kgf/m")

with col2:
    st.subheader("📐 Sección Transversal")
    st.plotly_chart(fig_geom, use_container_width=True)

# ==============================================================================
# 7. MÓDULO DE TESTERAS DEL PUENTE (DIN 120 / FEM 1001)
# ==============================================================================
from modulo_testera import calcular_testera, obtener_catalogo_perfiles_testera

st.markdown("---")
st.header("🛞 Dimensionamiento y Verificación de Testeras (Cabeceros)")

col_test1, col_test2 = st.columns(2)
with col_test1:
    # L/7 a L/6
    batalla_sugerida = round(((Luz * 1000.0) / 6.5) / 100.0) * 100.0
    batalla_at_user = st.number_input(
        "Batalla entre ruedas de testera (at) [mm]:", 
        min_value=1500.0, max_value=6000.0, 
        value=float(batalla_sugerida), step=100.0,
        help="Distancia entre centros de rueda de traslación del puente. Criterio: L/7 a L/6 para evitar acuñamiento."
    )
    
with col_test2:
    e_acercamiento_user = st.number_input(
        "Acercamiento mínimo del gancho/carro (e_min) [mm]:",
        min_value=800.0, max_value=3000.0,
        value=1200.0, step=50.0,
        help="Distancia mínima de aproximación del centro de gancho al riel de la carrilera."
    )

catalogo_test = obtener_catalogo_perfiles_testera()
perfil_testera_adoptado = st.selectbox(
    "Seleccionar Perfil en Cajón para la Testera:",
    catalogo_test["Perfil"].tolist(),
    index=2  # 2x UPN 260 por defecto
)

res_testera = calcular_testera(
    Luz_puente_m=Luz,
    es_birrail=es_birrail,
    distancia_ruedas_carro_al_mm=al,
    peso_lineal_viga_kg_m=Pp,
    peso_carro_total_kg=P_carro_consolidado,
    Q_carga_kg=Q,
    acercamiento_min_e_mm=e_acercamiento_user,
    batalla_adoptada_at_mm=batalla_at_user,
    perfil_seleccionado_str=perfil_testera_adoptado,
    sigma_adm_kgf_cm2=sigma_adm_v
)

st.info(
    f"📏 **Criterio Normativo de Batalla ($a_t$):** Mínimo ($L/7$) = **{res_testera['at_min_norma_mm']:.0f} mm** | "
    f"Recomendado ($L/6$) = **{res_testera['at_rec_norma_mm']:.0f} mm**. "
    f"{'🟢 Cumple relación anti-acuñamiento.' if batalla_at_user >= res_testera['at_min_norma_mm'] else '⚠️ Batalla corta, riesgo de acuñamiento.'}"
)

col_mtr1, col_mtr2, col_mtr3, col_mtr4 = st.columns(4)
col_mtr1.metric("Reacción Total Testera", f"{res_testera['R_total_testera_ton']} t")
col_mtr2.metric("Carga Máx. por Rueda ($P_r$)", f"{res_testera['P_rueda_max_ton']} t", help=f"{res_testera['P_rueda_max_kg']} kgf")
col_mtr3.metric("Momento Flector Testera", f"{res_testera['M_testera_kNm']} kN·m")
col_mtr4.metric(
    "Tensión Flexión (σ)", 
    f"{res_testera['sigma_real_kgf_cm2']:.1f} kgf/cm²",
    delta="Verifica" if res_testera['verifica_sigma'] else "No verifica",
    delta_color="normal" if res_testera['verifica_sigma'] else "inverse"
)

st.dataframe(res_testera["tabla_perfiles"], use_container_width=True)

# ------------------------------------------------------------------------------
# PIE DE PÁGINA INSTITUCIONAL
# ------------------------------------------------------------------------------
st.markdown("""
    <div class="footer-utn">
        <strong>Universidad Tecnológica Nacional — Facultad Regional Resistencia</strong><br>
        Departamento de Ingeniería Electromecánica | Cátedra de Máquinas y Equipos de Transporte
    </div>
""", unsafe_allow_html=True)