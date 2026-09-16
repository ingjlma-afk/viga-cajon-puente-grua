# modulo_reporte.py
from fpdf import FPDF
from datetime import datetime
import io

class ReporteIngenieriaPDF(FPDF):
    def header(self):
        self.set_fill_color(7, 13, 24)
        self.rect(0, 0, 210, 22, 'F')
        
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(56, 189, 248)
        self.cell(0, 5, "UTN FRRE - DEPARTAMENTO DE INGENIERIA ELECTROMECANICA", ln=True, align="L")
        
        self.set_font("Helvetica", "", 8)
        self.set_text_color(226, 232, 240)
        self.cell(0, 4, "Catedra: Maquinas y Equipos de Transporte | Memoria Tecnica Ejecutiva", ln=True, align="L")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(148, 163, 184)
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.cell(0, 10, f"Generado: {fecha} | Pagina {self.page_no()}/{{nb}}", align="C")

def crear_fila_tabla(pdf, etiqueta, valor, unidad="", fill=False):
    pdf.set_fill_color(241, 245, 249) if fill else pdf.set_fill_color(255, 255, 255)
    pdf.set_text_color(15, 23, 42)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(105, 6, etiqueta, border=1, fill=fill)
    pdf.set_font("Helvetica", "", 9)
    val_str = f"{valor} {unidad}".strip()
    pdf.cell(80, 6, val_str, border=1, ln=True, fill=fill)

def generar_pdf_memoria(datos: dict) -> bytes:
    pdf = ReporteIngenieriaPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    
    # Titulo de Portada / Resumen
    pdf.set_font("Helvetica", "B", 15)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 8, "MEMORIA DE CALCULO Y VERIFICACION - PUENTE GRUA", ln=True, align="C")
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 5, f"Normativa de aplicacion: DIN 120 / DIN 4130 / DIN 15020 / FEM 9.511 / DIN 4132", ln=True, align="C")
    pdf.ln(5)

    def subtitulo(texto):
        pdf.set_fill_color(30, 58, 95)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(185, 6.5, f"  {texto}", border=0, ln=True, fill=True)
        pdf.ln(1)

    # 1. PARAMETROS GENERALES
    subtitulo("1. CONDICIONES GENERALES DE SERVICIO")
    crear_fila_tabla(pdf, "Tipologia Estructural", datos.get('tipologia', 'N/D'), fill=True)
    crear_fila_tabla(pdf, "Capacidad Nominal en Gancho (Q)", f"{datos.get('Q_ton', 0):.2f}", "t")
    crear_fila_tabla(pdf, "Luz entre Rieles (L)", f"{datos.get('Luz_m', 0):.2f}", "m", fill=True)
    crear_fila_tabla(pdf, "Altura de Elevacion (H)", f"{datos.get('H_m', 0):.2f}", "m")
    crear_fila_tabla(pdf, "Grupo de Mecanismo DIN / FEM", f"{datos.get('grupo_din', 'N/D')} / {datos.get('grupo_fem', 'N/D')}", fill=True)
    pdf.ln(3)

    # 2. SISTEMA MECANICO DE ELEVACION
    subtitulo("2. CADENA CINEMATICA DE ELEVACION")
    crear_fila_tabla(pdf, "Cable Seleccionado", datos.get('cable_nombre', 'N/D'), fill=True)
    crear_fila_tabla(pdf, "Diametro de Cable / Factor Seguridad Real", f"Ø {datos.get('d_cable', 0)} mm | CS = {datos.get('cs_cable', 0):.2f}")
    crear_fila_tabla(pdf, "Tambor: Diametro / Longitud", f"Ø {datos.get('D_tambor', 0):.1f} mm | L = {datos.get('L_tambor', 0):.1f} mm", fill=True)
    crear_fila_tabla(pdf, "Diametro de Poleas Pasteca", f"Ø {datos.get('D_polea', 0):.1f}", "mm")
    crear_fila_tabla(pdf, "Potencia Motor IEC Elevacion", f"{datos.get('pot_motor_elev', 0):.2f}", "kW", fill=True)
    crear_fila_tabla(pdf, "Reductor Industrial Seleccionado", f"{datos.get('modelo_reductor', 'N/D')} (i = {datos.get('i_reductor', 0):.1f}:1)")
    crear_fila_tabla(pdf, "Freno de Retencion (Eje Rapido)", f"{datos.get('freno_nombre', 'N/D')} (kf = {datos.get('freno_kf', 0):.2f})", fill=True)
    pdf.ln(3)

    # 3. BALANCE DE CARGAS DEL CARRO
    subtitulo("3. BALANCE CONSOLIDADO DE PESOS DEL CARRO")
    crear_fila_tabla(pdf, "Aparejo / Pasteca de Carga", f"{datos.get('p_pasteca', 0):.1f}", "kg", fill=True)
    crear_fila_tabla(pdf, "Cable de Acero en Servicio", f"{datos.get('p_cable', 0):.1f}", "kg")
    crear_fila_tabla(pdf, "Tambor Ranurado", f"{datos.get('p_tambor', 0):.1f}", "kg", fill=True)
    crear_fila_tabla(pdf, "Motor + Reductor + Freno de Elevacion", f"{datos.get('p_mecanismos', 0):.1f}", "kg")
    crear_fila_tabla(pdf, "Estructura y Bastidor del Carro", f"{datos.get('p_bastidor', 0):.1f}", "kg", fill=True)
    crear_fila_tabla(pdf, "PESO TOTAL CARRO CONSOLIDADO", f"{datos.get('p_carro_tot', 0):.1f}", "kg")
    crear_fila_tabla(pdf, "CARGA MOVIL TOTAL GRAVITANTE (Q + Carro)", f"{datos.get('p_movil_tot', 0):.1f}", "kg", fill=True)
    pdf.ln(3)

    # 4. ESTRUCTURA PRINCIPAL (VIGA CAJON)
    subtitulo("4. VERIFICACION ESTRUCTURAL DE LA VIGA CAJON")
    crear_fila_tabla(pdf, "Seccion Adoptada", datos.get('sec_viga_nombre', 'Viga Cajon'), fill=True)
    crear_fila_tabla(pdf, "Inercia Jx / Modulo Wx", f"{datos.get('Jx_cm4', 0):.1f} cm4 | {datos.get('Wx_cm3', 0):.1f} cm3")
    crear_fila_tabla(pdf, "Peso Propio Lineal Viga", f"{datos.get('Pp_viga', 0):.1f}", "kg/m", fill=True)
    crear_fila_tabla(pdf, "Tension Flexion Vertical (sigma_v)", f"{datos.get('sigma_v', 0):.2f} kgf/cm2 (Adm: {datos.get('adm_v', 0):.0f})")
    crear_fila_tabla(pdf, "Tension Combinada V+H (sigma_Hv)", f"{datos.get('sigma_Hv', 0):.2f} kgf/cm2 (Adm: {datos.get('adm_hv', 0):.0f})", fill=True)
    crear_fila_tabla(pdf, "Flecha Vertical Elastica", f"{datos.get('f_calc_cm', 0):.2f} cm (Limite: {datos.get('f_adm_cm', 0):.2f} cm)")
    crear_fila_tabla(pdf, "Estado Final Verificacion Viga", "APROBADO" if datos.get('viga_ok', False) else "NO VERIFICA", fill=True)
    pdf.ln(3)

    # 5. TESTERAS, RUEDAS Y TRASLACION
    subtitulo("5. TESTERAS Y TREN DE TRASLACION (EJE X)")
    crear_fila_tabla(pdf, "Batalla de Ruedas Adoptada (at)", f"{datos.get('batalla_at', 0):.0f}", "mm (Relacion L/7 - L/6)", fill=True)
    crear_fila_tabla(pdf, "Reaccion Maxima Testera A / Minima Testera B", f"{datos.get('R_max_test', 0):.2f} t / {datos.get('R_min_test', 0):.2f} t")
    crear_fila_tabla(pdf, "Carga Maxima por Rueda (Pr)", f"{datos.get('Pr_ton', 0):.2f}", "t", fill=True)
    crear_fila_tabla(pdf, "Perfil / Seccion Testera", f"{datos.get('sec_testera', 'N/D')} (sigma = {datos.get('sigma_test', 0):.1f} kgf/cm2)")
    crear_fila_tabla(pdf, "Ruedas de Traslacion (DIN 15070)", f"Ø {datos.get('d_rueda', 0)} mm | Riel: {datos.get('riel', 'N/D')}", fill=True)
    crear_fila_tabla(pdf, "Motorizacion Traslacion (Bilateral)", f"2x {datos.get('pot_trasl_kw', 0):.2f} kW | i = {datos.get('i_trasl', 0):.1f}:1")
    pdf.ln(3)

    # 6. VIGA CARRILERA
    subtitulo("6. VIGA CARRILERA DE ALMA LLENA (NAVE)")
    crear_fila_tabla(pdf, "Luz entre Columnas (Lc)", f"{datos.get('Lc_m', 0):.2f}", "m", fill=True)
    crear_fila_tabla(pdf, "Perfil / Seccion Carrilera", datos.get('sec_carrilera', 'N/D'))
    crear_fila_tabla(pdf, "Tension Combinada V+H", f"{datos.get('sigma_carril', 0):.1f}", "kgf/cm2", fill=True)
    crear_fila_tabla(pdf, "Flecha Vertical Calculada", f"{datos.get('fv_carril', 0):.2f} mm (Adm: {datos.get('fv_adm_carril', 0):.2f} mm)")
    crear_fila_tabla(pdf, "Estado Final Carrilera", "APROBADO" if datos.get('carril_ok', False) else "NO VERIFICA", fill=True)

    return pdf.output()