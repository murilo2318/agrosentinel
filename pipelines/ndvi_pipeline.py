"""
pipelines/ndvi_pipeline.py
Aggregação e análise temporal do índice NDVI.
Detecta tendências de degradação de vegetação por estado.
"""
import pandas as pd
import numpy as np
from datetime import date

from providers.ndvi_provider import get_ndvi_data


def get_ndvi_trend(
    date_start: date,
    date_end: date,
    states: list[str],
) -> pd.DataFrame:
    """
    Calcula tendência linear do NDVI no período para cada estado.
    Retorna slope (positivo = vegetação melhorando, negativo = degradando).
    """
    df = get_ndvi_data(date_start, date_end, states)
    df["day_num"] = (
        pd.to_datetime(df["data"]) - pd.to_datetime(date_start)
    ).dt.days

    results = []
    for state, grp in df.groupby("estado"):
        if len(grp) < 2:
            continue
        slope, intercept = np.polyfit(grp["day_num"], grp["ndvi"], 1)
        results.append({
            "estado":        state,
            "ndvi_slope":    round(slope * 30, 4),   # variação por mês
            "ndvi_intercept": round(intercept, 3),
            "tendencia":     "↗ Melhora" if slope > 0.0005 else (
                             "↘ Degrada" if slope < -0.0005 else "→ Estável"
            ),
        })

    return pd.DataFrame(results)


def get_ndvi_timeseries(
    date_start: date,
    date_end: date,
    states: list[str],
) -> pd.DataFrame:
    """Série temporal de NDVI pronta para plotagem."""
    df = get_ndvi_data(date_start, date_end, states)
    df["data"] = pd.to_datetime(df["data"])
    return df.sort_values(["estado", "data"])
