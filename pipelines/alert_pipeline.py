"""
pipelines/alert_pipeline.py
Geração automática de alertas agroclimáticos a partir do risco calculado.
Cada alerta tem contexto suficiente para o loop Human-in-the-Loop.
"""
import pandas as pd
import hashlib
from datetime import date, timedelta
import numpy as np


_ALERT_TEMPLATES = {
    3: [  # Crítico
        "Risco crítico de queimada detectado em {estado}. "
        "{focos:.0f} focos ativos com temperatura de {temperatura:.1f}°C e umidade de {umidade:.0f}%.",
        "Alerta máximo para {estado}: combinação de seca intensa e ventos de {vento:.0f} km/h "
        "elevam risco de propagação de incêndios em {area_agr:.0f} mil ha de área agrícola.",
    ],
    2: [  # Alto
        "Risco alto em {estado}. NDVI de {ndvi:.2f} indica vegetação estressada. "
        "Precipitação acumulada de apenas {precipitacao:.0f} mm no período.",
        "Condições de risco alto identificadas em {estado}: temperatura elevada ({temperatura:.1f}°C) "
        "e baixa umidade ({umidade:.0f}%) aumentam vulnerabilidade agrícola.",
    ],
    1: [  # Moderado
        "Atenção para {estado}: tendência de aumento de risco. "
        "Monitorar evolução dos focos de queimada nas próximas 72h.",
    ],
}

_RECOMMENDED_ACTIONS = {
    3: [
        "Acionar Corpo de Bombeiros e Defesa Civil estadual",
        "Emitir alerta para produtores rurais da região",
        "Suspender queimadas controladas autorizadas",
        "Posicionar brigadistas em pontos estratégicos",
    ],
    2: [
        "Notificar Defesa Civil sobre risco elevado",
        "Intensificar patrulhamento em áreas de preservação",
        "Alertar cooperativas agrícolas da região",
    ],
    1: [
        "Monitorar evolução nas próximas 48h",
        "Verificar sistemas de irrigação das propriedades",
    ],
}


def generate_alerts(
    risk_df: pd.DataFrame,
    threshold_class: int = 1,
    date_ref: date | None = None,
) -> list[dict]:
    """
    Gera lista de alertas para estados com risco >= threshold_class.
    Cada alerta inclui contexto completo para decisão HITL.
    """
    if date_ref is None:
        date_ref = date.today()

    rng = np.random.default_rng(99)
    alerts = []

    high_risk = risk_df[risk_df["risk_class"] >= threshold_class].copy()
    high_risk = high_risk.sort_values("risk_score", ascending=False)

    for _, row in high_risk.iterrows():
        cls  = int(row["risk_class"])
        templates = _ALERT_TEMPLATES.get(cls, _ALERT_TEMPLATES[1])
        template  = templates[rng.integers(0, len(templates))]

        try:
            mensagem = template.format(
                estado=row["estado"],
                focos=row.get("total_focos", 0),
                temperatura=row.get("temperatura", 25),
                umidade=row.get("umidade", 60),
                vento=row.get("vento", 15),
                ndvi=row.get("ndvi", 0.5),
                precipitacao=row.get("precipitacao", 50),
                area_agr=row.get("area_agr", 500),
            )
        except (KeyError, ValueError):
            mensagem = f"Risco {row['risk_label']} detectado em {row['estado']}."

        actions = _RECOMMENDED_ACTIONS.get(cls, _RECOMMENDED_ACTIONS[1])
        # ID determinístico baseado no estado + data + score
        raw_id = f"{row['estado']}-{date_ref}-{row['risk_score']:.3f}"
        alert_id = hashlib.md5(raw_id.encode()).hexdigest()[:8]

        alerts.append({
            "id":          alert_id,
            "estado":      row["estado"],
            "bioma":       row.get("bioma", ""),
            "risk_class":  cls,
            "risk_label":  row["risk_label"],
            "risk_score":  float(row["risk_score"]),
            "mensagem":    mensagem,
            "acoes":       actions,
            "criado_em":   date_ref.isoformat(),
            "validade":    (date_ref + timedelta(days=3)).isoformat(),
            "area_afetada": int(row.get("area_agr", 500)),
        })

    return alerts
