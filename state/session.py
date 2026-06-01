"""
state/session.py
Inicialização e acesso centralizado ao st.session_state.
Toda chave de estado passa por aqui — nenhuma feature acessa
session_state diretamente sem passar por este módulo.
"""
import streamlit as st
from datetime import date, timedelta


_DEFAULTS: dict = {
    # Filtros ativos
    "filter_states":      ["SP", "MG", "MT", "PA", "MS"],
    "filter_date_start":  date.today() - timedelta(days=30),
    "filter_date_end":    date.today(),
    "filter_risk_min":    0.0,
    "filter_cultures":    ["Soja", "Milho", "Cana", "Pecuária", "Todos"],
    "filter_culture_sel": "Todos",

    # Dados carregados (preenchidos pelos providers)
    "data_fire":          None,
    "data_climate":       None,
    "data_ndvi":          None,
    "data_risk":          None,
    "data_alerts":        None,

    # Modelo de ML
    "ml_model":           None,
    "ml_trained":         False,

    # Estado HITL (Human-in-the-loop)
    "hitl_decisions":     {},   # {alert_id: "confirmed" | "discarded"}

    # UI state
    "selected_state":     None,
    "data_loaded":        False,
    "last_refresh":       None,
}


def init():
    """Inicializa todas as chaves com valores padrão se ainda não existirem."""
    for key, default in _DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = default


def get(key: str):
    return st.session_state.get(key)


def set(key: str, value):
    st.session_state[key] = value


def reset_data():
    """Força recarregamento dos dados na próxima execução."""
    for key in ["data_fire", "data_climate", "data_ndvi", "data_risk", "data_alerts"]:
        st.session_state[key] = None
    st.session_state["data_loaded"] = False
