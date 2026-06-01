"""
providers/climate_provider.py
Acesso a dados meteorológicos (Open-Meteo API).
Mock com padrões climatológicos reais do Brasil por estado.
"""
import numpy as np
import pandas as pd
from datetime import date, timedelta
import streamlit as st


# Perfis climáticos por estado (temperatura média e precipitação)
_CLIMATE_PROFILES = {
    "AC": {"temp_mean": 26.5, "temp_std": 2.0, "prec_mean": 180, "prec_dry_months": [6, 7, 8]},
    "AL": {"temp_mean": 25.8, "temp_std": 2.5, "prec_mean": 80,  "prec_dry_months": [8, 9, 10]},
    "AM": {"temp_mean": 27.0, "temp_std": 1.5, "prec_mean": 200, "prec_dry_months": [7, 8]},
    "AP": {"temp_mean": 26.8, "temp_std": 1.8, "prec_mean": 160, "prec_dry_months": [9, 10]},
    "BA": {"temp_mean": 24.5, "temp_std": 3.0, "prec_mean": 50,  "prec_dry_months": [6, 7, 8, 9]},
    "CE": {"temp_mean": 26.5, "temp_std": 2.0, "prec_mean": 30,  "prec_dry_months": [6, 7, 8, 9, 10]},
    "DF": {"temp_mean": 21.5, "temp_std": 3.5, "prec_mean": 40,  "prec_dry_months": [5, 6, 7, 8, 9]},
    "ES": {"temp_mean": 23.0, "temp_std": 3.0, "prec_mean": 90,  "prec_dry_months": [6, 7, 8]},
    "GO": {"temp_mean": 23.5, "temp_std": 3.5, "prec_mean": 45,  "prec_dry_months": [5, 6, 7, 8, 9]},
    "MA": {"temp_mean": 27.0, "temp_std": 2.0, "prec_mean": 60,  "prec_dry_months": [7, 8, 9, 10]},
    "MG": {"temp_mean": 22.0, "temp_std": 4.0, "prec_mean": 60,  "prec_dry_months": [5, 6, 7, 8, 9]},
    "MS": {"temp_mean": 24.0, "temp_std": 4.5, "prec_mean": 55,  "prec_dry_months": [6, 7, 8]},
    "MT": {"temp_mean": 26.0, "temp_std": 3.0, "prec_mean": 50,  "prec_dry_months": [5, 6, 7, 8, 9]},
    "PA": {"temp_mean": 27.5, "temp_std": 1.5, "prec_mean": 120, "prec_dry_months": [8, 9, 10]},
    "PB": {"temp_mean": 26.0, "temp_std": 2.5, "prec_mean": 25,  "prec_dry_months": [6, 7, 8, 9, 10]},
    "PE": {"temp_mean": 25.5, "temp_std": 2.5, "prec_mean": 30,  "prec_dry_months": [7, 8, 9, 10]},
    "PI": {"temp_mean": 28.0, "temp_std": 2.5, "prec_mean": 40,  "prec_dry_months": [6, 7, 8, 9]},
    "PR": {"temp_mean": 19.0, "temp_std": 5.0, "prec_mean": 130, "prec_dry_months": []},
    "RJ": {"temp_mean": 23.5, "temp_std": 3.5, "prec_mean": 90,  "prec_dry_months": [6, 7, 8]},
    "RN": {"temp_mean": 27.0, "temp_std": 2.0, "prec_mean": 25,  "prec_dry_months": [7, 8, 9, 10]},
    "RO": {"temp_mean": 26.0, "temp_std": 2.5, "prec_mean": 70,  "prec_dry_months": [6, 7, 8]},
    "RR": {"temp_mean": 28.0, "temp_std": 2.0, "prec_mean": 40,  "prec_dry_months": [1, 2, 3]},
    "RS": {"temp_mean": 17.5, "temp_std": 6.0, "prec_mean": 110, "prec_dry_months": []},
    "SC": {"temp_mean": 18.0, "temp_std": 5.5, "prec_mean": 120, "prec_dry_months": []},
    "SE": {"temp_mean": 25.5, "temp_std": 2.5, "prec_mean": 60,  "prec_dry_months": [8, 9, 10]},
    "SP": {"temp_mean": 21.5, "temp_std": 4.0, "prec_mean": 75,  "prec_dry_months": [6, 7, 8]},
    "TO": {"temp_mean": 28.0, "temp_std": 2.5, "prec_mean": 40,  "prec_dry_months": [5, 6, 7, 8, 9]},
}


@st.cache_data(ttl=3600, show_spinner=False)
def get_climate_data(
    date_start: date,
    date_end: date,
    states: list[str],
) -> pd.DataFrame:
    """
    Retorna DataFrame com dados climáticos diários por estado.
    Colunas: estado, data, temperatura, umidade, precipitacao, vento
    """
    rng = np.random.default_rng(7)
    records = []
    days = (date_end - date_start).days + 1
    dates = [date_start + timedelta(d) for d in range(days)]

    for uf in states:
        p = _CLIMATE_PROFILES.get(uf, {
            "temp_mean": 24.0, "temp_std": 3.0,
            "prec_mean": 80,   "prec_dry_months": [7, 8],
        })
        for d in dates:
            # Temperatura com variação sazonal
            season_offset = 3.0 * np.sin(2 * np.pi * (d.month - 1) / 12)
            temp = rng.normal(p["temp_mean"] + season_offset, p["temp_std"])

            # Precipitação: quase zero nos meses secos
            is_dry = d.month in p["prec_dry_months"]
            prec_base = p["prec_mean"] * (0.1 if is_dry else 1.0)
            precipitacao = max(0, rng.exponential(prec_base))

            # Umidade inversamente proporcional à temperatura e seca
            umidade = max(20, min(95, 90 - (temp - 20) * 1.5 - (20 if is_dry else 0) + rng.normal(0, 5)))

            # Velocidade do vento (km/h)
            vento = max(0, rng.normal(15, 6))

            records.append({
                "estado":       uf,
                "data":         d,
                "temperatura":  round(temp, 1),
                "umidade":      round(umidade, 1),
                "precipitacao": round(precipitacao, 1),
                "vento":        round(vento, 1),
            })

    return pd.DataFrame(records)


@st.cache_data(ttl=3600, show_spinner=False)
def get_climate_summary(
    date_start: date,
    date_end: date,
    states: list[str],
) -> pd.DataFrame:
    """Agrega dados climáticos por estado (média do período)."""
    df = get_climate_data(date_start, date_end, states)
    return (
        df.groupby("estado")
        .agg(
            temp_media=("temperatura", "mean"),
            umidade_media=("umidade", "mean"),
            prec_total=("precipitacao", "sum"),
            vento_medio=("vento", "mean"),
        )
        .reset_index()
        .round(1)
    )
