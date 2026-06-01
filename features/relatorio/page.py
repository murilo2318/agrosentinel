"""
features/relatorio/page.py
Relatório executivo consolidado — resumo do período para exportação.
Reutiliza os mesmos componentes de KPI e gráficos das outras features.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

from state.session          import get
from state.alerts           import count_confirmed, count_pending
from ui.components.kpi_card import render_kpi_card   # componente reutilizado
from ui.charts.time_series  import render_risk_timeseries  # chart reutilizado
from providers.fire_provider import get_fire_data


def render(filters: dict):
    """Renderiza o relatório executivo consolidado."""
    date_start = filters["date_start"]
    date_end   = filters["date_end"]
    states     = filters["states"]
    culture    = filters["culture"]

    st.markdown(
        '<div class="section-title">📄 Relatório Executivo</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        f"Gerado em {date.today().strftime('%d/%m/%Y')} · "
        f"Período: {date_start.strftime('%d/%m/%Y')} a {date_end.strftime('%d/%m/%Y')}"
    )

    risk_df = get("data_risk")
    alerts  = get("data_alerts") or []

    if risk_df is None:
        st.info("⏳ Carregue os dados na aba **Panorama** primeiro.")
        return

    # ── Cabeçalho do relatório ─────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #13161F 0%, #1A1D27 100%);
            border: 1px solid #2A2E40;
            border-left: 4px solid #52B788;
            border-radius: 12px;
            padding: 20px 24px;
            margin-bottom: 20px;
        ">
            <div style="font-size:20px; font-weight:700; color:#52B788; margin-bottom:8px;">
                🌿 AgroSentinel — Relatório de Risco Agroclimático
            </div>
            <div style="font-size:13px; color:#8B90A0; line-height:1.8;">
                <b style="color:#C8CAD4;">Período analisado:</b>
                {date_start.strftime('%d/%m/%Y')} a {date_end.strftime('%d/%m/%Y')}<br>
                <b style="color:#C8CAD4;">Estados monitorados:</b>
                {', '.join(states)}<br>
                <b style="color:#C8CAD4;">Cultura de interesse:</b> {culture}<br>
                <b style="color:#C8CAD4;">Metodologia:</b>
                RandomForestClassifier · Features: focos INPE, clima Open-Meteo, NDVI Sentinel-2
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── KPI summary (componente reutilizado com parâmetros diferentes) ─────
    st.markdown('<div class="section-title">Resumo do período</div>', unsafe_allow_html=True)

    n_critico  = int((risk_df["risk_class"] == 3).sum())
    n_alto     = int((risk_df["risk_class"] == 2).sum())
    n_confirmed = count_confirmed(alerts)
    score_max   = float(risk_df["risk_score"].max())

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_kpi_card(           # mesmo componente de panorama
            "Pior nível de risco",
            risk_df.loc[risk_df["risk_score"].idxmax(), "risk_label"],
            delta=risk_df.loc[risk_df["risk_score"].idxmax(), "estado"],
            delta_direction="up" if score_max > 0.5 else "neu",
            color_accent="#C1121F",
            icon="⚠️",
        )
    with col2:
        render_kpi_card(
            "Estados críticos + altos",
            str(n_critico + n_alto),
            delta=f"de {len(states)} analisados",
            delta_direction="up" if (n_critico + n_alto) > len(states) // 3 else "neu",
            color_accent="#E76F51",
            icon="📍",
        )
    with col3:
        render_kpi_card(
            "Total de focos",
            f"{int(risk_df['total_focos'].sum()):,}" if "total_focos" in risk_df else "—",
            delta="Acumulado no período",
            delta_direction="neu",
            color_accent="#F4A261",
            icon="🔥",
        )
    with col4:
        render_kpi_card(
            "Alertas confirmados",
            str(n_confirmed),
            delta="Enviados às autoridades",
            delta_direction="down",
            color_accent="#52B788",
            icon="✅",
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Série temporal reutilizada ─────────────────────────────────────────
    st.markdown('<div class="section-title">Evolução de focos no período</div>', unsafe_allow_html=True)
    fire_df = get_fire_data(date_start, date_end, states)
    top_states = (
        risk_df.nlargest(5, "risk_score")["estado"].tolist()
        if len(states) > 5 else states
    )
    render_risk_timeseries(    # mesmo componente de analise
        fire_df=fire_df,
        states=top_states,
        title="Top 5 estados por risco — focos diários",
        height=300,
    )

    # ── Ranking final de estados ───────────────────────────────────────────
    st.markdown('<div class="section-title">Ranking de estados por risco</div>', unsafe_allow_html=True)

    ranking_cols = ["estado", "bioma", "risk_label", "risk_score"]
    if "total_focos" in risk_df.columns:
        ranking_cols.append("total_focos")
    if "temperatura" in risk_df.columns:
        ranking_cols.append("temperatura")

    ranking_df = risk_df[ranking_cols].sort_values("risk_score", ascending=False).copy()
    ranking_df["risk_score"] = ranking_df["risk_score"].map("{:.1%}".format)
    if "temperatura" in ranking_df.columns:
        ranking_df["temperatura"] = ranking_df["temperatura"].map("{:.1f}°C".format)

    ranking_df.columns = [c.replace("_", " ").title() for c in ranking_df.columns]
    st.dataframe(ranking_df, use_container_width=True, hide_index=True)

    # ── Observações e limitações ───────────────────────────────────────────
    with st.expander("ℹ️ Notas metodológicas e limitações"):
        st.markdown("""
        **Fontes de dados:**
        - Focos de queimada: INPE / BDQueimadas (simulado com padrões históricos)
        - Dados climáticos: Open-Meteo API (simulado com perfis climatológicos por estado)
        - NDVI: Sentinel-2 / Copernicus (simulado com perfis por bioma)

        **Modelo de ML:**
        - Algoritmo: RandomForestClassifier (scikit-learn)
        - Treinamento: 4.000 amostras sintéticas com relações físicas reais
        - Features: 7 variáveis (focos, temperatura, umidade, precipitação, vento, NDVI, mês)
        - Saída: probabilidade de risco alto ou crítico (0–1)

        **Limitações:**
        - Dados são simulados para fins de demonstração
        - Em produção, substituir providers por APIs reais do INPE e Open-Meteo
        - O modelo deve ser re-treinado com dados históricos reais para uso operacional
        """)
