"""
state/filters.py
Getters e setters tipados para os filtros ativos.
Centraliza a lógica de validação de filtros.
"""
from datetime import date
from state.session import get, set


def get_date_range() -> tuple[date, date]:
    return get("filter_date_start"), get("filter_date_end")


def set_date_range(start: date, end: date):
    if start <= end:
        set("filter_date_start", start)
        set("filter_date_end", end)


def get_selected_states() -> list[str]:
    return get("filter_states") or []


def set_selected_states(states: list[str]):
    set("filter_states", states)


def get_risk_threshold() -> float:
    return get("filter_risk_min") or 0.0


def set_risk_threshold(value: float):
    set("filter_risk_min", max(0.0, min(1.0, value)))


def get_culture() -> str:
    return get("filter_culture_sel") or "Todos"


def set_culture(culture: str):
    set("filter_culture_sel", culture)
