"""
Section 2 : Analyse des secteurs
10 ETF proxies + module bonus "Secteurs émergents" (nouveaux ETF thématiques).
"""
import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime

st.set_page_config(page_title="Secteurs", page_icon="🏭", layout="wide")

st.title("🏭 Analyse des secteurs")
st.caption("10 secteurs porteurs via ETF proxies + détection secteurs émergents")

SECTORS_MAIN = [
    ("AI",              "BOTZ", "Global X Robotics & AI ETF",   100),
    ("Semiconducteurs", "SOXX", "iShares Semiconductor ETF",     95),
    ("Quantum",         "QTUM", "Defiance Quantum ETF",          85),
    ("Robotics",        "ROBO", "ROBO Global Robotics ETF",      80),
    ("Batteries/EV",    "LIT",  "Global X Lithium & Battery",    75),
    ("Cloud",           "WCLD", "WisdomTree Cloud Computing",    75),
    ("Cybersecurite",   "CIBR", "First Trust Cybersecurity",     85),
    ("Green Energy",    "ICLN", "iShares Global Clean Energy",   60),
    ("Biotech",         "XBI",  "SPDR S&P Biotech",              70),
    ("Crypto Equity",   "COIN", "Coinbase (proxy crypto)",       80),
]

# ETF thématiques récents (pour la section "émergents")
EMERGING_ETFS = [
    ("Space & Defense",    "UFO",  "Procure Space ETF"),
    ("Genomics",           "ARKG", "ARK Genomic Revolution"),
    ("Fintech",            "ARKF", "ARK Fintech Innovation"),
    ("3D Printing",        "PRNT", "3D Printing ETF"),
    ("Metaverse",          "META_metaverse", "Roundhill Ball Metaverse"),
    ("Nuclear Energy",     "URNM", "Sprott Uranium Miners"),
    ("Water & Infra",      "PHO",  "Invesco Water Resources"),
    ("Autonomous Driving", "DRIV", "Global X Autonomous EV"),
]

@st.cache_data(ttl=3600)
def fetch_sector_data(sym):
    try:
        t = yf.Ticker(sym)
        h = t.history(period="1y", interval="1d")
        if h.empty:
            return None
        closes = h["Close"]
        p_now = closes.iloc[-1]
        p_1m = closes.iloc[-22] if len(closes) >= 22 else closes.iloc[0]
        p_6m = closes.iloc[-130] if len(closes) >= 130 else closes.iloc[0]
        p_ytd = closes.iloc[-min(300, len(closes)-1)]
        # RSI simple 14j
        delta = closes.diff().dropna().tail(14)
        gains = delta.where(delta > 0, 0).mean()
        losses = -delta.where(delta < 0, 0).mean()
        rsi = 100 - 100 / (1 + gains/losses) if losses > 0 else 50
        return {
            "perf_1m": (p_now - p_1m) / p_1m * 100,
            "perf_6m": (p_now - p_6m) / p_6m * 100,
            "perf_ytd": (p_now - p_ytd) / p_ytd * 100,
            "rsi": round(rsi),
            "price": float(p_now),
        }
    except Exception:
        return None

@st.cache_data(ttl=3600)
def fetch_top_holdings(sym, n=5):
    """Récupère les top N holdings d'un ETF via yfinance."""
    try:
        t = yf.Ticker(sym)
        # yfinance ne donne pas toujours les holdings directement.
        # On tente via .funds_data (yfinance 0.2+)
        info = t.info
        # Fallback : nom + brief
        return info.get("longBusinessSummary", "N/A")[:200]
    except Exception:
        return "N/A"

st.sidebar.header("⚙️ Options")
show_emerging = st.sidebar.checkbox("Afficher secteurs émergents", value=True)
if st.sidebar.button("🔄 Rafraîchir données"):
    st.cache_data.clear()
    st.rerun()

# Section principale
st.subheader("📊 10 secteurs porteurs (base)")
with st.spinner("Récupération ETFs..."):
    rows = []
    for name, sym, desc, future_pot in SECTORS_MAIN:
        d = fetch_sector_data(sym)
        if not d:
            rows.append({"Secteur": name, "ETF": sym, "Prix": None, "Perf 1M %": None,
                        "Perf 6M %": None, "Perf YTD %": None, "RSI": 50,
                        "Future potential": future_pot, "Score /100": 0})
            continue
        # Score composite : 30% perf 6M + 30% future_pot + 20% RSI mid + 20% perf YTD
        perf_6m_norm = max(0, min(100, d["perf_6m"] * 2 + 50))
        perf_ytd_norm = max(0, min(100, d["perf_ytd"] * 1.5 + 50))
        rsi_score = 100 - abs(d["rsi"] - 50) * 2
        score = round(0.30*perf_6m_norm + 0.30*future_pot + 0.20*rsi_score + 0.20*perf_ytd_norm)
        rows.append({
            "Secteur": name, "ETF": sym, "Description": desc,
            "Prix": d["price"], "Perf 1M %": d["perf_1m"], "Perf 6M %": d["perf_6m"],
            "Perf YTD %": d["perf_ytd"], "RSI": d["rsi"],
            "Future potential": future_pot, "Score /100": score,
        })

df = pd.DataFrame(rows).sort_values("Score /100", ascending=False).reset_index(drop=True)

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Score /100": st.column_config.ProgressColumn("Score /100", min_value=0, max_value=100, format="%d"),
        "Perf 1M %": st.column_config.NumberColumn(format="%+.1f%%"),
        "Perf 6M %": st.column_config.NumberColumn(format="%+.1f%%"),
        "Perf YTD %": st.column_config.NumberColumn(format="%+.1f%%"),
        "Prix": st.column_config.NumberColumn(format="$%.2f"),
        "Future potential": st.column_config.ProgressColumn("Future pot.", min_value=0, max_value=100, format="%d"),
    },
)

# Top 3 insights
top3 = df.head(3)
st.success(f"**🏆 Top 3 secteurs** : {', '.join(top3['Secteur'])}")

# Section Emerging
if show_emerging:
    st.divider()
    st.subheader("🚀 Secteurs émergents (ETFs thématiques récents)")
    st.caption("Détection auto : perf 6M des ETF thématiques nouvellement lancés")
    with st.spinner("Analyse ETFs émergents..."):
        emerging_rows = []
        for name, sym, desc in EMERGING_ETFS:
            d = fetch_sector_data(sym)
            if not d:
                continue
            emerging_rows.append({
                "Thème": name, "ETF": sym, "Description": desc,
                "Perf 6M %": d["perf_6m"], "Perf YTD %": d["perf_ytd"],
                "RSI": d["rsi"],
            })
    if emerging_rows:
        df_em = pd.DataFrame(emerging_rows).sort_values("Perf 6M %", ascending=False).reset_index(drop=True)
        st.dataframe(df_em, use_container_width=True, hide_index=True,
                     column_config={"Perf 6M %": st.column_config.NumberColumn(format="%+.1f%%"),
                                    "Perf YTD %": st.column_config.NumberColumn(format="%+.1f%%")})
        top_em = df_em.head(3)
        st.info(f"**Thèmes émergents à surveiller** : {', '.join(top_em['Thème'])}")
    else:
        st.warning("Données ETFs émergents indisponibles pour le moment.")

with st.expander("📖 Formule du score composite"):
    st.markdown("""
    **Score /100** = pondération de 4 dimensions :
    - **30% Performance 6M** — momentum du secteur (normalisé)
    - **30% Future potential** — score subjectif de potentiel long terme (à ajuster manuellement dans le code selon tes convictions)
    - **20% RSI mid-range** — récompense les secteurs qui ne sont ni oversold ni overbought (RSI 30-70 = idéal)
    - **20% Performance YTD** — cohérence sur l'année

    **Pourquoi RSI mid ?** Un secteur avec RSI > 80 = déjà chauffé, risque de correction. RSI < 20 = capitulation, timing incertain. RSI 40-60 = zone de "trend healthy".
    """)

st.caption(f"Données mises à jour : {datetime.now().strftime('%Y-%m-%d %H:%M')}")
