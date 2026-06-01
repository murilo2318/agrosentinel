"""
features/alertas/page.py
Painel de alertas com loop Human-in-the-Loop (HITL).
O usuário revisa alertas gerados pelo modelo e decide aprovar ou descartar.
Este é o requisito central de Feedback Humano da Global Solution.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from state.session  import get, set
from state.alerts   import get_decision, register_decision, count_pending, count_confirmed
from ui.components.kpi_card   import render_kpi_card, render_risk_badge, render_skeleton_cards


_RISK_ICONS = {
    "Crítico":  "🔴",
    "Alto":     "🟠",
    "Moderado": "🟡",
    "Baixo":    "🟢",
}


def render(filters: dict):
    """Renderiza o painel de alertas com decisão HITL."""
    alerts = get("data_alerts")

    if alerts is None:
        st.info("⏳ Carregue os dados na aba **Panorama** primeiro.")
        return

    # ── Header ─────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="section-title">⚡ Central de Alertas — Revisão Humana</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Alertas gerados automaticamente pelo modelo de risco. "
        "Revise o contexto e decida se cada alerta deve ser confirmado e enviado."
    )

    # ── KPIs de alertas ────────────────────────────────────────────────────
    n_total    = len(alerts)
    n_pending  = count_pending(alerts)
    n_confirmed = count_confirmed(alerts)
    n_discarded = n_total - n_pending - n_confirmed

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_kpi_card("Total de alertas", str(n_total), icon="📋")
    with col2:
        render_kpi_card(
            "Aguardando revisão", str(n_pending),
            delta="Requerem sua decisão" if n_pending > 0 else "Tudo revisado ✓",
            delta_direction="up" if n_pending > 0 else "down",
            color_accent="#F4A261", icon="⏳"
        )
    with col3:
        render_kpi_card(
            "Confirmados", str(n_confirmed),
            delta="Serão enviados às autoridades",
            delta_direction="down",
            color_accent="#52B788", icon="✅"
        )
    with col4:
        render_kpi_card(
            "Descartados", str(n_discarded),
            delta="Não necessitam ação",
            delta_direction="neu",
            color_accent="#3A3E55", icon="🚫"
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Barra de progresso de revisão ──────────────────────────────────────
    if n_total > 0:
        progress = (n_confirmed + n_discarded) / n_total
        st.markdown(
            f"""
            <div style="margin-bottom:4px; font-size:12px; color:#8B90A0;">
                Progresso de revisão: {n_confirmed + n_discarded}/{n_total} alertas
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.progress(progress)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Filtro de nível de risco para os alertas ───────────────────────────
    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        level_filter = st.multiselect(
            "Filtrar por nível",
            options=["Crítico", "Alto", "Moderado", "Baixo"],
            default=["Crítico", "Alto", "Moderado"],
            key="alert_level_filter",
        )
    with col_f2:
        status_filter = st.selectbox(
            "Status",
            options=["Todos", "Pendentes", "Confirmados", "Descartados"],
            key="alert_status_filter",
        )

    # ── Lista de alertas ───────────────────────────────────────────────────
    filtered_alerts = [
        a for a in alerts
        if a["risk_label"] in level_filter
    ]

    if status_filter == "Pendentes":
        filtered_alerts = [a for a in filtered_alerts if get_decision(a["id"]) is None]
    elif status_filter == "Confirmados":
        filtered_alerts = [a for a in filtered_alerts if get_decision(a["id"]) == "confirmed"]
    elif status_filter == "Descartados":
        filtered_alerts = [a for a in filtered_alerts if get_decision(a["id"]) == "discarded"]

    if not filtered_alerts:
        st.info("Nenhum alerta encontrado com os filtros selecionados.")
        return

    for alert in filtered_alerts:
        _render_alert_card(alert)

    # ── Botão de reset de decisões ─────────────────────────────────────────
    st.markdown("---")
    col_r1, col_r2 = st.columns([3, 1])
    with col_r2:
        if st.button("↩️ Resetar todas as decisões", use_container_width=True):
            from state.alerts import reset_decisions
            reset_decisions()
            st.rerun()


def _render_alert_card(alert: dict):
    """Renderiza um card de alerta individual com botões HITL."""
    decision   = get_decision(alert["id"])
    icon       = _RISK_ICONS.get(alert["risk_label"], "⚠️")
    badge_html = render_risk_badge(alert["risk_label"])

    # CSS class baseada no status
    card_class = "alert-card"
    if decision == "confirmed":
        card_class += " confirmed"
    elif decision == "discarded":
        card_class += " discarded"

    status_html = ""
    if decision == "confirmed":
        status_html = '<span style="color:#52B788; font-size:12px;">✅ Confirmado — será enviado</span>'
    elif decision == "discarded":
        status_html = '<span style="color:#4A4E60; font-size:12px;">🚫 Descartado</span>'

    st.markdown(
        f"""
        <div class="{card_class}">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div class="alert-card-title">
                    {icon} {alert['estado']} — {alert['bioma']}
                </div>
                <div>{badge_html}</div>
            </div>
            <div class="alert-card-meta">
                Score: {alert['risk_score']:.1%} &nbsp;·&nbsp;
                Área afetada: ~{alert['area_afetada']:,} mil ha &nbsp;·&nbsp;
                Válido até: {alert['validade']}
            </div>
            <p style="font-size:13px; color:#C8CAD4; margin:10px 0 8px;">
                {alert['mensagem']}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Ações recomendadas e botões HITL
    with st.expander(f"Ver detalhes e ações recomendadas — {alert['id']}", expanded=(decision is None)):
        st.markdown("**Ações recomendadas pelo sistema:**")
        for i, acao in enumerate(alert["acoes"], 1):
            st.markdown(f"&nbsp;&nbsp;{i}. {acao}")

        st.markdown("")

        # ── Botões de decisão HITL ─────────────────────────────────────────
        if decision is None:
            col_confirm, col_discard, col_info = st.columns([2, 2, 3])
            with col_confirm:
                if st.button(
                    "✅ Confirmar envio",
                    key=f"confirm_{alert['id']}",
                    use_container_width=True,
                    type="primary",
                ):
                    register_decision(alert["id"], "confirmed")
                    st.rerun()
            with col_discard:
                if st.button(
                    "🚫 Descartar",
                    key=f"discard_{alert['id']}",
                    use_container_width=True,
                ):
                    register_decision(alert["id"], "discarded")
                    st.rerun()
            with col_info:
                st.caption(f"ID: `{alert['id']}` · Criado: {alert['criado_em']}")
        else:
            st.markdown(status_html, unsafe_allow_html=True)
            if st.button(
                "↩️ Reverter decisão",
                key=f"revert_{alert['id']}",
                use_container_width=False,
            ):
                from state.session import get as sget, set as sset
                decisions = sget("hitl_decisions") or {}
                decisions.pop(alert["id"], None)
                sset("hitl_decisions", decisions)
                st.rerun()
