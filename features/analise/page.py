"""
features/analise/page.py
Análise temporal aprofundada: séries de focos, NDVI e clima.
Segunda camada do storytelling: do panorama ao detalhe por estado.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from providers.fire_provider    import get_fire_data
from providers.climate_provider import get_climate_data
from pipelines.ndvi_pipeline    import get_ndvi_timeseries, get_ndvi_trend
from models.risk_model          import get_feature_importances
from ui.components.kpi_card     import render_kpi_card, render_skeleton_cards
from ui.components.risk_gauge   import render_risk_gauge
from ui.charts.time_series      import render_risk_timeseries, render_ndvi_timeseries
from state.session              import get


def render(filters: dict):
    """Renderiza a feature de Análise Temporal."""
    date_start = filters["date_start"]
    date_end   = filters["date_end"]
    states     = filters["states"]

    st.markdown(
        '<div class="section-title">📈 Análise Temporal — Dados por Estado</div>',
        unsafe_allow_html=True,
    )

    # Seletor de estado para detalhe
    risk_df = get("data_risk")
    if risk_df is not None:
        state_options = list(risk_df.sort_values("risk_score", ascending=False)["estado"])
    else:
        state_options = states

    col_sel, col_info = st.columns([2, 3])
    with col_sel:
        selected_detail = st.selectbox(
            "Estado para análise detalhada",
            options=state_options,
            key="analise_state_sel",
        )
    with col_info:
        if risk_df is not None and selected_detail:
            row = risk_df[risk_df["estado"] == selected_detail]
            if not row.empty:
                row = row.iloc[0]
                st.markdown(
                    f"""
                    <div style="
                        background:#1A1D27; border:1px solid #2A2E40;
                        border-radius:8px; padding:10px 16px; margin-top:6px;
                        font-size:13px; color:#C8CAD4;
                    ">
                        <b>{selected_detail}</b> &nbsp;·&nbsp;
                        Bioma: {row.get('bioma','')} &nbsp;·&nbsp;
                        Risco: <b style="color:{'#C1121F' if row['risk_score']>0.75 else '#E76F51' if row['risk_score']>0.5 else '#F4A261' if row['risk_score']>0.25 else '#52B788'}">
                        {row['risk_label']} ({row['risk_score']:.1%})</b>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── KPI cards do estado selecionado ────────────────────────────────────
    if risk_df is not None and selected_detail:
        row = risk_df[risk_df["estado"] == selected_detail]
        if not row.empty:
            row = row.iloc[0]
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                render_kpi_card(
                    "Score de risco (ML)",
                    f"{row['risk_score']:.1%}",
                    color_accent="#C1121F" if row["risk_score"] > 0.75 else "#E76F51",
                    icon="🤖",
                    help_text="Probabilidade de risco alto/crítico calculada pelo RandomForest",
                )
            with col2:
                render_kpi_card(
                    "Temperatura média",
                    f"{row.get('temperatura', 0):.1f}°C",
                    color_accent="#E76F51",
                    icon="🌡️",
                )
            with col3:
                render_kpi_card(
                    "NDVI médio",
                    f"{row.get('ndvi', 0):.3f}",
                    delta="↓ Abaixo do ideal" if row.get("ndvi", 0) < 0.4 else "→ Normal",
                    delta_direction="up" if row.get("ndvi", 0) < 0.4 else "neu",
                    color_accent="#52B788",
                    icon="🌿",
                )
            with col4:
                render_kpi_card(
                    "Focos (período)",
                    f"{int(row.get('total_focos', 0)):,}",
                    color_accent="#F4A261",
                    icon="🔥",
                )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Tabs internas de análise ───────────────────────────────────────────
    tab_fogo, tab_ndvi, tab_clima, tab_modelo = st.tabs([
        "🔥 Focos de queimada",
        "🌿 Índice NDVI",
        "🌡️ Clima",
        "🤖 Modelo ML",
    ])

    with tab_fogo:
        with st.spinner("Carregando série temporal de focos..."):
            fire_df = get_fire_data(date_start, date_end, states)

        render_risk_timeseries(
            fire_df=fire_df,
            states=states[:6],
            thresholds={
                "Crítico":  fire_df["focos"].quantile(0.90),
                "Alto":     fire_df["focos"].quantile(0.75),
                "Moderado": fire_df["focos"].quantile(0.50),
            },
            title="Focos de queimada diários por estado",
            height=380,
        )

        # Gauge do estado selecionado
        if risk_df is not None and selected_detail:
            row = risk_df[risk_df["estado"] == selected_detail]
            if not row.empty:
                gcol1, gcol2 = st.columns([1, 2])
                with gcol1:
                    render_risk_gauge(
                        score=float(row.iloc[0]["risk_score"]),
                        title=f"Risco — {selected_detail}",
                        height=200,
                    )
                with gcol2:
                    # Bar chart de focos por estado (top 10)
                    top_fire = (
                        fire_df.groupby("estado")["focos"]
                        .sum()
                        .reset_index()
                        .nlargest(10, "focos")
                    )
                    bar_fig = px.bar(
                        top_fire,
                        x="estado", y="focos",
                        color="focos",
                        color_continuous_scale=[
                            [0, "#2D6A4F"], [0.5, "#E76F51"], [1, "#C1121F"]
                        ],
                        labels={"estado": "Estado", "focos": "Total de focos"},
                        height=200,
                        title="Top 10 estados — total de focos",
                    )
                    bar_fig.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(26,29,39,0.6)",
                        font=dict(color="#E8EAF0"),
                        margin=dict(l=10, r=10, t=40, b=10),
                        showlegend=False,
                        coloraxis_showscale=False,
                        xaxis=dict(gridcolor="#1E2130", tickfont=dict(color="#8B90A0")),
                        yaxis=dict(gridcolor="#1E2130", tickfont=dict(color="#8B90A0")),
                    )
                    st.plotly_chart(bar_fig, use_container_width=True)

    with tab_ndvi:
        with st.spinner("Carregando dados NDVI..."):
            ndvi_df   = get_ndvi_timeseries(date_start, date_end, states)
            ndvi_trend = get_ndvi_trend(date_start, date_end, states)

        render_ndvi_timeseries(
            ndvi_df=ndvi_df,
            states=states[:6],
            title="NDVI semanal por estado (Sentinel-2 simulado)",
            height=340,
        )

        # Tabela de tendências
        if not ndvi_trend.empty:
            st.markdown('<div class="section-title">📉 Tendência de vegetação no período</div>', unsafe_allow_html=True)
            trend_disp = ndvi_trend.copy()
            trend_disp["ndvi_slope"] = trend_disp["ndvi_slope"].map("{:+.4f}/mês".format)
            st.dataframe(
                trend_disp[["estado", "tendencia", "ndvi_slope"]].rename(columns={
                    "estado": "Estado",
                    "tendencia": "Tendência",
                    "ndvi_slope": "Variação",
                }),
                use_container_width=True,
                hide_index=True,
            )

    with tab_clima:
        with st.spinner("Carregando dados climáticos..."):
            climate_df = get_climate_data(date_start, date_end, states)

        _render_climate_tab(climate_df, states)

    with tab_modelo:
        _render_model_tab()


def _render_climate_tab(climate_df: pd.DataFrame, states: list[str]):
    """Visualizações climáticas."""
    # Temperatura e umidade para o estado selecionado
    col_c1, col_c2 = st.columns(2)

    state_df = climate_df[climate_df["estado"].isin(states[:4])].copy()
    state_df["data"] = pd.to_datetime(state_df["data"])

    with col_c1:
        temp_fig = px.line(
            state_df, x="data", y="temperatura", color="estado",
            title="Temperatura média (°C)",
            labels={"temperatura": "°C", "data": "Data", "estado": "Estado"},
            height=280,
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        temp_fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(26,29,39,0.6)",
            font=dict(color="#E8EAF0"),
            margin=dict(l=10, r=10, t=40, b=10),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
            xaxis=dict(gridcolor="#1E2130", tickfont=dict(color="#8B90A0")),
            yaxis=dict(gridcolor="#1E2130", tickfont=dict(color="#8B90A0")),
        )
        st.plotly_chart(temp_fig, use_container_width=True)

    with col_c2:
        hum_fig = px.line(
            state_df, x="data", y="umidade", color="estado",
            title="Umidade relativa (%)",
            labels={"umidade": "%", "data": "Data", "estado": "Estado"},
            height=280,
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        hum_fig.add_hrect(
            y0=0, y1=30,
            fillcolor="#C1121F", opacity=0.08,
            annotation_text="Umidade crítica (<30%)",
            annotation_font_color="#E76F51",
            annotation_font_size=10,
        )
        hum_fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(26,29,39,0.6)",
            font=dict(color="#E8EAF0"),
            margin=dict(l=10, r=10, t=40, b=10),
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
            xaxis=dict(gridcolor="#1E2130", tickfont=dict(color="#8B90A0")),
            yaxis=dict(gridcolor="#1E2130", tickfont=dict(color="#8B90A0")),
        )
        st.plotly_chart(hum_fig, use_container_width=True)


def _render_model_tab():
    """Explica o modelo de ML com importância das features."""
    st.markdown(
        """
        <div style="background:#1A1D27; border:1px solid #2A2E40; border-radius:10px;
             padding:16px 20px; margin-bottom:16px;">
            <div style="font-size:14px; font-weight:600; color:#E8EAF0; margin-bottom:8px;">
                🤖 RandomForestClassifier — Modelo de Risco Agroclimático
            </div>
            <div style="font-size:13px; color:#8B90A0; line-height:1.7;">
                Treinado com 4.000 amostras sintéticas baseadas em padrões históricos do INPE e INMET.<br>
                <b style="color:#C8CAD4;">Features:</b> focos normalizados, temperatura, umidade, precipitação, vento, NDVI e mês.<br>
                <b style="color:#C8CAD4;">Saída:</b> probabilidade de risco alto/crítico (0–1) por estado.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Importâncias das features
    importances = get_feature_importances()
    imp_fig = px.bar(
        importances,
        x="importance",
        y="feature",
        orientation="h",
        color="importance",
        color_continuous_scale=[[0, "#2D6A4F"], [0.5, "#F4A261"], [1, "#C1121F"]],
        labels={"importance": "Importância", "feature": "Feature"},
        title="Importância das features no modelo",
        height=320,
    )
    imp_fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(26,29,39,0.6)",
        font=dict(color="#E8EAF0"),
        margin=dict(l=10, r=10, t=40, b=10),
        coloraxis_showscale=False,
        yaxis=dict(gridcolor="#1E2130", tickfont=dict(color="#C8CAD4", size=12)),
        xaxis=dict(gridcolor="#1E2130", tickfont=dict(color="#8B90A0")),
    )
    st.plotly_chart(imp_fig, use_container_width=True)

    st.info(
        "ℹ️ O modelo é treinado automaticamente na inicialização do app e "
        "cacheado com `@st.cache_resource`. Nenhum re-treinamento ocorre durante a sessão."
    )
