"""
state/alerts.py
Gerenciamento de estado das decisões Human-in-the-Loop.
Registra aprovações e descartes de alertas pelo usuário.
"""
from state.session import get, set


def get_decision(alert_id: str) -> str | None:
    """Retorna 'confirmed', 'discarded' ou None se pendente."""
    decisions = get("hitl_decisions") or {}
    return decisions.get(alert_id)


def register_decision(alert_id: str, decision: str):
    """Registra decisão do usuário para um alerta específico."""
    assert decision in ("confirmed", "discarded")
    decisions = get("hitl_decisions") or {}
    decisions[alert_id] = decision
    set("hitl_decisions", decisions)


def count_pending(alerts: list[dict]) -> int:
    decisions = get("hitl_decisions") or {}
    return sum(1 for a in alerts if a["id"] not in decisions)


def count_confirmed(alerts: list[dict]) -> int:
    decisions = get("hitl_decisions") or {}
    return sum(1 for a in alerts if decisions.get(a["id"]) == "confirmed")


def reset_decisions():
    set("hitl_decisions", {})
