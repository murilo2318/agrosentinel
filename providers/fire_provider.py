"""
providers/fire_provider.py
Acesso a dados de focos de queimada (INPE / BDQueimadas).
Em produção faria chamada HTTP à API do INPE. Aqui usa mock
realista baseado em padrões históricos brasileiros.
"""
import numpy as np
import pandas as pd
from datetime import date, timedelta
import streamlit as st

# Estados e suas características de risco de queimada
_STATE_PROFILES = {
    "AC": {"base_fire": 80,  "peak_month": 8,  "biome": "Amazônia"},
    "AL": {"base_fire": 15,  "peak_month": 9,  "biome": "Caatinga"},
    "AM": {"base_fire": 120, "peak_month": 8,  "biome": "Amazônia"},
    "AP": {"base_fire": 30,  "peak_month": 9,  "biome": "Amazônia"},
    "BA": {"base_fire": 90,  "peak_month": 9,  "biome": "Cerrado"},
    "CE": {"base_fire": 25,  "peak_month": 8,  "biome": "Caatinga"},
    "DF": {"base_fire": 10,  "peak_month": 8,  "biome": "Cerrado"},
    "ES": {"base_fire": 20,  "peak_month": 8,  "biome": "Mata Atlântica"},
    "GO": {"base_fire": 70,  "peak_month": 8,  "biome": "Cerrado"},
    "MA": {"base_fire": 110, "peak_month": 9,  "biome": "Cerrado"},
    "MG": {"base_fire": 85,  "peak_month": 8,  "biome": "Cerrado"},
    "MS": {"base_fire": 65,  "peak_month": 9,  "biome": "Cerrado"},
    "MT": {"base_fire": 190, "peak_month": 8,  "biome": "Amazônia"},
    "PA": {"base_fire": 210, "peak_month": 8,  "biome": "Amazônia"},
    "PB": {"base_fire": 18,  "peak_month": 9,  "biome": "Caatinga"},
    "PE": {"base_fire": 22,  "peak_month": 9,  "biome": "Caatinga"},
    "PI": {"base_fire": 55,  "peak_month": 9,  "biome": "Caatinga"},
    "PR": {"base_fire": 28,  "peak_month": 8,  "biome": "Mata Atlântica"},
    "RJ": {"base_fire": 12,  "peak_month": 8,  "biome": "Mata Atlântica"},
    "RN": {"base_fire": 14,  "peak_month": 9,  "biome": "Caatinga"},
    "RO": {"base_fire": 160, "peak_month": 8,  "biome": "Amazônia"},
    "RR": {"base_fire": 90,  "peak_month": 3,  "biome": "Amazônia"},
    "RS": {"base_fire": 20,  "peak_month": 11, "biome": "Pampa"},
    "SC": {"base_fire": 15,  "peak_month": 8,  "biome": "Mata Atlântica"},
    "SE": {"base_fire": 12,  "peak_month": 9,  "biome": "Caatinga"},
    "SP": {"base_fire": 55,  "peak_month": 8,  "biome": "Cerrado"},
    "TO": {"base_fire": 130, "peak_month": 8,  "biome": "Cerrado"},
}


@st.cache_data(ttl=3600, show_spinner=False)
def get_fire_data(
    date_start: date,
    date_end: date,
    states: list[str],
) -> pd.DataFrame:
    """
    Retorna DataFrame com focos de queimada por estado e dia.
    Colunas: estado, data, focos, bioma, lat, lon
    """
    rng = np.random.default_rng(42)
    records = []
    days = (date_end - date_start).days + 1
    dates = [date_start + timedelta(d) for d in range(days)]

    for uf in states:
        profile = _STATE_PROFILES.get(uf, {"base_fire": 30, "peak_month": 8, "biome": "Cerrado"})
        for d in dates:
            # Sazonalidade: mais focos no mês de pico
            month_factor = 1.0 + 0.8 * np.cos(
                np.pi * (d.month - profile["peak_month"]) / 6
            )
            month_factor = max(0.2, month_factor)
            base = profile["base_fire"] * month_factor
            # Ruído diário
            focos = max(0, int(rng.normal(base, base * 0.25)))
            records.append({
                "estado": uf,
                "data":   d,
                "focos":  focos,
                "bioma":  profile["biome"],
            })

    df = pd.DataFrame(records)
    df["focos_norm"] = (df["focos"] / df["focos"].max()).clip(0, 1)
    return df


@st.cache_data(ttl=3600, show_spinner=False)
def get_fire_summary(
    date_start: date,
    date_end: date,
    states: list[str],
) -> pd.DataFrame:
    """Agrega focos de queimada por estado (soma do período)."""
    df = get_fire_data(date_start, date_end, states)
    summary = (
        df.groupby(["estado", "bioma"])
        .agg(total_focos=("focos", "sum"), media_diaria=("focos", "mean"))
        .reset_index()
    )
    summary["focos_norm"] = (
        summary["total_focos"] / summary["total_focos"].max()
    ).clip(0, 1)
    return summary
