"""
ui/components/kpi_card.py
Componente reutilizável de KPI Card.
Invocado em features/panorama e features/analise com diferentes parâmetros.
"""
import streamlit as st


def render_kpi_card(
    label: str,
    value: str,
    delta: str | None = None,
    delta_direction: str = "neu",   # "up" | "down" | "neu"
    color_accent: str | None = None,
    icon: str = "",
    help_text: str | None = None,
):
    """
    Renderiza um card de métrica com label, valor e variação opcional.

    Args:
        label: Título da métrica (ex: "Focos de queimada")
        value: Valor formatado (ex: "1.234")
        delta: Variação opcional (ex: "+12% vs. mês anterior")
        delta_direction: "up" (ruim/vermelho), "down" (bom/verde), "neu" (cinza)
        color_accent: Cor opcional para borda superior do card (hex)
        icon: Emoji opcional
        help_text: Tooltip de ajuda
    """
    border_style = (
        f"border-top: 3px solid {color_accent};"
        if color_accent else ""
    )

    delta_html = ""
    if delta:
        delta_html = f'<div class="kpi-delta {delta_direction}">{delta}</div>'

    help_html = ""
    if help_text:
        help_html = f'<span title="{help_text}" style="cursor:help; color:#8B90A0; font-size:11px; margin-left:4px;">ⓘ</span>'

    st.markdown(f"""
    <div class="kpi-card" style="{border_style}">
        <div class="kpi-label">{icon} {label}{help_html}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def render_risk_badge(risk_label: str) -> str:
    """Retorna HTML de badge de risco semântico."""
    class_map = {
        "Crítico":  "risk-critico",
        "Alto":     "risk-alto",
        "Moderado": "risk-moderado",
        "Baixo":    "risk-baixo",
    }
    css_class = class_map.get(risk_label, "risk-baixo")
    return f'<span class="risk-badge {css_class}">{risk_label}</span>'


def render_skeleton_cards(n: int = 4):
    """Renderiza N skeleton loaders enquanto os dados carregam."""
    cols = st.columns(n)
    for col in cols:
        with col:
            st.markdown('<div class="skeleton"></div>', unsafe_allow_html=True)
