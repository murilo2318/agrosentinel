"""
ui/sidebar/filters.py
Todos os filtros interativos do AgroSentinel em um único módulo.
Mínimo de 5 filtros que afetam dados exibidos em todas as features.
"""
import streamlit as st
from datetime import date, timedelta
from state import filters as filter_state
from ui.theme import render_logo

ALL_STATES = [
    "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO",
    "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR",
    "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO",
]

ALL_CULTURES = ["Todos", "Soja", "Milho", "Cana", "Pecuária", "Café", "Algodão"]

BIOMES = ["Todos", "Amazônia", "Cerrado", "Caatinga", "Mata Atlântica", "Pampa", "Pantanal"]

_STATE_BY_BIOME = {
    "Amazônia":       ["AC", "AM", "AP", "MT", "PA", "RO", "RR"],
    "Cerrado":        ["BA", "DF", "GO", "MA", "MG", "MS", "MT", "PI", "SP", "TO"],
    "Caatinga":       ["AL", "BA", "CE", "PB", "PE", "PI", "RN", "SE"],
    "Mata Atlântica": ["ES", "MG", "PR", "RJ", "RS", "SC", "SP"],
    "Pampa":          ["RS"],
    "Pantanal":       ["MS", "MT"],
}


def render_sidebar() -> dict:
    """
    Renderiza o sidebar completo e retorna os valores dos filtros ativos.
    Retorna dict com todos os filtros para uso nas features.
    """
    render_logo(sidebar=True)

    st.sidebar.markdown(
        '<div class="section-title">📅 Período de análise</div>',
        unsafe_allow_html=True,
    )

    # Filtro 1 — Intervalo de datas
    col1, col2 = st.sidebar.columns(2)
    with col1:
        date_start = st.date_input(
            "De",
            value=filter_state.get_date_range()[0],
            max_value=date.today(),
            key="filter_date_start_widget",
        )
    with col2:
        date_end = st.date_input(
            "Até",
            value=filter_state.get_date_range()[1],
            max_value=date.today(),
            key="filter_date_end_widget",
        )

    if date_start > date_end:
        st.sidebar.error("⚠️ Data inicial maior que a final.")
        date_start = date_end - timedelta(days=30)

    filter_state.set_date_range(date_start, date_end)

    st.sidebar.markdown(
        '<div class="section-title">🗺️ Localização</div>',
        unsafe_allow_html=True,
    )

    # Filtro 2 — Bioma (pré-seleção de estados)
    biome_sel = st.sidebar.selectbox(
        "Filtrar por bioma",
        options=BIOMES,
        index=0,
        key="filter_biome",
    )

    default_states = (
        _STATE_BY_BIOME.get(biome_sel, ALL_STATES)
        if biome_sel != "Todos"
        else filter_state.get_selected_states()
    )

    # Filtro 3 — Estados (multiselect)
    selected_states = st.sidebar.multiselect(
        "Estados",
        options=ALL_STATES,
        default=default_states,
        key="filter_states_widget",
        help="Selecione até 27 estados para análise",
    )
    if not selected_states:
        selected_states = ["SP", "MG", "MT"]
        st.sidebar.warning("Selecione ao menos 1 estado.")

    filter_state.set_selected_states(selected_states)

    st.sidebar.markdown(
        '<div class="section-title">⚠️ Risco</div>',
        unsafe_allow_html=True,
    )

    # Filtro 4 — Threshold de risco mínimo
    risk_min = st.sidebar.slider(
        "Mostrar risco ≥",
        min_value=0.0,
        max_value=1.0,
        value=filter_state.get_risk_threshold(),
        step=0.05,
        format="%.2f",
        key="filter_risk_widget",
        help="Filtra estados com score de risco abaixo do threshold",
    )
    filter_state.set_risk_threshold(risk_min)

    st.sidebar.markdown(
        '<div class="section-title">🌱 Cultura</div>',
        unsafe_allow_html=True,
    )

    # Filtro 5 — Tipo de cultura agrícola
    culture = st.sidebar.selectbox(
        "Cultura agrícola",
        options=ALL_CULTURES,
        index=ALL_CULTURES.index(filter_state.get_culture()),
        key="filter_culture_widget",
        help="Filtra análise por tipo de cultura predominante",
    )
    filter_state.set_culture(culture)

    # Botão de atualização
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Atualizar dados", use_container_width=True):
        from state.session import reset_data
        reset_data()
        st.rerun()

    # Rodapé do sidebar
    st.sidebar.markdown(
        f"""
        <div style="
            font-size: 11px;
            color: #4A4E60;
            margin-top: 2rem;
            text-align: center;
            line-height: 1.8;
        ">
            AgroSentinel v1.0<br>
            Dados: INPE · Open-Meteo · Sentinel-2<br>
            Modelo: RandomForest (sklearn)
        </div>
        """,
        unsafe_allow_html=True,
    )

    return {
        "date_start":  date_start,
        "date_end":    date_end,
        "states":      selected_states,
        "risk_min":    risk_min,
        "culture":     culture,
        "biome":       biome_sel,
    }
