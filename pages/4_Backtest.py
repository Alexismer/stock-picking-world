"""
Section 4 : Backtest 5 stratégies actions vs Buy & Hold Monde
Utilise les ETF factor investing (Value, Growth, Quality, Dividend, Momentum) comme proxies.
"""
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Backtest", page_icon="📈", layout="wide")

st.title("📈 Backtest 5 stratégies vs Buy & Hold Monde")
st.caption("Compare Value / Growth / Quality / Dividend / Momentum vs ETF Monde sur 10 ans")

# Stratégies via ETF factor investing (proxies éprouvés)
STRATEGIES = [
    ("Buy & Hold Monde", "VT",   "Vanguard Total World Stock",       "#1a3a52"),
    ("Value",            "SPYV", "SPDR S&P 500 Value",               "#4A90E2"),
    ("Growth",           "SPYG", "SPDR S&P 500 Growth",              "#4a9c3a"),
    ("Quality",          "QUAL", "iShares MSCI USA Quality Factor",  "#e8a86a"),
    ("Dividend Aristo",  "NOBL", "ProShares S&P 500 Dividend Aristo","#c93838"),
    ("Momentum",         "MTUM", "iShares MSCI USA Momentum",        "#8e44ad"),
]

@st.cache_data(ttl=3600)
def fetch_history(sym, years=10):
    try:
        t = yf.Ticker(sym)
        h = t.history(period=f"{years}y", interval="1mo")
        if h.empty:
            return None
        return h["Close"]
    except Exception:
        return None

# Sidebar
st.sidebar.header("⚙️ Paramètres")
years = st.sidebar.slider("Horizon backtest (années)", 3, 10, 10)
initial_amount = st.sidebar.number_input("Investissement initial ($)", 1000, 100000, 10000, 1000)
mode = st.sidebar.radio("Mode", ["Lump sum (tout au début)", "DCA mensuel ($100/mois)"])
if st.sidebar.button("🔄 Rafraîchir"):
    st.cache_data.clear()
    st.rerun()

# Fetch data
with st.spinner(f"Récupération {years} ans d'historique..."):
    data = {}
    for name, sym, desc, color in STRATEGIES:
        h = fetch_history(sym, years)
        if h is not None and len(h) >= 12:
            data[name] = {"prices": h, "color": color, "desc": desc, "ticker": sym}

if not data:
    st.error("Aucune donnée disponible. Réessaie plus tard.")
    st.stop()

# Simulation
def simulate_lump_sum(prices, initial):
    if len(prices) < 2:
        return None, None, None
    shares = initial / prices.iloc[0]
    values = shares * prices
    return values, values.iloc[-1], (values.iloc[-1] - initial) / initial * 100

def simulate_dca(prices, monthly=100):
    if len(prices) < 2:
        return None, None, None
    total_invested = 0
    shares = 0
    values = []
    for price in prices:
        shares += monthly / price
        total_invested += monthly
        values.append(shares * price)
    final_value = values[-1]
    total_return = (final_value - total_invested) / total_invested * 100
    return pd.Series(values, index=prices.index), final_value, total_return

# Compute results
results = []
curves = {}
for name, d in data.items():
    prices = d["prices"]
    if mode.startswith("Lump"):
        curve, final, ret = simulate_lump_sum(prices, initial_amount)
        invested = initial_amount
    else:
        curve, final, ret = simulate_dca(prices, 100)
        invested = 100 * len(prices)
    if curve is None:
        continue
    # Metrics
    curve_pct = (curve / curve.iloc[0]) if mode.startswith("Lump") else (curve / (100 * pd.Series(range(1, len(curve)+1), index=curve.index)))
    monthly_returns = prices.pct_change().dropna()
    cagr = (final / invested) ** (1/(len(prices)/12)) - 1 if invested > 0 else 0
    max_dd = ((curve - curve.cummax()) / curve.cummax()).min() * 100
    vol = monthly_returns.std() * np.sqrt(12) * 100
    sharpe = (monthly_returns.mean() * 12) / (monthly_returns.std() * np.sqrt(12)) if monthly_returns.std() > 0 else 0
    results.append({
        "Stratégie": name,
        "ETF": d["ticker"],
        "Investi $": invested,
        "Final $": final,
        "Rendement total %": ret,
        "CAGR %": cagr * 100,
        "Max Drawdown %": max_dd,
        "Volatilité annuelle %": vol,
        "Sharpe ratio": sharpe,
    })
    curves[name] = curve

df = pd.DataFrame(results).sort_values("CAGR %", ascending=False).reset_index(drop=True)

# Tableau résultats
st.subheader("📊 Résultats comparatifs")
st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Investi $": st.column_config.NumberColumn(format="$%.0f"),
        "Final $": st.column_config.NumberColumn(format="$%.0f"),
        "Rendement total %": st.column_config.NumberColumn(format="%+.1f%%"),
        "CAGR %": st.column_config.NumberColumn(format="%+.2f%%"),
        "Max Drawdown %": st.column_config.NumberColumn(format="%.1f%%"),
        "Volatilité annuelle %": st.column_config.NumberColumn(format="%.1f%%"),
        "Sharpe ratio": st.column_config.NumberColumn(format="%.2f"),
    },
)

# Graphique croissance
st.subheader("📈 Croissance des portefeuilles")
fig = go.Figure()
for name, curve in curves.items():
    color = data[name]["color"]
    fig.add_trace(go.Scatter(x=curve.index, y=curve.values, mode='lines',
                             name=name, line=dict(color=color, width=2)))
fig.update_layout(
    xaxis_title="Date", yaxis_title="Valeur portefeuille ($)",
    template="plotly_white", height=500,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)
st.plotly_chart(fig, use_container_width=True)

# Insights
st.subheader("📌 Insights")
best = df.iloc[0]
worst = df.iloc[-1]
baseline = df[df["Stratégie"] == "Buy & Hold Monde"].iloc[0] if "Buy & Hold Monde" in df["Stratégie"].values else None

c1, c2, c3 = st.columns(3)
c1.metric("🥇 Meilleure stratégie", best["Stratégie"], f"CAGR {best['CAGR %']:+.2f}%")
c2.metric("🔻 Pire stratégie", worst["Stratégie"], f"CAGR {worst['CAGR %']:+.2f}%")
if baseline is not None:
    n_beat = sum(1 for _, r in df.iterrows() if r["CAGR %"] > baseline["CAGR %"])
    c3.metric("Stratégies battant Buy & Hold Monde", f"{n_beat}/{len(df)-1}",
              f"vs {baseline['CAGR %']:+.2f}% baseline")

with st.expander("📖 Méthodologie du backtest"):
    st.markdown("""
    **Proxies ETF factor investing utilisés** :
    - Buy & Hold Monde → **VT** (Vanguard Total World, exposition globale)
    - Value → **SPYV** (SPDR S&P 500 Value)
    - Growth → **SPYG** (SPDR S&P 500 Growth)
    - Quality → **QUAL** (iShares MSCI USA Quality)
    - Dividend → **NOBL** (Dividend Aristocrats 25+ ans)
    - Momentum → **MTUM** (iShares MSCI USA Momentum)

    Ces ETF sont les **implémentations institutionnelles** des factor strategies (Fama-French, MSCI factor investing).
    Backtester ces ETF = backtester les stratégies elles-mêmes, sans avoir à sélectionner les stocks manuellement.

    **Modes** :
    - **Lump sum** : tu investis toute la somme au début, tu tiens
    - **DCA mensuel** : tu investis $100/mois à date fixe (achat prix moyen)

    **Métriques** :
    - **CAGR** = rendement annualisé composé (le vrai indicateur long terme)
    - **Max Drawdown** = pire chute depuis un plus haut (mesure du stress)
    - **Sharpe ratio** = rendement / risque (>1 = bon, >2 = excellent)

    **Attention** : les performances passées ne préjugent pas des futures. Ces ETF sont US-centric (biais MSCI USA).
    """)

st.caption(f"Données mises à jour : {datetime.now().strftime('%Y-%m-%d %H:%M')} | Source : Yahoo Finance")
