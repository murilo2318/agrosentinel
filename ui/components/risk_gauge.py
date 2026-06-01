"""
ui/components/risk_gauge.py
Componente reutilizável de gauge velocímetro de risco.
Invocado em panorama (gauge nacional) e analise (gauge por estado).
"""
import plotly.graph_objects as go
import streamlit as st


def render_risk_gauge(
    score: float,
    title: str = "Índice de Risco",
    height: int = 220,
    show_label: bool = True,
):
    """
    Renderiza gauge velocímetro com escala de risco 0-1.
    Cores semânticas: verde → amarelo → laranja → vermelho.

    Args:
        score: Valor entre 0 e 1
        title: Título exibido abaixo do gauge
        height: Altura em pixels
        show_label: Se mostra o rótulo de classe textual
    """
    score = float(max(0, min(1, score)))

    if score < 0.25:
        risk_label, bar_color = "Baixo",    "#2D6A4F"
    elif score < 0.50:
        risk_label, bar_color = "Moderado", "#F4A261"
    elif score < 0.75:
        risk_label, bar_color = "Alto",     "#E76F51"
    else:
        risk_label, bar_color = "Crítico",  "#C1121F"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=round(score * 100, 1),
        number={
            "suffix": "%",
            "font": {"size": 26, "color": "#E8EAF0"},
        },
        title={
            "text": f"{title}<br><span style='font-size:13px; color:#8B90A0'>{risk_label if show_label else ''}</span>",
            "font": {"size": 14, "color": "#E8EAF0"},
        },
        gauge={
            "axis": {
                "range": [0, 100],
                "tickwidth": 1,
                "tickcolor": "#2A2E40",
                "tickfont": {"size": 10, "color": "#8B90A0"},
                "nticks": 5,
            },
            "bar": {"color": bar_color, "thickness": 0.28},
            "bgcolor": "#1A1D27",
            "borderwidth": 0,
            "steps": [
                {"range": [0,  25],  "color": "#0D2B1F"},
                {"range": [25, 50],  "color": "#2D1E0A"},
                {"range": [50, 75],  "color": "#2D1A0A"},
                {"range": [75, 100], "color": "#2D0A0A"},
            ],
            "threshold": {
                "line": {"color": "#E8EAF0", "width": 2},
                "thickness": 0.75,
                "value": score * 100,
            },
        },
    ))

    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, sans-serif"},
    )

    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
