# modulo_esquema.py
"""
Módulo para la generación gráfica del esquema kinemático y componentes del carro de elevación.
Visualización técnica interactiva con Plotly para alumnos.
"""

import plotly.graph_objects as go

def generar_diagrama_cinematico(D_tambor_mm: float, L_tambor_mm: float, D_polea_mm: float, num_ramales: int = 4, tipo_polipasto: str = "Gemelo"):
    """
    Genera un croquis técnico en 2D/3D con la distribución espacial de componentes.
    """
    fig = go.Figure()

    # Coordenadas relativas de disposición de izquierda a derecha
    # 1. FRENO
    fig.add_trace(go.Scatter(
        x=[0, 0.8, 0.8, 0, 0], y=[1, 1, -1, -1, 1],
        fill="toself", fillcolor="crimson", opacity=0.8,
        name="1. Freno de Seguridad", text="[1] Freno Electromagnético (Eje Veloz)", hoverinfo="text"
    ))

    # 2. MOTOR
    fig.add_trace(go.Scatter(
        x=[0.8, 2.5, 2.5, 0.8, 0.8], y=[1.3, 1.3, -1.3, -1.3, 1.3],
        fill="toself", fillcolor="royalblue", opacity=0.8,
        name="2. Motor Eléctrico", text="[2] Motor Eléctrico de Elevación", hoverinfo="text"
    ))

    # 3. REDUCTOR
    fig.add_trace(go.Scatter(
        x=[2.5, 4.2, 4.2, 2.5, 2.5], y=[1.8, 1.8, -1.8, -1.8, 1.8],
        fill="toself", fillcolor="darkorange", opacity=0.8,
        name="3. Reductor", text="[3] Reductor de Velocidad (i_reductor)", hoverinfo="text"
    ))

    # 4. ACOPLAMIENTO / EJE LENTO
    fig.add_trace(go.Scatter(
        x=[4.2, 4.8, 4.8, 4.2, 4.2], y=[0.5, 0.5, -0.5, -0.5, 0.5],
        fill="toself", fillcolor="gray", opacity=0.9,
        name="4. Acoplamiento", text="[4] Acoplamiento de Eje Lento", hoverinfo="text"
    ))

    # 5. TAMBOR ACANALADO
    fig.add_trace(go.Scatter(
        x=[4.8, 8.5, 8.5, 4.8, 4.8], y=[1.5, 1.5, -1.5, -1.5, 1.5],
        fill="toself", fillcolor="darkslategrey", opacity=0.85,
        name="5. Tambor", text=f"[5] Tambor Acanalado (Ø{D_tambor_mm} mm x L{L_tambor_mm} mm)", hoverinfo="text"
    ))

    # 6. CABLES Y PASTECA (Hacia abajo)
    # Cable Ramal 1
    fig.add_trace(go.Scatter(x=[5.5, 5.5], y=[-1.5, -5.5], mode="lines+markers", line=dict(color="black", width=3, dash="dot"), name="6. Cables"))
    # Cable Ramal 2
    fig.add_trace(go.Scatter(x=[7.8, 7.8], y=[-1.5, -5.5], mode="lines+markers", line=dict(color="black", width=3, dash="dot"), showlegend=False))

    # 7. PASTECA / GANCHO
    fig.add_trace(go.Scatter(
        x=[5.0, 8.3, 8.3, 5.0, 5.0], y=[-5.5, -5.5, -7.0, -7.0, -5.5],
        fill="toself", fillcolor="gold", opacity=0.9,
        name="7. Pasteca y Gancho", text=f"[7] Pasteca (Ø Poleas: {D_polea_mm} mm)", hoverinfo="text"
    ))

    # Anotaciones numéricas e identificadores gráficos
    anotaciones = [
        dict(x=0.4, y=0, text="<b>[1] FRENO</b>", showarrow=False, font=dict(color="white", size=10)),
        dict(x=1.65, y=0, text="<b>[2] MOTOR</b>", showarrow=False, font=dict(color="white", size=12)),
        dict(x=3.35, y=0, text="<b>[3] REDUCTOR</b>", showarrow=False, font=dict(color="white", size=11)),
        dict(x=6.65, y=0, text="<b>[5] TAMBOR ACANALADO</b>", showarrow=False, font=dict(color="white", size=12)),
        dict(x=6.65, y=-6.25, text="<b>[7] PASTECA / GANCHO</b>", showarrow=False, font=dict(color="black", size=11)),
    ]

    fig.update_layout(
        title="<b>Diagrama de Distribución Cinemática y Posicionamiento de Componentes</b>",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, scaleanchor="x", scaleratio=1),
        annotations=anotaciones,
        height=450,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=True
    )

    return fig