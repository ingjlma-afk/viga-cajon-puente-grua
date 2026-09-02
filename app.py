import streamlit as st
import math
import io
import tempfile
import os
import plotly.graph_objects as go
import ezdxf
from ezdxf import recover

# Importación de módulos propios
from modulo_cables import verificar_tabla_cables, obtener_tabla_cables_completa
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

# Variables geométricas iniciales
Jx, Jy, Wx, Wy, Pp = 0.0, 0.0, 0.0, 0.0, 0.0
fig = go.Figure()

# --- CÁLCULO DE PROPIEDADES GEOMÉTRICAS DXF CON ROTACIÓN Y LECTURA BINARIA ---
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
    
    # Matriz de rotación en radianes
    rad = math.radians(angulo_deg)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    
    for entity in msp:
        if entity.dxftype() in ('LWPOLYLINE', 'POLYLINE'):
            pts_orig = [(p[0], p[1]) for p in entity.get_points()]
            if len(pts_orig) >= 3:
                # Rotación de puntos sobre el centroide (0,0) de CAD
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

# --- ENTRADA DE DATOS Y SELECCIÓN GEOMÉTRICA ---
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

    fig.add_shape(type="rect", x0=-b/2, y0=h/2, x1=b/2, y1=h/2 + esp_patin, fillcolor="SteelBlue", line=dict(color="Black"))
    fig.add_shape(type="rect", x0=-b/2, y0=-h/2 - esp_patin, x1=b/2, y1=-h/2, fillcolor="SteelBlue", line=dict(color="Black"))
    fig.add_shape(type="rect", x0=-b/2 + dl, y0=-h/2, x1=-b/2 + dl + esp_alma, y1=h/2, fillcolor="LightSteelBlue", line=dict(color="Black"))
    fig.add_shape(type="rect", x0=b/2 - dl - esp_alma, y0=-h/2, x1=b/2 - dl, y1=h/2, fillcolor="LightSteelBlue", line=dict(color="Black"))
    fig.update_layout(xaxis=dict(range=[-b*0.7, b*0.7]), yaxis=dict(range=[-h*0.7, h*0.7]))

else:
    st.sidebar.subheader("📁 Cargar Archivo DXF")
    uploaded_dxf = st.sidebar.file_uploader("Seleccione el archivo .dxf dibujado en mm", type=["dxf"])
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
                    fig.add_trace(go.Scatter(
                        x=xs, y=ys, 
                        fill=fill_type, 
                        fillcolor="LightSteelBlue", 
                        line=dict(color=color_line), 
                        mode="lines", 
                        name=f"Polígono {idx+1}"
                    ))
                
                # FORZAR ESCALA 1:1 EN AMBOS EJES PARA VER EL GIRO REAL
                fig.update_layout(
                    showlegend=False,
                    yaxis=dict(scaleanchor="x", scaleratio=1),
                    xaxis=dict(constrain="domain")
                )
            else:
                st.sidebar.error("No se encontraron polilíneas cerradas en el DXF.")
        except Exception as e:
            st.sidebar.error(f"Error al procesar DXF: {e}")
    else:
        st.info("👈 Cargue el archivo .dxf desde la barra lateral para procesar la geometría.")

# --- PARÁMETROS DE CARGA Y MECANISMOS EN BARRA LATERAL ---
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
    
    st.markdown("---")
    st.markdown("**📉 Rendimientos Mecánicos (DIN 15020)**")
    eta_poleas = st.number_input("Rendimiento Aparejo/Poleas (η_p)", value=0.97, min_value=0.80, max_value=0.99, step=0.01, help="Rodamientos: 0.97-0.98 | Bujes: 0.93-0.95")
    eta_tambor = st.number_input("Rendimiento Tambor (η_t)", value=0.98, min_value=0.90, max_value=1.00, step=0.01)
    eta_reductor = st.number_input("Rendimiento Reductor (η_r)", value=0.93, min_value=0.50, max_value=0.98, step=0.01, help="Engranajes Cilíndricos/Helicoidales: 0.92-0.96 | Corona y Sinfín: 0.60-0.75")

    phi = st.number_input("Coeficiente de choque (ϕ)", value=1.1, step=0.05)
    psi = st.number_input("Coeficiente de mayoración (ψ)", value=1.6, step=0.05)
    sigma_adm_v = st.number_input("σ admisible vertical [kgf/cm²]", value=1400.0)
    sigma_adm_hv = st.number_input("σ admisible combinada [kgf/cm²]", value=1600.0)
    E = st.number_input("Módulo elástico E [kgf/cm²]", value=2100000.0)

# ==============================================================================
# CÁLCULOS MECÁNICOS Y CARGA FINAL
# ==============================================================================
peso_pasteca = estimar_peso_pasteca(Q, num_ramales)

S_max, F_req, tabla_cables = verificar_tabla_cables(
    Q_kg=Q,
    P_ap_kg=peso_pasteca,
    num_ramales=num_ramales
)

# ------------------------------------------------------------------------------
# INTERFAZ VISUAL: SELECCIÓN INTERACTIVA Y GEOMETRÍA
# ------------------------------------------------------------------------------
st.markdown("---")
st.subheader("🧵 Selección del Cable y Configuración del Polipasto")

col_p1, col_p2 = st.columns(2)
with col_p1:
    tipo_polipasto = st.radio("Tipo de Polipasto:", ["Gemelo (Doble arrollamiento)", "Simple (Un solo ramal al tambor)"], index=0)
with col_p2:
    vueltas_reserva = st.number_input("Vueltas de seguridad en tambor por lado:", min_value=2, max_value=5, value=3)

# Filtro de catálogo
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

# EL ALUMNO SELECCIONA EL CABLE DEFINITIVO DE LA LISTA
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

# ------------------------------------------------------------------------------
# ADOPCIÓN DE COEFICIENTES h1, h2, h3 (DECISIÓN DEL ALUMNO)
# ------------------------------------------------------------------------------
st.markdown("---")
st.subheader("📐 Adopción de Coeficientes para Tambor y Poleas (DIN 15020)")

# Traemos la tabla de mínimos para alertar al alumno
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

# CÁLCULO DE GEOMETRÍA CON LOS VALORES ADOPTADOS
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
    h3_adoptado=h3_user
)

# VERIFICACIÓN TÉCNICA
if not (res_tambor['h1_valido'] and res_tambor['h2_valido'] and res_tambor['h3_valido']):
    st.error("❌ **ERROR NORMATIVO:** Uno o más coeficientes adoptados están por debajo del mínimo exigido por DIN 15020 / FEM.")
else:
    st.success("✅ **DISEÑO VERIFICADO:** Los coeficientes adoptados cumplen con las exigencias normativas.")

# MOSTRAR RESULTADOS EN PANTALLA
st.subheader("⚙️ Dimensiones Calculadas de Componentes")
col_t1, col_t2, col_t3, col_t4 = st.columns(4)
col_t1.metric("Ø Tambor ($D_t$)", f"{res_tambor['D_tambor_mm']} mm")
col_t2.metric("Ancho Tambor ($L_t$)", f"{res_tambor['L_tambor_mm']} mm")
col_t3.metric("Ø Poleas Pasteca ($D_p$)", f"{res_tambor['D_polea_mm']} mm")
col_t4.metric("Ø Polea Reenvío ($D_r$)", f"{res_tambor['D_reenvio_mm']} mm")

if "Gemelo" in str(tipo_polipasto):
    st.info(f"📏 **Separación central libre en tambor ($L_{{centro}}$):** {res_tambor['L_centro_mm']} mm (Igual al Ø de polea de pasteca para evitar desvío de cable).")

# BALANCE FINAL DE CARGAS CARRO
peso_mecanismos_est = 350.0
P_carro_real = peso_pasteca + res_tambor['peso_cable_kg'] + res_tambor['peso_tambor_kg'] + peso_mecanismos_est
CARGA_TOTAL_ACTUANTE = Q + P_carro_real

# =======================================================
# CÁLCULO ESTRUCTURAL DE LA VIGA
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
# MÓDULOS MECÁNICOS Y DESGLOSE
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


from modulo_motor import calcular_motor_reductor

# =======================================================
# MÓDULO DE MOTORIZACIÓN Y REDUCTOR
# =======================================================
st.markdown("---")
st.header("⚡ Selección del Grupo Motorreductor de Elevación")

res_motor = calcular_motor_reductor(
    carga_total_kg=CARGA_TOTAL_ACTUANTE,
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
col_m4.metric("Relación Reducción (i)", f"{res_motor['i_reductor']}:1")

st.info(f"""
💡 **Análisis Cinemático:**  
* **Potencia útil neta en gancho:** {res_motor['potencia_util_kw']} kW  
* **Pérdidas acumuladas por rozamiento:** {res_motor['potencia_teorica_kw'] - res_motor['potencia_util_kw']:.2f} kW  
* **Torque en el eje del tambor:** {res_motor['torque_tambor_Nm']} N·m a {res_motor['n_tambor_rpm']} rpm.
""")

# Pie de Página
st.markdown("""
    <div class="footer-utn">
        <strong>Universidad Tecnológica Nacional — Facultad Regional Resistencia</strong><br>
        Departamento de Ingeniería Electromecánica | Cátedra de Máquinas y Equipos de Transporte
    </div>
""", unsafe_allow_html=True)