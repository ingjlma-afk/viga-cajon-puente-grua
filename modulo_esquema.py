# modulo_esquema.py
import plotly.graph_objects as go

def generar_diagrama_cinematico(D_tambor_mm: float, L_tambor_mm: float, D_polea_mm: float, num_ramales: int = 4, d_cable_mm: float = 16.0, tipo_polipasto: str = "Gemelo", *args, **kwargs):
    fig = go.Figure()

    # Dimensiones visuales relativas
    w_tambor = max(3.5, min(6.0, L_tambor_mm / 300.0))
    h_tambor = max(1.2, min(2.4, D_tambor_mm / 300.0))

    # 1. FRENO ELECTROMAGNÉTICO (Eje Veloz)
    fig.add_trace(go.Scatter(
        x=[0.0, 0.7, 0.7, 0.0, 0.0],
        y=[0.9, 0.9, -0.9, -0.9, 0.9],
        fill="toself", fillcolor="#dc2626", line=dict(color="#f87171", width=2),
        name="[1] Freno de Retención",
        hoverinfo="text",
        text="<b>[Ítem 1] Freno Electromagnético</b><br>Eje Veloz del Motor"
    ))

    # 2. MOTOR ELÉCTRICO
    fig.add_trace(go.Scatter(
        x=[0.7, 2.5, 2.5, 0.7, 0.7],
        y=[1.2, 1.2, -1.2, -1.2, 1.2],
        fill="toself", fillcolor="#2563eb", line=dict(color="#60a5fa", width=2),
        name="[2] Motor Eléctrico",
        hoverinfo="text",
        text="<b>[Ítem 2] Motor Eléctrico Principal</b><br>1500 rpm"
    ))

    # Eje veloz intermedio
    fig.add_trace(go.Scatter(
        x=[2.5, 2.9, 2.9, 2.5, 2.5],
        y=[0.3, 0.3, -0.3, -0.3, 0.3],
        fill="toself", fillcolor="#94a3b8", line=dict(color="#cbd5e1", width=1),
        showlegend=False, hoverinfo="none"
    ))

    # 3. REDUCTOR LENTAX
    fig.add_trace(go.Scatter(
        x=[2.9, 5.0, 5.0, 2.9, 2.9],
        y=[1.6, 1.6, -1.6, -1.6, 1.6],
        fill="toself", fillcolor="#d97706", line=dict(color="#fbbf24", width=2),
        name="[3] Reductor LENTAX",
        hoverinfo="text",
        text="<b>[Ítem 3] Reductor LENTAX</b><br>Ejes Paralelos"
    ))

    # 4. ACOPLAMIENTO DE TAMBOR
    fig.add_trace(go.Scatter(
        x=[5.0, 5.5, 5.5, 5.0, 5.0],
        y=[0.5, 0.5, -0.5, -0.5, 0.5],
        fill="toself", fillcolor="#64748b", line=dict(color="#94a3b8", width=1),
        name="[4] Acoplamiento",
        hoverinfo="text",
        text="<b>[Ítem 4] Acoplamiento</b><br>Eje lento al tambor"
    ))

    # 5. TAMBOR DE ARROLLAMIENTO
    x_t0 = 5.5
    x_t1 = x_t0 + w_tambor
    fig.add_trace(go.Scatter(
        x=[x_t0, x_t1, x_t1, x_t0, x_t0],
        y=[h_tambor, h_tambor, -h_tambor, -h_tambor, h_tambor],
        fill="toself", fillcolor="#1e293b", line=dict(color="#38bdf8", width=2),
        name="[5] Tambor Acanalado",
        hoverinfo="text",
        text=f"<b>[Ítem 5] Tambor Ranurado ({tipo_polipasto})</b><br>Ø{D_tambor_mm:.1f} mm x L{L_tambor_mm:.1f} mm"
    ))

    # 6. CABLES DESCENDENTES
    x_c1 = x_t0 + 0.8
    x_c2 = x_t1 - 0.8
    y_pasteca_sup = -4.5
    
    fig.add_trace(go.Scatter(
        x=[x_c1, x_c1], y=[-h_tambor, y_pasteca_sup],
        mode="lines", line=dict(color="#94a3b8", width=3, dash="dash"),
        name="[6] Ramales de Cable",
        hoverinfo="text",
        text=f"<b>[Ítem 6] Cables ({num_ramales} ramales)</b>"
    ))
    fig.add_trace(go.Scatter(
        x=[x_c2, x_c2], y=[-h_tambor, y_pasteca_sup],
        mode="lines", line=dict(color="#94a3b8", width=3, dash="dash"),
        showlegend=False, hoverinfo="none"
    ))

    # 7. PASTECA INFERIOR Y GANCHO
    x_p0 = (x_c1 + x_c2) / 2.0
    w_p = (x_c2 - x_c1) + 0.8
    fig.add_trace(go.Scatter(
        x=[x_p0 - w_p/2, x_p0 + w_p/2, x_p0 + w_p/2, x_p0 - w_p/2, x_p0 - w_p/2],
        y=[y_pasteca_sup, y_pasteca_sup, y_pasteca_sup - 1.2, y_pasteca_sup - 1.2, y_pasteca_sup],
        fill="toself", fillcolor="#eab308", line=dict(color="#ca8a04", width=2),
        name="[7] Pasteca y Gancho",
        hoverinfo="text",
        text=f"<b>[Ítem 7] Pasteca</b><br>Poleas Ø{D_polea_mm:.1f} mm"
    ))

    # Gancho
    fig.add_trace(go.Scatter(
        x=[x_p0, x_p0, x_p0 - 0.3, x_p0, x_p0 + 0.3],
        y=[y_pasteca_sup - 1.2, y_pasteca_sup - 1.9, y_pasteca_sup - 2.3, y_pasteca_sup - 2.5, y_pasteca_sup - 2.0],
        mode="lines", line=dict(color="#f8fafc", width=4),
        showlegend=False, hoverinfo="none"
    ))

    # Anotaciones
    anotaciones = [
        dict(x=0.35, y=0.0, text="<b>[1]<br>FRENO</b>", showarrow=False, font=dict(color="#ffffff", size=10)),
        dict(x=1.60, y=0.0, text="<b>[2]<br>MOTOR</b>", showarrow=False, font=dict(color="#ffffff", size=12)),
        dict(x=3.95, y=0.0, text="<b>[3]<br>REDUCTOR</b>", showarrow=False, font=dict(color="#ffffff", size=12)),
        dict(x=(x_t0 + x_t1)/2.0, y=0.0, text="<b>[5] TAMBOR</b>", showarrow=False, font=dict(color="#38bdf8", size=12)),
        dict(x=x_p0, y=y_pasteca_sup - 0.6, text="<b>[7] PASTECA</b>", showarrow=False, font=dict(color="#0f172a", size=11)),
    ]

    fig.update_layout(
        paper_bgcolor="#0b111e",
        plot_bgcolor="#070d18",
        margin=dict(l=20, r=20, t=30, b=20),
        height=480,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            font=dict(color="#cbd5e1", size=11)
        ),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.5, x_t1 + 1.0]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, scaleanchor="x", scaleratio=1, range=[y_pasteca_sup - 3.2, 2.5]),
        annotations=anotaciones
    )

    return fig