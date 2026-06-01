"""
app.py
Entrypoint do AgroSentinel — orquestrador principal.
Responsável apenas por: configurar página, inicializar estado,
renderizar sidebar e despachar para as features corretas.
"""
from ui.theme             import configure_page
from state.session        import init as init_state
from ui.sidebar.filters   import render_sidebar

# Configuração de página deve ser a primeira chamada Streamlit
configure_page()

# Inicializa session_state com valores padrão
init_state()

# Sidebar retorna todos os filtros ativos
filters = render_sidebar()

# ── Cabeçalho principal ────────────────────────────────────────────────────
import streamlit as st

st.markdown(
    """
    <div style="
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.5rem;
    ">
        <div>
            <h1 style="
                font-size: 26px;
                font-weight: 700;
                color: #52B788;
                margin: 0;
                letter-spacing: -0.5px;
            ">🌿 AgroSentinel</h1>
            <p style="
                font-size: 13px;
                color: #8B90A0;
                margin: 2px 0 0;
            ">Dashboard de Monitoramento de Risco Agroclimático · Brasil</p>
        </div>
        <div style="
            font-size: 11px;
            color: #4A4E60;
            text-align: right;
            line-height: 1.8;
        ">
            Modelo: RandomForest (sklearn)<br>
            Fontes: INPE · Open-Meteo · Sentinel-2
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<hr style="border-color: #2A2E40; margin: 0 0 1rem;">',
    unsafe_allow_html=True,
)

# ── Navegação por abas ─────────────────────────────────────────────────────
tab_panorama, tab_alertas, tab_analise, tab_relatorio = st.tabs([
    "🌎 Panorama Nacional",
    "⚡ Alertas & Decisões",
    "📈 Análise Temporal",
    "📄 Relatório",
])

with tab_panorama:
    from features.panorama.page import render as render_panorama
    render_panorama(filters)

with tab_alertas:
    from features.alertas.page import render as render_alertas
    render_alertas(filters)

with tab_analise:
    from features.analise.page import render as render_analise
    render_analise(filters)

with tab_relatorio:
    from features.relatorio.page import render as render_relatorio
    render_relatorio(filters)
