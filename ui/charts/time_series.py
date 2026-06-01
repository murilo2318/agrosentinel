"""
ui/charts/time_series.py
Gráfico de série temporal interativo e reutilizável.
Invocado em features/analise (risco) e features/relatorio (resumo).
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import streamlit as st


_THRESHOLD_COLORS = {
    "Crítico":  "#C1121F",
    "Alto":     "#E76F51",
    "Moderado": "#F4A261",
    "Baixo":    "#52B788",
}

_STATE_COLORS = px.colors.qualitative.Set2


def render_risk_timeseries(
    fire_df: pd.DataFrame,
    states: list[str],
    thresholds: dict[str, float] | None = None,
    height: int = 360,
    title: str = "Focos de queimada — série temporal",
):
    """
    Série temporal de focos de queimada por estado.
    Suporta múltiplos estados com cores distintas.
    Linhas de threshold coloridas semanticamente.

    Args:
        fire_df: DataFrame com colunas [estado, data, focos]
        states: Lista de estados para exibir
        thresholds: Dict {label: valor} de linhas de referência
        height: Altura em pixels
        title: Título do gráfico
    """
    fig = go.Figure()

    for i, uf in enumerate(states[:8]):   # máximo 8 estados
        df_uf = fire_df[fire_df["estado"] == uf].sort_values("data")
        if df_uf.empty:
            continue

        color = _STATE_COLORS[i % len(_STATE_COLORS)]

        fig.add_trace(go.Scatter(
            x=df_uf["data"],
            y=df_uf["focos"],
            name=uf,
            mode="lines",
            line=dict(color=color, width=2),
            hovertemplate=(
                f"<b>{uf}</b><br>"
                "Data: %{x|%d/%m/%Y}<br>"
                "Focos: %{y:,.0f}<extra></extra>"
            ),
            fill="tozeroy",
            fillcolor=color.replace("rgb", "rgba").replace(")", ", 0.06)") if color.startswith("rgb") else color + "10",
        ))

    # Linhas de threshold semânticas
    if thresholds:
        for label, value in thresholds.items():
            color = _THRESHOLD_COLORS.get(label, "#8B90A0")
            fig.add_hline(
                y=value,
                line_dash="dot",
                line_color=color,
                line_width=1.5,
                annotation_text=f"  {label}",
                annotation_font_color=color,
                annotation_font_size=11,
                annotation_position="right",
            )

    _apply_timeseries_style(fig, title, height, "Focos de queimada")
    st.plotly_chart(fig, use_container_width=True)


def render_ndvi_timeseries(
    ndvi_df: pd.DataFrame,
    states: list[str],
    height: int = 300,
    title: str = "NDVI — índice de vegetação",
):
    """Série temporal de NDVI com banda de referência."""
    fig = go.Figure()

    # Banda de referência NDVI saudável
    fig.add_hrect(
        y0=0.6, y1=1.0,
        fillcolor="#2D6A4F",
        opacity=0.08,
        line_width=0,
        annotation_text="Vegetação saudável",
        annotation_font_color="#52B788",
        annotation_font_size=10,
        annotation_position="top right",
    )
    fig.add_hrect(
        y0=0.0, y1=0.3,
        fillcolor="#C1121F",
        opacity=0.08,
        line_width=0,
        annotation_text="Solo exposto / estresse",
        annotation_font_color="#E76F51",
        annotation_font_size=10,
        annotation_position="bottom right",
    )

    for i, uf in enumerate(states[:8]):
        df_uf = ndvi_df[ndvi_df["estado"] == uf].sort_values("data")
        if df_uf.empty:
            continue
        color = _STATE_COLORS[i % len(_STATE_COLORS)]
        fig.add_trace(go.Scatter(
            x=df_uf["data"],
            y=df_uf["ndvi"],
            name=uf,
            mode="lines+markers",
            line=dict(color=color, width=2),
            marker=dict(size=5),
            hovertemplate=(
                f"<b>{uf}</b><br>"
                "Data: %{x|%d/%m/%Y}<br>"
                "NDVI: %{y:.3f}<extra></extra>"
            ),
        ))

    _apply_timeseries_style(fig, title, height, "NDVI")
    fig.update_yaxes(range=[0, 1])
    st.plotly_chart(fig, use_container_width=True)


def _apply_timeseries_style(fig: go.Figure, title: str, height: int, y_label: str):
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color="#8B90A0")),
        height=height,
        margin=dict(l=10, r=80, t=50, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(26,29,39,0.6)",
        font=dict(color="#E8EAF0", family="Inter, sans-serif"),
        legend=dict(
            bgcolor="rgba(26,29,39,0.8)",
            bordercolor="#2A2E40",
            borderwidth=1,
            font=dict(size=11),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
        ),
        xaxis=dict(
            gridcolor="#1E2130",
            showgrid=True,
            tickfont=dict(size=11, color="#8B90A0"),
            tickformat="%d/%m",
        ),
        yaxis=dict(
            title=y_label,
            gridcolor="#1E2130",
            showgrid=True,
            tickfont=dict(size=11, color="#8B90A0"),
            title_font=dict(size=12, color="#8B90A0"),
        ),
        hovermode="x unified",
    )
