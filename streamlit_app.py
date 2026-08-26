"""
Stock Picking World - Page d'accueil
Dashboard multi-pages pour l'analyse d'actions mondiales.
"""
import streamlit as st

st.set_page_config(
    page_title="Stock Picking World",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📊 Stock Picking World")
st.markdown("### Dashboard multi-pays / secteurs / stocks avec KPIs et backtests")

st.markdown("""
Bienvenue sur ton dashboard d'analyse actions mondiales. Utilise le menu de gauche
pour naviguer entre les 4 sections.
""")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    #### 🌍 Section 1 — Analyse des pays
    10 pays clés (USA, Chine, HK, Corée, Japon, Taiwan, Singapour, Inde, Allemagne, France).
    Score composite : momentum + valuation + macro.

    #### 🏭 Section 2 — Analyse des secteurs
    10 secteurs porteurs via ETF proxies (AI, Semiconducteurs, Quantum, Robotics, etc.).
    Module bonus : détection automatique des secteurs émergents.
    """)

with col2:
    st.markdown("""
    #### 🎯 Section 3 — Stock Picks
    Screener multi-critères (Pays × Secteur + filtres KPI).
    5 presets : Value, Growth, Quality, Dividend, Momentum.

    #### 📈 Section 4 — Backtest stratégies
    Compare 5 stratégies actions sur 10 ans vs Buy & Hold VWCE.
    """)

st.divider()

with st.expander("⚙️ Comment fonctionne ce dashboard ?"):
    st.markdown("""
    **Sources de données** :
    - Prix, fondamentaux : Yahoo Finance (lib `yfinance`)
    - Holdings ETF : yfinance
    - PIB forecasts, bond yields : base manuelle Q3 2026 (mise à jour trimestrielle recommandée)

    **Cache** : données mises en cache 1h pour éviter le rate-limiting.

    **Mises à jour** : bouton refresh dans chaque page. Automatique toutes les 24h en fond.

    **Limitation** : Streamlit Cloud gratuit = 1 GB RAM. Si l'app ralentit, réduire la liste des tickers dans chaque page.
    """)

with st.expander("📢 Disclaimer"):
    st.markdown("""
    Ce dashboard est un **outil d'aide à la décision**, PAS un conseil en investissement.

    - Les scores composites et présets sont des **heuristiques**, pas des recommandations.
    - Les performances passées ne préjugent pas des performances futures.
    - Tout investissement comporte un risque de perte en capital.
    - Consulter un conseiller financier professionnel avant toute décision d'investissement.
    """)

st.caption("Généré par Claude x Alexis — Dashboard V1")
