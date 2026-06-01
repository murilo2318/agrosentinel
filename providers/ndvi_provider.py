"""
providers/ndvi_provider.py
Índice de Vegetação por Diferença Normalizada (NDVI) simulado.
Baseado em padrões do Sentinel-2 por bioma e época do ano.
NDVI: -1 a 1 (vegetação densa próxima de 0.8, solo exposto próximo de 0.1)
"""
import numpy as np
import pandas as pd
from datetime import date, timedelta
import streamlit as st


# Perfis de NDVI por bioma e sazonalidade
_NDVI_PROFILES = {
    "Amazônia":       {"base": 0.82, "amplitude": 0.05, "peak_month": 4},
    "Cerrado":        {"base": 0.55, "amplitude": 0.20, "peak_month": 3},
    "Caatinga":       {"base": 0.35, "amplitude": 0.30, "peak_month": 4},
    "Mata Atlântica": {"base": 0.70, "amplitude": 0.10, "peak_month": 3},
    "Pampa":          {"base": 0.60, "amplitude": 0.20, "peak_month": 11},
    "Pantanal":       {"base": 0.65, "amplitude": 0.15, "peak_month": 2},
}

_STATE_BIOME = {
    "AC": "Amazônia",   "AL": "Caatinga",     "AM": "Amazônia",
    "AP": "Amazônia",   "BA": "Cerrado",       "CE": "Caatinga",
    "DF": "Cerrado",    "ES": "Mata Atlântica","GO": "Cerrado",
    "MA": "Cerrado",    "MG": "Cerrado",       "MS": "Cerrado",
    "MT": "Amazônia",   "PA": "Amazônia",      "PB": "Caatinga",
    "PE": "Caatinga",   "PI": "Caatinga",      "PR": "Mata Atlântica",
    "RJ": "Mata Atlântica","RN": "Caatinga",   "RO": "Amazônia",
    "RR": "Amazônia",   "RS": "Pampa",         "SC": "Mata Atlântica",
    "SE": "Caatinga",   "SP": "Cerrado",       "TO": "Cerrado",
}


@st.cache_data(ttl=3600, show_spinner=False)
def get_ndvi_data(
    date_start: date,
    date_end: date,
    states: list[str],
) -> pd.DataFrame:
    """
    Retorna DataFrame com NDVI semanal por estado.
    Colunas: estado, data, ndvi, bioma, ndvi_anomalia
    """
    rng = np.random.default_rng(13)
    records = []
    # NDVI é disponível ~semanalmente (satélite passa a cada 5 dias)
    days = (date_end - date_start).days + 1
    dates = [
        date_start + timedelta(d)
        for d in range(0, days, 5)  # a cada 5 dias
    ]

    for uf in states:
        biome = _STATE_BIOME.get(uf, "Cerrado")
        p = _NDVI_PROFILES[biome]
        for d in dates:
            # Sazonalidade
            season_factor = p["amplitude"] * np.cos(
                2 * np.pi * (d.month - p["peak_month"]) / 12
            )
            ndvi = p["base"] + season_factor + rng.normal(0, 0.03)
            ndvi = float(np.clip(ndvi, 0.0, 1.0))

            # Anomalia em relação à média do bioma
            anomalia = ndvi - p["base"]

            records.append({
                "estado":       uf,
                "data":         d,
                "ndvi":         round(ndvi, 3),
                "bioma":        biome,
                "ndvi_anomalia": round(anomalia, 3),
            })

    return pd.DataFrame(records)


@st.cache_data(ttl=3600, show_spinner=False)
def get_ndvi_summary(
    date_start: date,
    date_end: date,
    states: list[str],
) -> pd.DataFrame:
    """Agrega NDVI por estado (média do período)."""
    df = get_ndvi_data(date_start, date_end, states)
    return (
        df.groupby(["estado", "bioma"])
        .agg(
            ndvi_medio=("ndvi", "mean"),
            ndvi_min=("ndvi", "min"),
            ndvi_max=("ndvi", "max"),
            anomalia_media=("ndvi_anomalia", "mean"),
        )
        .reset_index()
        .round(3)
    )
