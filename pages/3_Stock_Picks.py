"""
Section 3 : Stock Picks
Screener multi-critères + 5 presets (Value, Growth, Quality, Dividend, Momentum).
"""
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

st.set_page_config(page_title="Stock Picks", page_icon="🎯", layout="wide")

st.title("🎯 Stock Picks")
st.caption("Screener multi-critères + 5 presets (Value, Growth, Quality, Dividend, Momentum)")

# Watchlist ~50 stocks emblématiques (mid/large cap par pays × secteur)
STOCKS = [
    # USA - AI/Tech
    ("NVDA","USA","Semiconducteurs"), ("MSFT","USA","AI/Cloud"), ("GOOGL","USA","AI/Cloud"),
    ("META","USA","AI/Cloud"), ("AAPL","USA","Consumer Tech"), ("AMZN","USA","E-commerce"),
    ("AVGO","USA","Semiconducteurs"), ("AMD","USA","Semiconducteurs"), ("PLTR","USA","AI/Data"),
    ("CRM","USA","Cloud"), ("SNOW","USA","Cloud"), ("PANW","USA","Cybersecurite"),
    ("CRWD","USA","Cybersecurite"), ("TSLA","USA","EV/Batteries"), ("MRNA","USA","Biotech"),
    ("REGN","USA","Biotech"), ("COIN","USA","Crypto"), ("MSTR","USA","Crypto"),
    ("BRK-B","USA","Holding"), ("JPM","USA","Finance"), ("V","USA","Payments"),
    # Taiwan
    ("TSM","Taiwan","Semiconducteurs"),
    # Coree
    ("005930.KS","Coree Sud","Semiconducteurs"), ("000660.KS","Coree Sud","Semiconducteurs"),
    # Japon
    ("6954.T","Japon","Robotics"), ("6506.T","Japon","Robotics"), ("7203.T","Japon","Auto"),
    # Chine/HK
    ("BABA","Chine","AI/Cloud"), ("TCEHY","Chine","AI/Cloud"), ("BYDDY","Chine","EV/Batteries"),
    ("JD","Chine","E-commerce"), ("PDD","Chine","E-commerce"),
    # Inde
    ("INFY","Inde","IT Services"), ("HDB","Inde","Finance"),
    # Europe
    ("ASML","Europe","Semiconducteurs"), ("SAP","Allemagne","Cloud"),
    ("SIE.DE","Allemagne","Robotics"), ("MC.PA","France","Luxe"),
    ("OR.PA","France","Cosmetics"), ("AIR.PA","France","Aerospace"),
    ("NESN.SW","Suisse","Consumer"), ("NOVN.SW","Suisse","Biotech"),
    # Singapour
    ("DBS.SI","Singapour","Finance"),
]

@st.cache_data(ttl=3600)
def fetch_stock_data(ticker):
    """Récupère fondamentaux + prix + perf via yfinance."""
    try:
        t = yf.Ticker(ticker)
        info = t.info
        h = t.history(period="6mo", interval="1d")
        if h.empty:
            perf_6m = None
            perf_1m = None
        else:
            closes = h["Close"]
            p_now = closes.iloc[-1]
            p_1m = closes.iloc[-22] if len(closes) >= 22 else closes.iloc[0]
            p_6m = closes.iloc[0]
            perf_6m = (p_now - p_6m) / p_6m * 100
            perf_1m = (p_now - p_1m) / p_1m * 100
        return {
            "name": info.get("shortName") or info.get("longName") or ticker,
            "price": info.get("currentPrice") or info.get("regularMarketPrice"),
            "pe": info.get("trailingPE"),
            "pe_fwd": info.get("forwardPE"),
            "roe": info.get("returnOnEquity"),
            "profit_margin": info.get("profitMargins"),
            "revenue_growth": info.get("revenueGrowth"),
            "dividend_yield": info.get("dividendYield"),
            "debt_to_equity": info.get("debtToEquity"),
            "market_cap": info.get("marketCap"),
            "perf_1m": perf_1m,
            "perf_6m": perf_6m,
        }
    except Exception:
        return {}

# Sidebar - Filtres
st.sidebar.header("🎛️ Filtres")
countries_avail = sorted(set(s[1] for s in STOCKS))
sectors_avail = sorted(set(s[2] for s in STOCKS))
sel_countries = st.sidebar.multiselect("Pays", countries_avail, default=countries_avail)
sel_sectors   = st.sidebar.multiselect("Secteurs", sectors_avail, default=sectors_avail)

pe_max = st.sidebar.slider("PE max", 0, 200, 60)
roe_min = st.sidebar.slider("ROE min %", -50, 100, 0)
growth_min = st.sidebar.slider("Croissance revenus min %", -50, 100, -10)
div_min = st.sidebar.slider("Dividend yield min %", 0.0, 10.0, 0.0, 0.5)
perf_min = st.sidebar.slider("Perf 6M min %", -50, 200, -30)

st.sidebar.divider()
st.sidebar.header("🎁 Presets")
preset = st.sidebar.radio("Preset rapide", ["Aucun", "Value", "Growth", "Quality", "Dividend", "Momentum"])

if st.sidebar.button("🔄 Rafraîchir"):
    st.cache_data.clear()
    st.rerun()

# Application préset
if preset == "Value":
    pe_max, roe_min, growth_min, div_min, perf_min = 20, 15, 0, 0, -30
elif preset == "Growth":
    pe_max, roe_min, growth_min, div_min, perf_min = 100, 5, 20, 0, 0
elif preset == "Quality":
    pe_max, roe_min, growth_min, div_min, perf_min = 40, 20, 5, 0, -20
elif preset == "Dividend":
    pe_max, roe_min, growth_min, div_min, perf_min = 30, 5, 0, 2.5, -20
elif preset == "Momentum":
    pe_max, roe_min, growth_min, div_min, perf_min = 200, -10, 0, 0, 15

# Fetch data
with st.spinner("Récupération données stocks (30-60s)..."):
    rows = []
    for ticker, country, sector in STOCKS:
        if country not in sel_countries or sector not in sel_sectors:
            continue
        d = fetch_stock_data(ticker)
        if not d:
            continue
        # Filtres
        pe = d.get("pe") or 999
        roe = (d.get("roe") or -1) * 100
        growth = (d.get("revenue_growth") or -1) * 100
        div = (d.get("dividend_yield") or 0) * 100
        perf = d.get("perf_6m") or -100
        if pe > pe_max: continue
        if roe < roe_min: continue
        if growth < growth_min: continue
        if div < div_min: continue
        if perf < perf_min: continue
        # Score composite : 25% cheap + 25% quality + 25% growth + 25% momentum
        cheap_s = max(0, min(100, (30 - pe) * 3.3))
        qual_s = max(0, min(100, roe * 2 + (d.get("profit_margin") or 0) * 100))
        growth_s = max(0, min(100, growth * 4))
        mom_s = max(0, min(100, perf * 2 + 50))
        score = round(0.25*cheap_s + 0.25*qual_s + 0.25*growth_s + 0.25*mom_s)
        rows.append({
            "Ticker": ticker,
            "Nom": d["name"][:30],
            "Pays": country,
            "Secteur": sector,
            "Prix $": d["price"],
            "PE": d["pe"],
            "ROE %": roe if roe > -50 else None,
            "Marge %": (d.get("profit_margin") or 0) * 100,
            "Growth %": growth,
            "Dividend %": div,
            "Debt/Eq": d.get("debt_to_equity"),
            "Perf 6M %": d.get("perf_6m"),
            "Cap $B": (d.get("market_cap") or 0) / 1e9,
            "Score /100": score,
        })

df = pd.DataFrame(rows)
if df.empty:
    st.warning("Aucun stock ne matche tes filtres. Assouplis les critères ou change de preset.")
else:
    df = df.sort_values("Score /100", ascending=False).reset_index(drop=True)
    st.info(f"**{len(df)} stocks match** avec les filtres actuels (preset : {preset})")
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Score /100": st.column_config.ProgressColumn("Score /100", min_value=0, max_value=100, format="%d"),
            "Prix $": st.column_config.NumberColumn(format="$%.2f"),
            "PE": st.column_config.NumberColumn(format="%.1f"),
            "ROE %": st.column_config.NumberColumn(format="%.1f%%"),
            "Marge %": st.column_config.NumberColumn(format="%.1f%%"),
            "Growth %": st.column_config.NumberColumn(format="%+.1f%%"),
            "Dividend %": st.column_config.NumberColumn(format="%.2f%%"),
            "Perf 6M %": st.column_config.NumberColumn(format="%+.1f%%"),
            "Cap $B": st.column_config.NumberColumn(format="%.0f B"),
        },
    )
    st.markdown(f"**🥇 Top 3 selon score** : {' | '.join(df.head(3)['Ticker'].tolist())}")

with st.expander("📖 Explication des presets"):
    st.markdown("""
    - **Value** : PE<20 + ROE>15% — actions sous-évaluées avec bonne rentabilité (style Buffett)
    - **Growth** : Growth>20% + PE flexible — jeunes leaders en forte croissance (NVDA, TSMC)
    - **Quality** : ROE>20% + Marges>15% — moats et pricing power (ASML, LVMH)
    - **Dividend** : Yield>2.5% + PE<30 — revenu passif régulier
    - **Momentum** : Perf 6M>15% — capture les rotations sectorielles court terme
    """)

st.caption(f"Données mises à jour : {datetime.now().strftime('%Y-%m-%d %H:%M')}")
