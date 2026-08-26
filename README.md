# 📊 Stock Picking World

Dashboard multi-pages Streamlit pour l'analyse d'actions mondiales : pays, secteurs, stocks + backtests.

## 🌍 Sections

- **Pays** : Analyse macro de 10 pays clés (USA, Chine, HK, Corée, Japon, Taiwan, Singapour, Inde, Allemagne, France)
- **Secteurs** : Analyse de 10 secteurs porteurs (AI, Semiconducteurs, Quantum, Robotics, Batteries, Cloud, Cyber, Green, Biotech, Crypto)
- **Stock Picks** : Screener multi-critères + 5 presets (Value, Growth, Quality, Dividend, Momentum)
- **Backtest** : Compare 5 stratégies sur 10 ans vs Buy & Hold

## 🚀 Déploiement Streamlit Cloud

1. Fork ce repo (ou push directement)
2. Va sur https://share.streamlit.io
3. Sign in with GitHub → New app
4. Sélectionne le repo `stock-picking-world`
5. Main file : `streamlit_app.py`
6. Deploy

L'app est dispo à `https://<username>-stock-picking-world.streamlit.app`.

## 🛠 Développement local

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## 📁 Structure

```
├── streamlit_app.py      # Page d'accueil
├── requirements.txt      # Dépendances Python
├── pages/
│   ├── 1_🌍_Pays.py     # Section 1 : Analyse pays
│   ├── 2_🏭_Secteurs.py # Section 2 : Analyse secteurs
│   ├── 3_🎯_Stock_Picks.py # Section 3 : Stock picking
│   └── 4_📈_Backtest.py # Section 4 : Backtest stratégies
└── data/                # (auto-généré) cache yfinance
```

## 📊 Sources de données

- **yfinance** : prix, fondamentaux, holdings ETF
- **World Bank API** : PIB forecasts (data intégrée statiquement pour V1)
- **Base manuelle Q3 2026** : P/E médiane 10 ans par indice, bond yields
