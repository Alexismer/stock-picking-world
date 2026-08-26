"""
Section 1 : Analyse des pays
Score composite : 25% momentum + 35% cheapness + 20% PIB + 10% dette + 10% bond
"""
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

st.set_page_config(page_title="Pays", page_icon="🌍", layout="wide")

st.title("🌍 Analyse des pays")
st.caption("10 pays clés notés sur un score composite momentum + valuation + macro")

# Configuration
COUNTRIES = [
    ("USA",       "S&P 500",    "^GSPC",    "🇺🇸"),
    ("Chine",     "CSI 300",    "000300.SS","🇨🇳"),
    ("Hong Kong", "Hang Seng",  "^HSI",     "🇭🇰"),
    ("Coree Sud", "KOSPI",      "^KS11",    "🇰🇷"),
    ("Japon",     "Nikkei 225", "^N225",    "🇯🇵"),
    ("Taiwan",    "TSEC",       "^TWII",    "🇹🇼"),
    ("Singapour", "STI",        "^STI",     "🇸🇬"),
    ("Inde",      "NIFTY 50",   "^NSEI",    "🇮🇳"),
    ("Allemagne", "DAX",        "^GDAXI",   "🇩🇪"),
    ("France",    "CAC 40",     "^FCHI",    "🇫🇷"),
]

PE_MEDIAN_10Y  = {"USA":22,"Chine":12,"Hong Kong":11,"Coree Sud":13,"Japon":16,"Taiwan":15,"Singapour":13,"Inde":22,"Allemagne":14,"France":15}
PE_CURRENT     = {"USA":26,"Chine":12,"Hong Kong":10,"Coree Sud":12,"Japon":17,"Taiwan":20,"Singapour":12,"Inde":24,"Allemagne":15,"France":14}
PIB_FORECAST   = {"USA":2.3,"Chine":4.8,"Hong Kong":3.1,"Coree Sud":2.2,"Japon":1.1,"Taiwan":2.8,"Singapour":2.6,"Inde":6.7,"Allemagne":0.9,"France":1.3}
DEBT_TO_GDP    = {"USA":123,"Chine":84,"Hong Kong":38,"Coree Sud":52,"Japon":263,"Taiwan":33,"Singapour":168,"Inde":83,"Allemagne":65,"France":112}
BOND_10Y       = {"USA":4.4,"Chine":2.1,"Hong Kong":3.9,"Coree Sud":3.5,"Japon":1.6,"Taiwan":1.7,"Singapour":2.8,"Inde":6.9,"Allemagne":2.5,"France":3.1}

@st.cache_data(ttl=3600)
def fetch_perf(symbol):
    try:
        t = yf.Ticker(symbol)
        h = t.history(period="1y", interval="1d")
        if h.empty:
            return None, None, None
        closes = h["Close"]
        p_now = closes.iloc[-1]
        p_1m = closes.iloc[-22] if len(closes) >= 22 else closes.iloc[0]
        p_6m = closes.iloc[-130] if len(closes) >= 130 else closes.iloc[0]
        p_yr = closes.iloc[0]
        return (p_now - p_1m) / p_1m * 100, (p_now - p_6m) / p_6m * 100, (p_now - p_yr) / p_yr * 100
    except Exception:
        return None, None, None

# Sidebar
st.sidebar.header("⚙️ Options")
tri_mode = st.sidebar.radio("Mode de tri", ["Long terme (score)", "Tactique (momentum 6M)"])
if st.sidebar.button("🔄 Rafraîchir données"):
    st.cache_data.clear()
    st.rerun()

# Fetch data
with st.spinner("Récupération données Yahoo Finance..."):
    rows = []
    for name, idx, sym, flag in COUNTRIES:
        p1m, p6m, pyr = fetch_perf(sym)
        rows.append({
            "Rang": 0,
            "Pays": f"{flag} {name}",
            "Indice": idx,
            "Perf 1M %": p1m, "Perf 6M %": p6m, "Perf 1Y %": pyr,
            "PE actuel": PE_CURRENT.get(name),
            "PE mediane 10y": PE_MEDIAN_10Y.get(name),
            "PIB fc %": PIB_FORECAST.get(name),
            "Dette/PIB %": DEBT_TO_GDP.get(name),
            "Bond 10Y %": BOND_10Y.get(name),
        })

df = pd.DataFrame(rows)

# Score composite
p6m_vals = df["Perf 6M %"].dropna()
p6m_min = p6m_vals.min() if not p6m_vals.empty else 0
p6m_max = p6m_vals.max() if not p6m_vals.empty else 1

def compute_score(row):
    if row["Perf 6M %"] is not None and p6m_max > p6m_min:
        mom = (row["Perf 6M %"] - p6m_min) / (p6m_max - p6m_min) * 100
    else:
        mom = 50
    if row["PE mediane 10y"] > 0:
        ratio = row["PE actuel"] / row["PE mediane 10y"]
        cheap = max(0, min(100, (2 - ratio) * 50))
    else:
        cheap = 50
    pib = max(0, min(100, (row["PIB fc %"] or 0) * 100 / 7))
    debt_score = max(0, min(100, 100 - (row["Dette/PIB %"] or 100) / 3))
    bond_stab = max(0, min(100, 100 - abs((row["Bond 10Y %"] or 4) - 3) * 15))
    return round(0.25*mom + 0.35*cheap + 0.20*pib + 0.10*debt_score + 0.10*bond_stab)

df["Score /100"] = df.apply(compute_score, axis=1)

# Tri
if tri_mode == "Long terme (score)":
    df = df.sort_values("Score /100", ascending=False).reset_index(drop=True)
else:
    df = df.sort_values("Perf 6M %", ascending=False).reset_index(drop=True)
df["Rang"] = df.index + 1

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Score /100": st.column_config.ProgressColumn("Score /100", min_value=0, max_value=100, format="%d"),
        "Perf 1M %": st.column_config.NumberColumn(format="%+.1f%%"),
        "Perf 6M %": st.column_config.NumberColumn(format="%+.1f%%"),
        "Perf 1Y %": st.column_config.NumberColumn(format="%+.1f%%"),
        "PIB fc %":  st.column_config.NumberColumn(format="%+.1f%%"),
        "Bond 10Y %":st.column_config.NumberColumn(format="%.1f%%"),
    },
)

# Insights auto
st.markdown("### 📌 Insights auto")
top3 = df.head(3)
worst3 = df.tail(3)
c1, c2 = st.columns(2)
with c1:
    st.success(f"**Top 3** : {', '.join(top3['Pays'])}")
    st.write("Ces pays combinent momentum, valuation raisonnable et macro solide.")
with c2:
    st.error(f"**Flop 3** : {', '.join(worst3['Pays'])}")
    st.write("À éviter ou attendre un rebond confirmé.")

with st.expander("📖 Formule du score composite"):
    st.markdown("""
    **Score /100** = pondération de 5 dimensions :
    - **25% Momentum 6M** — normalisé sur les 10 pays
    - **35% Cheapness** — PE actuel vs médiane 10 ans (bas = cheap)
    - **20% Croissance PIB** — forecast IMF 12 mois
    - **10% Santé fiscale** — inverse ratio Dette/PIB (bas = bon)
    - **10% Bond 10Y stable** — pénalise les taux extrêmes (haut ou bas)

    **Bond 10Y stable** : un pays avec taux à 3% (proche norme historique) est "stable". Taux à 7% (Inde) = risque inflation, taux à 1% (Japon) = économie stagnante.
    """)

st.caption(f"Données mises à jour : {datetime.now().strftime('%Y-%m-%d %H:%M')} | Sources : Yahoo Finance + base manuelle Q3 2026")
