# 🌿 AgroSentinel

**Dashboard interativo de monitoramento de risco agroclimático para o Brasil.**

Desenvolvido como Global Solution 2026/1 — Disciplina de Front-End & Mobile Development em Sistemas de IA — FIAP Tecnólogo em Inteligência Artificial.

---

## 🎯 O Problema

Eventos climáticos extremos, secas prolongadas e queimadas impõem perdas bilionárias à agricultura brasileira anualmente. Gestores rurais, Defesa Civil e órgãos ambientais precisam de informação acionável em tempo real — não de planilhas estáticas ou relatórios atrasados.

O AgroSentinel cruza **três fontes de dados** (focos de queimada INPE, dados climáticos Open-Meteo e índice de vegetação NDVI via Sentinel-2) e aplica um **modelo de Machine Learning** para calcular um **Índice de Risco Agroclimático** por estado brasileiro, guiando o usuário do panorama nacional até a decisão de envio de alertas.

---

## 🏗️ Arquitetura

```
agrosentinel/
├── app.py                          # Entrypoint — ~30 linhas, só orquestra
├── providers/                      # Acesso a dados externos (HTTP / mock)
│   ├── fire_provider.py            # INPE / BDQueimadas
│   ├── climate_provider.py         # Open-Meteo API
│   └── ndvi_provider.py            # Sentinel-2 (NDVI por bioma)
├── pipelines/                      # Transformação e orquestração
│   ├── risk_pipeline.py            # Integra providers → modelo ML
│   ├── alert_pipeline.py           # Geração de alertas por threshold
│   └── ndvi_pipeline.py            # Agregação temporal de NDVI
├── models/
│   └── risk_model.py               # RandomForestClassifier (scikit-learn)
├── state/                          # Gerenciamento de session_state
│   ├── session.py                  # Init e getters centralizados
│   ├── filters.py                  # Estado dos filtros ativos
│   └── alerts.py                   # Decisões HITL
├── features/                       # Telas separadas por responsabilidade
│   ├── panorama/page.py            # Mapa nacional + KPIs
│   ├── alertas/page.py             # Painel Human-in-the-Loop
│   ├── analise/page.py             # Série temporal + NDVI + clima
│   └── relatorio/page.py           # Resumo executivo
└── ui/
    ├── theme.py                    # CSS global + configuração de página
    ├── components/
    │   ├── kpi_card.py             # KPI card reutilizável (panorama + relatório)
    │   └── risk_gauge.py           # Gauge velocímetro (panorama + analise)
    ├── charts/
    │   ├── plotly_map.py           # Mapa coroplético reutilizável
    │   └── time_series.py          # Série temporal reutilizável (analise + relatório)
    └── sidebar/
        └── filters.py              # 5 filtros interativos centralizados
```

---

## 🤖 Modelo de Machine Learning

**Algoritmo:** `RandomForestClassifier` (scikit-learn)

**Features (7):**
| Feature | Fonte |
|---|---|
| Focos de queimada normalizados | INPE / BDQueimadas |
| Temperatura média (°C) | Open-Meteo |
| Umidade relativa (%) | Open-Meteo |
| Precipitação acumulada (mm) | Open-Meteo |
| Velocidade do vento (km/h) | Open-Meteo |
| NDVI médio (índice de vegetação) | Sentinel-2 / Copernicus |
| Mês do ano | — |

**Saída:** Probabilidade de risco alto ou crítico (0–1)
**Classes:** Baixo · Moderado · Alto · Crítico

O modelo é treinado automaticamente na inicialização e cacheado com `@st.cache_resource`, garantindo que nenhum re-treinamento ocorra durante a sessão.

---

## ✅ Requisitos técnicos atendidos

| Requisito | Implementação |
|---|---|
| Framework Streamlit | `app.py` com `st.session_state`, `@st.cache_data`, `@st.cache_resource` |
| Arquitetura em camadas | `providers/`, `pipelines/`, `state/`, `features/`, `ui/` |
| ≥ 3 filtros interativos | **5 filtros**: datas, bioma, estados, threshold de risco, cultura |
| ≥ 2 visualizações Plotly | Mapa coroplético, gauge, scatter, séries temporais, bar chart |
| Componentização real | `kpi_card.py` e `time_series.py` invocados em 2+ features com parâmetros diferentes |
| Layout organizado | Tabs, colunas, sidebar e expanders |
| Design para latência | Skeleton loaders + `st.spinner` nas pipelines |
| Cores semânticas | Verde→Amarelo→Laranja→Vermelho em todos os gráficos |
| Human-in-the-Loop | Painel completo de aprovação/descarte de alertas com reversão |
| **Modelo de IA (diferencial)** | RandomForestClassifier integrado na pipeline de risco |

---

## 🚀 Instalação e execução

```bash
# Clone o repositório
git clone https://github.com/SEU_USUARIO/agrosentinel.git
cd agrosentinel

# Crie e ative um ambiente virtual
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows

# Instale as dependências
pip install -r requirements.txt

# Execute o dashboard
streamlit run app.py
```

O app estará disponível em `http://localhost:8501`.

---

## ☁️ Deploy no Streamlit Cloud

1. Faça fork/push do repositório para o GitHub
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Conecte o repositório e selecione `app.py` como entrypoint
4. Clique em **Deploy** — o Streamlit Cloud instala o `requirements.txt` automaticamente

---

## 📊 Fontes de dados

| Fonte | Dados | Status |
|---|---|---|
| [INPE / BDQueimadas](https://queimadas.dgi.inpe.br/) | Focos de queimada | Simulado com padrões históricos |
| [Open-Meteo](https://open-meteo.com/) | Temperatura, umidade, precipitação, vento | Simulado com perfis climatológicos |
| [Sentinel-2 / Copernicus](https://www.copernicus.eu/) | NDVI por bioma | Simulado com perfis por bioma |

Em produção, substituir os providers simulados pelas APIs reais das fontes acima.

---

## 👥 Grupo

| Nome | RM |
|---|---|
| [NOME 1] | [RM] |
| [NOME 2] | [RM] |
| [NOME 3] | [RM] |

**FIAP — Tecnólogo em Inteligência Artificial — 2TIAPF — Global Solution 2026/1**
