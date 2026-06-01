"""
models/risk_model.py
Modelo de classificação de risco agroclimático.
RandomForestClassifier treinado com dados sintéticos que simulam
padrões históricos do INPE + INMET para o Brasil.

Features de entrada:
  - focos_norm:    focos de queimada normalizados (0-1)
  - temperatura:   temperatura média do período (°C)
  - umidade:       umidade relativa média (%)
  - precipitacao:  precipitação total do período (mm)
  - vento:         velocidade média do vento (km/h)
  - ndvi:          índice de vegetação NDVI (0-1)
  - mes:           mês do ano (1-12)

Saída: probabilidade de risco alto (0-1)
Classes: 0=baixo, 1=moderado, 2=alto, 3=crítico
"""
import numpy as np
import pandas as pd
import streamlit as st
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline


FEATURES = [
    "focos_norm", "temperatura", "umidade",
    "precipitacao", "vento", "ndvi", "mes",
]

RISK_CLASSES = {0: "Baixo", 1: "Moderado", 2: "Alto", 3: "Crítico"}
RISK_THRESHOLDS = [0.25, 0.50, 0.75]  # limites para classes


def _generate_training_data(n_samples: int = 4000) -> tuple[np.ndarray, np.ndarray]:
    """
    Gera dataset sintético para treino baseado em relações
    físicas reais entre as variáveis e risco de incêndio.
    """
    rng = np.random.default_rng(42)

    focos_norm   = rng.beta(1.5, 4, n_samples)       # concentrado em valores baixos
    temperatura  = rng.normal(25, 5, n_samples).clip(15, 42)
    umidade      = rng.normal(55, 20, n_samples).clip(10, 95)
    precipitacao = rng.exponential(60, n_samples)
    vento        = rng.normal(15, 7, n_samples).clip(0, 60)
    ndvi         = rng.beta(4, 2, n_samples)          # concentrado em valores altos
    mes          = rng.integers(1, 13, n_samples).astype(float)

    X = np.column_stack([
        focos_norm, temperatura, umidade,
        precipitacao, vento, ndvi, mes,
    ])

    # Regra de risco composta (simula lógica do perito)
    risco_continuo = (
        0.35 * focos_norm
        + 0.25 * (temperatura - 15) / 27       # normaliza 15-42°C
        + 0.20 * (1 - umidade / 95)            # umidade inversa
        + 0.10 * (1 - np.clip(precipitacao / 200, 0, 1))
        + 0.05 * vento / 60
        + 0.05 * (1 - ndvi)                   # vegetação seca
    )

    # Sazonalidade: meses secos (maio–outubro) aumentam risco
    sazonalidade = np.where((mes >= 5) & (mes <= 10), 0.1, -0.05)
    risco_continuo = np.clip(risco_continuo + sazonalidade + rng.normal(0, 0.03, n_samples), 0, 1)

    # Discretiza em 4 classes
    y = np.digitize(risco_continuo, RISK_THRESHOLDS)

    return X, y


@st.cache_resource(show_spinner=False)
def load_model() -> Pipeline:
    """
    Treina (ou carrega do cache) o pipeline de ML.
    @st.cache_resource garante que o modelo só é treinado uma vez.
    """
    X_train, y_train = _generate_training_data(4000)

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", RandomForestClassifier(
            n_estimators=200,
            max_depth=8,
            min_samples_leaf=10,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        )),
    ])

    pipeline.fit(X_train, y_train)
    return pipeline


def predict_risk(features_df: pd.DataFrame) -> pd.DataFrame:
    """
    Recebe DataFrame com colunas = FEATURES e retorna:
      - risk_class:  0-3
      - risk_label:  Baixo/Moderado/Alto/Crítico
      - risk_score:  probabilidade da classe predita (0-1)
      - risk_proba_critico: probabilidade de risco crítico
    """
    model = load_model()
    X = features_df[FEATURES].values

    classes    = model.predict(X)
    probas     = model.predict_proba(X)   # shape (n, 4)

    # Probabilidade de ser Alto ou Crítico (classes 2 e 3)
    risk_score = probas[:, 2] + probas[:, 3]

    result = features_df.copy()
    result["risk_class"]         = classes
    result["risk_label"]         = [RISK_CLASSES[c] for c in classes]
    result["risk_score"]         = risk_score.round(3)
    result["risk_proba_critico"] = probas[:, 3].round(3)

    return result


def get_feature_importances() -> pd.DataFrame:
    """Retorna importâncias das features para exibir no dashboard."""
    model = load_model()
    clf = model.named_steps["clf"]
    labels_pt = {
        "focos_norm":   "Focos de queimada",
        "temperatura":  "Temperatura",
        "umidade":      "Umidade relativa",
        "precipitacao": "Precipitação",
        "vento":        "Velocidade do vento",
        "ndvi":         "Índice de vegetação (NDVI)",
        "mes":          "Mês do ano",
    }
    return pd.DataFrame({
        "feature":    [labels_pt[f] for f in FEATURES],
        "importance": clf.feature_importances_,
    }).sort_values("importance", ascending=False)
