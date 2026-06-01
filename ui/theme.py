"""
ui/theme.py
Configuração de página e injeção de CSS global do AgroSentinel.
"""
import streamlit as st


PALETTE = {
    "verde_safe":   "#2D6A4F",
    "verde_mid":    "#52B788",
    "amarelo":      "#F4A261",
    "laranja":      "#E76F51",
    "vermelho":     "#C1121F",
    "terra":        "#6B4226",
    "bg_dark":      "#0F1117",
    "bg_card":      "#1A1D27",
    "bg_card2":     "#21253A",
    "texto":        "#E8EAF0",
    "texto_muted":  "#8B90A0",
}

RISK_COLORSCALE = [
    [0.0,  "#2D6A4F"],
    [0.25, "#52B788"],
    [0.50, "#F4A261"],
    [0.75, "#E76F51"],
    [1.0,  "#C1121F"],
]


def configure_page():
    st.set_page_config(
        page_title="AgroSentinel",
        page_icon="🌿",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    _inject_css()


def _inject_css():
    st.markdown("""
    <style>
    /* ── Base ─────────────────────────────────────────── */
    [data-testid="stAppViewContainer"] {
        background: #0F1117;
    }
    [data-testid="stSidebar"] {
        background: #13161F;
        border-right: 1px solid #2A2E40;
    }
    [data-testid="stSidebar"] * {
        color: #E8EAF0 !important;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    /* ── Logo / Header ────────────────────────────────── */
    .ags-logo {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 1.5rem;
    }
    .ags-logo-icon {
        font-size: 28px;
        line-height: 1;
    }
    .ags-logo-text {
        font-size: 22px;
        font-weight: 700;
        color: #52B788;
        letter-spacing: -0.5px;
    }
    .ags-logo-sub {
        font-size: 11px;
        color: #8B90A0;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-top: -4px;
    }

    /* ── KPI Cards ────────────────────────────────────── */
    .kpi-card {
        background: #1A1D27;
        border: 1px solid #2A2E40;
        border-radius: 12px;
        padding: 16px 20px;
        transition: border-color 0.2s;
    }
    .kpi-card:hover { border-color: #3A3E55; }
    .kpi-label {
        font-size: 12px;
        color: #8B90A0;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        color: #E8EAF0;
        line-height: 1;
    }
    .kpi-delta {
        font-size: 12px;
        margin-top: 6px;
    }
    .kpi-delta.up   { color: #C1121F; }
    .kpi-delta.down { color: #52B788; }
    .kpi-delta.neu  { color: #8B90A0; }

    /* ── Risk Badge ───────────────────────────────────── */
    .risk-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    .risk-critico   { background:#3D0A0A; color:#FF6B6B; border:1px solid #C1121F; }
    .risk-alto      { background:#3D1A0A; color:#FFA07A; border:1px solid #E76F51; }
    .risk-moderado  { background:#3D2D0A; color:#FFD166; border:1px solid #F4A261; }
    .risk-baixo     { background:#0A2D1A; color:#6FCF97; border:1px solid #52B788; }

    /* ── Alert Card (HITL) ────────────────────────────── */
    .alert-card {
        background: #1A1D27;
        border-left: 4px solid #E76F51;
        border-radius: 0 10px 10px 0;
        padding: 14px 18px;
        margin-bottom: 12px;
        transition: opacity 0.3s;
    }
    .alert-card.confirmed { border-left-color: #52B788; opacity: 0.6; }
    .alert-card.discarded { border-left-color: #3A3E55; opacity: 0.4; }
    .alert-card-title {
        font-size: 14px;
        font-weight: 600;
        color: #E8EAF0;
        margin-bottom: 4px;
    }
    .alert-card-meta {
        font-size: 12px;
        color: #8B90A0;
    }

    /* ── Section divider ──────────────────────────────── */
    .section-title {
        font-size: 13px;
        font-weight: 600;
        color: #8B90A0;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 1.2rem 0 0.6rem;
    }

    /* ── Skeleton loader ──────────────────────────────── */
    @keyframes shimmer {
        0%   { background-position: -700px 0; }
        100% { background-position:  700px 0; }
    }
    .skeleton {
        background: linear-gradient(90deg, #1A1D27 25%, #21253A 50%, #1A1D27 75%);
        background-size: 700px 100%;
        animation: shimmer 1.4s infinite;
        border-radius: 8px;
        height: 80px;
        margin-bottom: 10px;
    }

    /* ── Scrollbar ────────────────────────────────────── */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0F1117; }
    ::-webkit-scrollbar-thumb { background: #2A2E40; border-radius: 3px; }
    </style>
    """, unsafe_allow_html=True)


def render_logo(sidebar: bool = True):
    html = """
    <div class="ags-logo">
        <span class="ags-logo-icon">🌿</span>
        <div>
            <div class="ags-logo-text">AgroSentinel</div>
            <div class="ags-logo-sub">Monitoramento Agroclimático</div>
        </div>
    </div>
    """
    if sidebar:
        st.sidebar.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(html, unsafe_allow_html=True)
