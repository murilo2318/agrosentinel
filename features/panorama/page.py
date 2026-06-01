"""
features/panorama/page.py
Tela de panorama nacional — visão geral de risco agroclimático.
Primeira tela do storytelling: do panorama ao detalhe.
"""
import streamlit as st
import plotly.express as px
import pandas as pd

from pipelines.risk_pipeline    import build_risk_dataframe
from pipelines.alert_pipeline   import generate_alerts
from ui.components.kpi_card     import render_kpi_card, render_risk_badge, render_skeleton_cards
from ui.components.risk_gauge   import render_risk_gauge
from ui.charts.plotly_map       import render_choropleth_map
from state.session              import get, set
from state.alerts               import count_pending


def render(filters: dict):
    """Renderiza a feature de Panorama Nacional."""
    date_start = filters["date_start"]
    date_end   = filters["date_end"]
    states     = filters["states"]
    risk_min   = filters["risk_min"]

    st.markdown(
        '<div class="section-title">🌎 Panorama Nacional — Risco Agroclimático</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        f"Período: {date_start.strftime('%d/%m/%Y')} → {date_end.strftime('%d/%m/%Y')} "
        f"· {len(states)} estado(s) analisado(s) · Modelo: RandomForest"
    )

    # Carregamento com skeleton + spinner
    if get("data_risk") is None:
        render_skeleton_cards(4)
        with st.spinner("Calculando índice de risco com modelo de ML..."):
            risk_df = build_risk_dataframe(date_start, date_end, states)
            alerts  = generate_alerts(risk_df, threshold_class=1)
            set("data_risk", risk_df)
            set("data_alerts", alerts)
            set("data_loaded", True)
    else:
        risk_df = get("data_risk")
        alerts  = get("data_alerts") or []

    # Aplica filtro de risco mínimo para exibição
    display_df = risk_df[risk_df["risk_score"] >= risk_min].copy()

    if display_df.empty:
        st.warning("Nenhum estado acima do threshold de risco selecionado.")
        return

    # ── KPI Cards ──────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)

    n_critico  = int((risk_df["risk_class"] == 3).sum())
    n_alto     = int((risk_df["risk_class"] == 2).sum())
    score_med  = float(risk_df["risk_score"].mean())
    total_focos = int(risk_df["total_focos"].sum()) if "total_focos" in risk_df.columns else 0
    n_pending  = count_pending(alerts)

    with col1:
        render_kpi_card(
            label="Estados em risco crítico",
            value=str(n_critico),
            delta=f"{n_critico} requerem ação imediata" if n_critico > 0 else "Nenhum estado crítico",
            delta_direction="up" if n_critico > 0 else "down",
            color_accent="#C1121F",
            icon="🔴",
            help_text="Estados com score de risco > 0.75",
        )

    with col2:
        render_kpi_card(
            label="Estados em risco alto",
            value=str(n_alto),
            delta=f"{n_alto} em atenção elevada",
            delta_direction="up" if n_alto > 2 else "neu",
            color_accent="#E76F51",
            icon="🟠",
        )

    with col3:
        render_kpi_card(
            label="Score médio de risco",
            value=f"{score_med:.0%}",
            delta="Modelo RandomForest",
            delta_direction="neu",
            color_accent="#F4A261",
            icon="📊",
            help_text="Média ponderada do índice de risco calculado pelo modelo de ML",
        )

    with col4:
        render_kpi_card(
            label="Alertas pendentes",
            value=str(n_pending),
            delta="Aguardando revisão humana" if n_pending > 0 else "Todos revisados",
            delta_direction="up" if n_pending > 0 else "down",
            color_accent="#52B788" if n_pending == 0 else "#F4A261",
            icon="⚡",
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Mapa + Gauge lado a lado ───────────────────────────────────────────
    map_col, gauge_col = st.columns([3, 1])

    with map_col:
        st.markdown('<p class="section-title">Índice de risco por estado</p>', unsafe_allow_html=True)
        render_choropleth_map(
            df=display_df,
            value_col="risk_score",
            state_col="estado",
            title="",
            hover_cols=["risk_label", "total_focos", "temperatura", "umidade", "ndvi"],
            range_color=(0, 1),
            labels={
                "risk_score":    "Score de risco",
                "risk_label":    "Nível",
                "total_focos":   "Focos (período)",
                "temperatura":   "Temperatura (°C)",
                "umidade":       "Umidade (%)",
                "ndvi":          "NDVI",
            },
            height=440,
        )

    with gauge_col:
        st.markdown('<p class="section-title">Risco nacional</p>', unsafe_allow_html=True)
        render_risk_gauge(
            score=score_med,
            title="Média nacional",
            height=230,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        # Top 3 estados mais críticos
        st.markdown(
            '<div class="section-title" style="font-size:11px;">📍 Estados críticos</div>',
            unsafe_allow_html=True,
        )
        top3 = risk_df.nlargest(3, "risk_score")[["estado", "risk_label", "risk_score"]]
        for _, row in top3.iterrows():
            badge = render_risk_badge(row["risk_label"])
            st.markdown(
                f"""
                <div style="
                    display:flex; justify-content:space-between;
                    align-items:center; padding:6px 0;
                    border-bottom:1px solid #2A2E40;
                    font-size:13px; color:#E8EAF0;
                ">
                    <span><b>{row['estado']}</b></span>
                    {badge}
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Scatter: NDVI × Score de Risco ────────────────────────────────────
    st.markdown('<p class="section-title">Relação NDVI × Risco (todos os estados)</p>', unsafe_allow_html=True)

    if "ndvi" in risk_df.columns and "temperatura" in risk_df.columns:
        scatter_fig = px.scatter(
            risk_df,
            x="ndvi",
            y="risk_score",
            color="risk_label",
            size="total_focos" if "total_focos" in risk_df.columns else None,
            hover_name="estado",
            color_discrete_map={
                "Baixo":    "#2D6A4F",
                "Moderado": "#F4A261",
                "Alto":     "#E76F51",
                "Crítico":  "#C1121F",
            },
            labels={
                "ndvi":       "NDVI (índice de vegetação)",
                "risk_score": "Score de risco",
                "risk_label": "Nível de risco",
                "total_focos":"Focos de queimada",
            },
            category_orders={"risk_label": ["Baixo", "Moderado", "Alto", "Crítico"]},
            height=320,
        )
        scatter_fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(26,29,39,0.6)",
            font=dict(color="#E8EAF0", family="Inter, sans-serif"),
            margin=dict(l=10, r=10, t=20, b=40),
            xaxis=dict(gridcolor="#1E2130", tickfont=dict(color="#8B90A0")),
            yaxis=dict(gridcolor="#1E2130", tickfont=dict(color="#8B90A0")),
            legend=dict(
                bgcolor="rgba(26,29,39,0.8)",
                bordercolor="#2A2E40",
                borderwidth=1,
                font=dict(size=11),
            ),
        )
        st.plotly_chart(scatter_fig, use_container_width=True)

    # ── Tabela de estados ─────────────────────────────────────────────────
    with st.expander("📋 Ver tabela completa de estados", expanded=False):
        table_cols = ["estado", "bioma", "risk_label", "risk_score", "total_focos", "temperatura", "umidade", "ndvi"]
        existing  = [c for c in table_cols if c in risk_df.columns]
        table_df  = risk_df[existing].sort_values("risk_score", ascending=False).copy()
        table_df["risk_score"] = table_df["risk_score"].map("{:.1%}".format)
        if "temperatura" in table_df.columns:
            table_df["temperatura"] = table_df["temperatura"].map("{:.1f}°C".format)
        if "umidade" in table_df.columns:
            table_df["umidade"] = table_df["umidade"].map("{:.0f}%".format)
        st.dataframe(table_df, use_container_width=True, hide_index=True)
