"""
pipelines/risk_pipeline.py
Orquestra providers → modelo de ML → DataFrame de risco por estado.
Esta é a pipeline central do AgroSentinel.
"""
import pandas as pd
from datetime import date

from providers.fire_provider    import get_fire_summary
from providers.climate_provider import get_climate_summary
from providers.ndvi_provider    import get_ndvi_summary
from models.risk_model          import predict_risk, FEATURES

# Coordenadas aproximadas dos centros dos estados (para o mapa)
STATE_COORDS = {
    "AC": (-9.02,  -70.81), "AL": (-9.57,  -36.78), "AM": (-4.13,  -63.35),
    "AP": ( 1.41,  -51.77), "BA": (-12.97, -41.71), "CE": (-5.50,  -39.32),
    "DF": (-15.78, -47.93), "ES": (-19.19, -40.34), "GO": (-15.83, -49.84),
    "MA": (-5.42,  -45.44), "MG": (-18.51, -44.55), "MS": (-20.51, -54.54),
    "MT": (-12.64, -55.42), "PA": (-3.41,  -52.29), "PB": (-7.24,  -36.78),
    "PE": (-8.38,  -37.86), "PI": (-7.72,  -42.73), "PR": (-24.89, -51.55),
    "RJ": (-22.25, -42.66), "RN": (-5.81,  -36.59), "RO": (-10.83, -63.34),
    "RR": ( 1.99,  -61.33), "RS": (-30.17, -53.50), "SC": (-27.45, -50.95),
    "SE": (-10.57, -37.45), "SP": (-22.28, -48.73), "TO": (-9.46,  -48.26),
}

# Área agrícola aproximada por estado (mil hectares) — para contexto
STATE_AREA_AGR = {
    "MT": 17500, "PR": 8200, "GO": 7800, "RS": 6500, "SP": 5800,
    "MG": 5500,  "MS": 5200, "BA": 4800, "MA": 3800, "PA": 3200,
    "TO": 2900,  "RO": 1800, "PI": 1600, "AC": 400,  "AL": 600,
    "AM": 350,   "AP": 120,  "CE": 900,  "DF": 80,   "ES": 700,
    "PB": 450,   "PE": 700,  "RJ": 350,  "RN": 500,  "RR": 250,
    "SC": 2200,  "SE": 480,
}


def build_risk_dataframe(
    date_start: date,
    date_end: date,
    states: list[str],
) -> pd.DataFrame:
    """
    Monta DataFrame completo com risco por estado, pronto para o modelo de ML.
    Integra dados de queimada, clima e NDVI.
    """
    fire_df    = get_fire_summary(date_start, date_end, states)
    climate_df = get_climate_summary(date_start, date_end, states)
    ndvi_df    = get_ndvi_summary(date_start, date_end, states)

    # Merge das três fontes
    df = fire_df.merge(climate_df, on="estado", how="left")
    df = df.merge(
        ndvi_df[["estado", "ndvi_medio", "anomalia_media"]],
        on="estado", how="left"
    )

    # Renomeia para as features do modelo
    df = df.rename(columns={
        "temp_media":  "temperatura",
        "umidade_media": "umidade",
        "prec_total":  "precipitacao",
        "vento_medio": "vento",
        "ndvi_medio":  "ndvi",
    })

    # Feature de mês (mês central do período)
    mid_date = date_start + (date_end - date_start) / 2
    df["mes"] = float(mid_date.month)

    # Garante que todas as features existem
    for feat in FEATURES:
        if feat not in df.columns:
            df[feat] = 0.0

    # Aplica o modelo de ML
    df = predict_risk(df)

    # Enriquece com coordenadas e área agrícola
    df["lat"]      = df["estado"].map(lambda s: STATE_COORDS.get(s, (0, 0))[0])
    df["lon"]      = df["estado"].map(lambda s: STATE_COORDS.get(s, (0, 0))[1])
    df["area_agr"] = df["estado"].map(lambda s: STATE_AREA_AGR.get(s, 500))

    return df
