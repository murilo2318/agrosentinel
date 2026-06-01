"""
ui/charts/plotly_map.py
Mapa coroplético interativo do Brasil por estado.
Reutilizado em panorama (risco) e análise (NDVI).
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import json


# GeoJSON simplificado dos estados brasileiros (via cdn)
_GEOJSON_URL = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"

@st.cache_data(show_spinner=False)
def _load_geojson() -> dict:
    """Carrega GeoJSON dos estados brasileiros com cache."""
    import urllib.request
    try:
        with urllib.request.urlopen(_GEOJSON_URL, timeout=5) as r:
            return json.loads(r.read())
    except Exception:
        return None


def render_choropleth_map(
    df: pd.DataFrame,
    value_col: str,
    state_col: str = "estado",
    color_scale: list | None = None,
    title: str = "",
    hover_cols: list[str] | None = None,
    range_color: tuple = (0, 1),
    height: int = 480,
    labels: dict | None = None,
):
    """
    Mapa coroplético interativo com hover rico.
    Fallback para mapa de bolhas se GeoJSON não carregar.

    Args:
        df: DataFrame com dados por estado
        value_col: Coluna com valor para colorir o mapa
        state_col: Coluna com sigla do estado
        color_scale: Escala de cores Plotly
        title: Título do mapa
        hover_cols: Colunas extras para tooltip
        range_color: Range mínimo e máximo da escala
        height: Altura em pixels
        labels: Dict de renomeação de colunas para hover
    """
    if color_scale is None:
        color_scale = [
            [0.0,  "#2D6A4F"],
            [0.25, "#52B788"],
            [0.50, "#F4A261"],
            [0.75, "#E76F51"],
            [1.0,  "#C1121F"],
        ]

    if labels is None:
        labels = {}

    hover_data = {value_col: ":.3f"}
    if hover_cols:
        for col in hover_cols:
            if col in df.columns:
                hover_data[col] = True

    geojson = _load_geojson()

    if geojson:
        # Tenta mapear as siglas do GeoJSON
        # O GeoJSON do click_that_hood usa "sigla" como propriedade
        fig = px.choropleth(
            df,
            geojson=geojson,
            locations=state_col,
            featureidkey="properties.sigla",
            color=value_col,
            color_continuous_scale=color_scale,
            range_color=range_color,
            hover_data=hover_data,
            labels={**labels, value_col: labels.get(value_col, value_col)},
            title=title,
        )
        fig.update_geos(
            fitbounds="locations",
            visible=False,
            bgcolor="rgba(0,0,0,0)",
        )
    else:
        # Fallback: mapa de bolhas usando lat/lon
        fig = px.scatter_geo(
            df,
            lat="lat",
            lon="lon",
            color=value_col,
            size=value_col,
            hover_name=state_col,
            color_continuous_scale=color_scale,
            range_color=range_color,
            hover_data=hover_data,
            title=title,
            labels=labels,
        )
        fig.update_geos(
            scope="south america",
            showland=True,
            landcolor="#1A1D27",
            showocean=True,
            oceancolor="#0F1117",
            showcoastlines=True,
            coastlinecolor="#2A2E40",
            showborder=True,
            bgcolor="rgba(0,0,0,0)",
        )

    _apply_map_style(fig, height)
    st.plotly_chart(fig, use_container_width=True)


def _apply_map_style(fig: go.Figure, height: int):
    fig.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=40, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        geo_bgcolor="rgba(0,0,0,0)",
        font={"color": "#E8EAF0", "family": "Inter, sans-serif"},
        title_font={"size": 14, "color": "#8B90A0"},
        coloraxis_colorbar=dict(
            tickfont={"color": "#8B90A0", "size": 10},
            title_font={"color": "#8B90A0", "size": 11},
            bgcolor="rgba(26,29,39,0.8)",
            bordercolor="#2A2E40",
            borderwidth=1,
            len=0.7,
        ),
    )
