"""
Stock Picking World - Dashboard single-page avec 4 onglets.
Version 100% fiable (pas de multi-pages, pas de dossier pages/ requis).
"""
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Stock Picking World", page_icon="📊", layout="wide")

st.title("📊 Stock Picking World")
st.caption("Dashboard multi-pays / secteurs / stocks avec KPIs et backtests")

tab1, tab2, tab3, tab4 = st.tabs([
    "🌍 Pays",
    "🏭 Secteurs",
    "🎯 Stock Picks",
    "📈 Backtest"
])

# ==========================================================
# TAB 1 : PAYS
# ==========================================================
with tab1:
    st.header("🌍 Analyse des pays")
    st.caption("10 pays clés notés sur un score composite momentum + valuation + macro")

    COUNTRIES = [
        ("USA","S&P 500","^GSPC","🇺🇸"),("Chine","CSI 300","000300.SS","🇨🇳"),
        ("Hong Kong","Hang Seng","^HSI","🇭🇰"),("Coree Sud","KOSPI","^KS11","🇰🇷"),
        ("Japon","Nikkei 225","^N225","🇯🇵"),("Taiwan","TSEC","^TWII","🇹🇼"),
        ("Singapour","STI","^STI","🇸🇬"),("Inde","NIFTY 50","^NSEI","🇮🇳"),
        ("Allemagne","DAX","^GDAXI","🇩🇪"),("France","CAC 40","^FCHI","🇫🇷"),
    ]
    PE_MED10 = {"USA":22,"Chine":12,"Hong Kong":11,"Coree Sud":13,"Japon":16,"Taiwan":15,"Singapour":13,"Inde":22,"Allemagne":14,"France":15}
    PE_CUR = {"USA":26,"Chine":12,"Hong Kong":10,"Coree Sud":12,"Japon":17,"Taiwan":20,"Singapour":12,"Inde":24,"Allemagne":15,"France":14}
    PIB_FC = {"USA":2.3,"Chine":4.8,"Hong Kong":3.1,"Coree Sud":2.2,"Japon":1.1,"Taiwan":2.8,"Singapour":2.6,"Inde":6.7,"Allemagne":0.9,"France":1.3}
    DEBT = {"USA":123,"Chine":84,"Hong Kong":38,"Coree Sud":52,"Japon":263,"Taiwan":33,"Singapour":168,"Inde":83,"Allemagne":65,"France":112}
    BOND = {"USA":4.4,"Chine":2.1,"Hong Kong":3.9,"Coree Sud":3.5,"Japon":1.6,"Taiwan":1.7,"Singapour":2.8,"Inde":6.9,"Allemagne":2.5,"France":3.1}

    @st.cache_data(ttl=3600)
    def fetch_perf(sym):
        try:
            h = yf.Ticker(sym).history(period="1y", interval="1d")
            if h.empty: return None,None,None
            c = h["Close"]
            p_now = c.iloc[-1]
            p_1m = c.iloc[-22] if len(c)>=22 else c.iloc[0]
            p_6m = c.iloc[-130] if len(c)>=130 else c.iloc[0]
            return (p_now-p_1m)/p_1m*100, (p_now-p_6m)/p_6m*100, (p_now-c.iloc[0])/c.iloc[0]*100
        except: return None,None,None

    tri_mode = st.radio("Tri", ["Long terme (score)", "Tactique (momentum 6M)"], horizontal=True, key="t1_tri")

    with st.spinner("Récupération données Yahoo..."):
        rows = []
        for name, idx, sym, flag in COUNTRIES:
            p1m, p6m, pyr = fetch_perf(sym)
            rows.append({"Pays": f"{flag} {name}", "Indice": idx,
                        "Perf 1M %": p1m, "Perf 6M %": p6m, "Perf 1Y %": pyr,
                        "PE actuel": PE_CUR[name], "PE med 10y": PE_MED10[name],
                        "PIB fc %": PIB_FC[name], "Dette/PIB %": DEBT[name], "Bond 10Y %": BOND[name]})

    df1 = pd.DataFrame(rows)
    p6m_v = df1["Perf 6M %"].dropna()
    if not p6m_v.empty:
        pmin, pmax = p6m_v.min(), p6m_v.max()
        def score1(r):
            p6m = r["Perf 6M %"]
            mom = ((p6m-pmin)/(pmax-pmin)*100) if pd.notna(p6m) and pmax>pmin else 50
            try: cheap = max(0,min(100,(2-r["PE actuel"]/r["PE med 10y"])*50))
            except: cheap = 50
            pib = max(0,min(100,(r["PIB fc %"] or 0)*100/7))
            debt = max(0,min(100,100-(r["Dette/PIB %"] or 100)/3))
            bond = max(0,min(100,100-abs((r["Bond 10Y %"] or 4)-3)*15))
            val = 0.25*mom+0.35*cheap+0.20*pib+0.10*debt+0.10*bond
            return int(round(val)) if pd.notna(val) else 0
        df1["Score /100"] = df1.apply(score1, axis=1)
    df1 = df1.sort_values("Score /100" if tri_mode.startswith("Long") else "Perf 6M %", ascending=False, na_position="last").reset_index(drop=True)

    st.dataframe(df1, use_container_width=True, hide_index=True, column_config={
        "Score /100": st.column_config.ProgressColumn("Score /100", min_value=0, max_value=100, format="%d"),
        "Perf 1M %": st.column_config.NumberColumn(format="%+.1f%%"),
        "Perf 6M %": st.column_config.NumberColumn(format="%+.1f%%"),
        "Perf 1Y %": st.column_config.NumberColumn(format="%+.1f%%"),
        "PIB fc %": st.column_config.NumberColumn(format="%+.1f%%"),
    })
    c1,c2 = st.columns(2)
    c1.success(f"🥇 Top 3 : {', '.join(df1.head(3)['Pays'])}")
    c2.error(f"🔻 Flop 3 : {', '.join(df1.tail(3)['Pays'])}")

# ==========================================================
# TAB 2 : SECTEURS
# ==========================================================
with tab2:
    st.header("🏭 Analyse des secteurs")
    st.caption("10 secteurs porteurs via ETF proxies + émergents")

    SECTORS = [
        ("AI","BOTZ",100),("Semiconducteurs","SOXX",95),("Quantum","QTUM",85),
        ("Robotics","ROBO",80),("Batteries/EV","LIT",75),("Cloud","WCLD",75),
        ("Cybersecurite","CIBR",85),("Green Energy","ICLN",60),("Biotech","XBI",70),
        ("Crypto Equity","COIN",80),
    ]

    @st.cache_data(ttl=3600)
    def fetch_sec(sym):
        try:
            h = yf.Ticker(sym).history(period="1y", interval="1d")
            if h.empty: return None
            c = h["Close"]
            p_now = c.iloc[-1]
            p_1m = c.iloc[-22] if len(c)>=22 else c.iloc[0]
            p_6m = c.iloc[-130] if len(c)>=130 else c.iloc[0]
            p_ytd = c.iloc[-min(200,len(c)-1)]
            delta = c.diff().dropna().tail(14)
            g = delta.where(delta>0,0).mean(); l = -delta.where(delta<0,0).mean()
            rsi = round(100-100/(1+g/l)) if l>0 else 50
            return {"perf_1m":(p_now-p_1m)/p_1m*100,"perf_6m":(p_now-p_6m)/p_6m*100,
                    "perf_ytd":(p_now-p_ytd)/p_ytd*100,"rsi":rsi,"price":float(p_now)}
        except: return None

    with st.spinner("Récupération ETFs sectoriels..."):
        rows = []
        for name, sym, fp in SECTORS:
            d = fetch_sec(sym)
            if not d:
                rows.append({"Secteur":name,"ETF":sym,"Perf 6M %":None,"Perf YTD %":None,"RSI":50,"Future pot.":fp,"Score /100":0})
                continue
            p6n = max(0,min(100,d["perf_6m"]*2+50))
            pyn = max(0,min(100,d["perf_ytd"]*1.5+50))
            rsi_s = 100-abs(d["rsi"]-50)*2
            try: score = int(round(0.30*p6n+0.30*fp+0.20*rsi_s+0.20*pyn))
            except: score = 0
            rows.append({"Secteur":name,"ETF":sym,"Prix $":d["price"],
                        "Perf 1M %":d["perf_1m"],"Perf 6M %":d["perf_6m"],"Perf YTD %":d["perf_ytd"],
                        "RSI":d["rsi"],"Future pot.":fp,"Score /100":score})

    df2 = pd.DataFrame(rows).sort_values("Score /100", ascending=False).reset_index(drop=True)
    st.dataframe(df2, use_container_width=True, hide_index=True, column_config={
        "Score /100": st.column_config.ProgressColumn("Score /100", min_value=0, max_value=100, format="%d"),
        "Future pot.": st.column_config.ProgressColumn("Future pot.", min_value=0, max_value=100, format="%d"),
        "Perf 1M %": st.column_config.NumberColumn(format="%+.1f%%"),
        "Perf 6M %": st.column_config.NumberColumn(format="%+.1f%%"),
        "Perf YTD %": st.column_config.NumberColumn(format="%+.1f%%"),
        "Prix $": st.column_config.NumberColumn(format="$%.2f"),
    })
    st.success(f"🏆 Top 3 secteurs : {', '.join(df2.head(3)['Secteur'])}")

# ==========================================================
# TAB 3 : STOCK PICKS
# ==========================================================
with tab3:
    st.header("🎯 Stock Picks")
    st.caption("Screener multi-criteres + 6 presets. Fondamentaux Q3 2026 (base statique) + prix live via yfinance.")

    # Base statique : ticker, pays, secteur, nom, pe, pb, ev_ebitda, peg, roe, margin, growth, div, d2e, cap ($)
    STOCKS_FULL = [
        ("NVDA","USA","Semiconducteurs","NVIDIA",48,45,55,1.2,0.98,0.55,1.22,0.001,0.24,3.9e12),
        ("MSFT","USA","AI/Cloud","Microsoft",34,12,22,2.3,0.35,0.36,0.15,0.008,0.35,3.3e12),
        ("GOOGL","USA","AI/Cloud","Alphabet",24,7,17,1.5,0.30,0.28,0.14,0.005,0.10,2.1e12),
        ("META","USA","AI/Cloud","Meta Platforms",28,9,18,1.5,0.33,0.35,0.19,0.004,0.28,1.45e12),
        ("AAPL","USA","Consumer Tech","Apple",32,45,24,2.6,1.60,0.24,0.06,0.005,1.50,3.3e12),
        ("AMZN","USA","E-commerce","Amazon",42,7,20,1.5,0.21,0.10,0.11,0,0.35,2.2e12),
        ("AVGO","USA","Semiconducteurs","Broadcom",38,15,25,1.4,0.24,0.30,0.44,0.014,1.60,900e9),
        ("AMD","USA","Semiconducteurs","AMD",65,4,55,1.8,0.05,0.06,0.10,0,0.05,250e9),
        ("PLTR","USA","AI/Data","Palantir",195,55,180,4.5,0.10,0.14,0.30,0,0.02,230e9),
        ("CRM","USA","Cloud","Salesforce",42,4,22,2.1,0.10,0.16,0.09,0.005,0.20,320e9),
        ("SNOW","USA","Cloud","Snowflake",250,15,180,None,-0.05,-0.05,0.30,0,0.05,75e9),
        ("PANW","USA","Cybersecurite","Palo Alto Networks",58,15,45,3.0,0.35,0.13,0.16,0,0.30,150e9),
        ("CRWD","USA","Cybersecurite","CrowdStrike",95,25,65,None,0.10,0.10,0.31,0,0.30,95e9),
        ("TSLA","USA","EV/Batteries","Tesla",85,10,60,4.5,0.10,0.08,0.03,0,0.11,1.2e12),
        ("MRNA","USA","Biotech","Moderna",0,0.9,0,None,-0.35,-1.0,-0.45,0,0.05,18e9),
        ("REGN","USA","Biotech","Regeneron",19,3,15,1.8,0.14,0.28,0.09,0.005,0.05,85e9),
        ("COIN","USA","Crypto","Coinbase",42,8,25,1.1,0.32,0.24,0.55,0,0.35,75e9),
        ("MSTR","USA","Crypto","MicroStrategy",0,3,0,None,-0.20,-2.5,0,0,0.50,80e9),
        ("BRK-B","USA","Holding","Berkshire Hathaway",13,1.6,12,None,0.13,0.28,0.05,0,0.20,1e12),
        ("JPM","USA","Finance","JPMorgan Chase",13,2,None,None,0.16,0.35,0.08,0.021,None,650e9),
        ("V","USA","Payments","Visa",32,15,25,2.0,0.50,0.55,0.10,0.007,0.55,570e9),
        ("TSM","Taiwan","Semiconducteurs","TSMC",24,7,15,0.9,0.28,0.41,0.36,0.014,0.28,950e9),
        ("005930.KS","Coree Sud","Semiconducteurs","Samsung Electronics",13,1.3,7,None,0.11,0.14,0.11,0.025,0.31,420e9),
        ("000660.KS","Coree Sud","Semiconducteurs","SK Hynix",9,3,5,None,0.35,0.28,0.65,0.006,0.24,140e9),
        ("6954.T","Japon","Robotics","Fanuc",28,2.5,15,None,0.09,0.20,0.05,0.020,0.03,45e9),
        ("6506.T","Japon","Robotics","Yaskawa Electric",22,2,12,None,0.15,0.11,0.10,0.014,0.20,18e9),
        ("7203.T","Japon","Auto","Toyota",9,1,None,None,0.10,0.10,0.03,0.028,None,250e9),
        ("BABA","Chine","AI/Cloud","Alibaba",15,1.5,10,0.8,0.11,0.14,0.05,0.010,0.20,230e9),
        ("TCEHY","Chine","AI/Cloud","Tencent",19,4,15,1.5,0.15,0.29,0.08,0.008,0.28,500e9),
        ("BYDDY","Chine","EV/Batteries","BYD",22,3,10,0.9,0.19,0.05,0.24,0.013,0.32,110e9),
        ("ASML","Europe","Semiconducteurs","ASML",38,22,28,2.5,0.55,0.28,0.11,0.008,0.25,330e9),
        ("SAP","Allemagne","Cloud","SAP",42,5,25,3.0,0.15,0.15,0.10,0.011,0.35,280e9),
        ("SIE.DE","Allemagne","Robotics","Siemens",18,3,12,1.8,0.15,0.11,0.05,0.028,0.50,175e9),
        ("MC.PA","France","Luxe","LVMH",22,5,14,None,0.19,0.24,0.02,0.020,0.45,330e9),
        ("OR.PA","France","Cosmetics","L'Oreal",30,7,20,None,0.19,0.19,0.05,0.017,0.25,220e9),
        ("AIR.PA","France","Aerospace","Airbus",25,5,15,1.5,0.22,0.10,0.15,0.014,0.35,140e9),
    ]

    @st.cache_data(ttl=3600)
    def fetch_live_price(t):
        try:
            h = yf.Ticker(t).history(period="6mo")
            if h.empty: return None, None, None
            c = h["Close"]
            p_now = float(c.iloc[-1])
            p1m_ref = c.iloc[-22] if len(c)>=22 else c.iloc[0]
            perf_1m = (p_now - p1m_ref) / p1m_ref * 100 if p1m_ref > 0 else None
            perf_6m = (p_now - c.iloc[0]) / c.iloc[0] * 100 if c.iloc[0] > 0 else None
            return p_now, perf_1m, perf_6m
        except: return None, None, None

    c1,c2 = st.columns(2)
    countries = sorted(set(s[1] for s in STOCKS_FULL))
    sectors = sorted(set(s[2] for s in STOCKS_FULL))
    with c1:
        sel_c = st.multiselect("Pays", countries, default=countries)
        sel_s = st.multiselect("Secteurs", sectors, default=sectors)
    with c2:
        preset = st.radio("Preset", ["Aucun","Value","Growth","Quality","Dividend","Momentum","Deep Value"], horizontal=True)

    defaults = {
        "Aucun":       {"pe":300, "roe":-50, "growth":-100, "div":0.0, "perf":-100},
        "Value":       {"pe":20,  "roe":15,  "growth":0,    "div":0.0, "perf":-30},
        "Growth":      {"pe":100, "roe":5,   "growth":20,   "div":0.0, "perf":0},
        "Quality":     {"pe":40,  "roe":20,  "growth":5,    "div":0.0, "perf":-20},
        "Dividend":    {"pe":30,  "roe":5,   "growth":0,    "div":2.5, "perf":-20},
        "Momentum":    {"pe":200, "roe":-10, "growth":0,    "div":0.0, "perf":15},
        "Deep Value":  {"pe":15,  "roe":10,  "growth":0,    "div":0.0, "perf":-40},
    }
    d = defaults[preset]
    c3,c4,c5,c6,c7 = st.columns(5)
    pe_max     = c3.number_input("PE max",         0,   300, d["pe"],     key=f"pe_{preset}")
    roe_min    = c4.number_input("ROE min %",      -50, 100, d["roe"],    key=f"roe_{preset}")
    growth_min = c5.number_input("Growth min %",   -100,200, d["growth"], key=f"gr_{preset}")
    div_min    = c6.number_input("Div min %",      0.0, 10.0,float(d["div"]), key=f"div_{preset}")
    perf_min   = c7.number_input("Perf 6M min %",  -100,500, d["perf"],   key=f"perf_{preset}")

    with st.spinner("Recuperation prix live yfinance..."):
        rows = []
        n_live = 0
        for t, pays, sect, name, pe, pb, ev, peg, roe, margin, growth, div, d2e, cap in STOCKS_FULL:
            if pays not in sel_c or sect not in sel_s: continue
            # Filtres sur fondamentaux (statiques)
            if pe > 0 and pe > pe_max: continue
            if roe*100 < roe_min: continue
            if growth*100 < growth_min: continue
            if div*100 < div_min: continue
            # Prix live (peut echouer)
            price, p1m, p6m = fetch_live_price(t)
            if p6m is not None: n_live += 1
            if perf_min > -100 and p6m is not None and p6m < perf_min: continue
            # Score composite
            cheap_s = max(0,min(100,(30-max(pe,0.1))*3.3)) if pe > 0 else 30
            qual_s  = max(0,min(100,roe*100*2 + margin*100))
            grow_s  = max(0,min(100,growth*100*4))
            mom_s   = max(0,min(100,(p6m or 0)*2+50))
            try: score = int(round(0.25*cheap_s+0.25*qual_s+0.25*grow_s+0.25*mom_s))
            except: score = 0
            rows.append({"Ticker":t,"Nom":name,"Pays":pays,"Secteur":sect,
                        "Prix $":price,"PE":pe if pe>0 else None,"P/B":pb,
                        "EV/EBITDA":ev,"PEG":peg,
                        "ROE %":roe*100 if roe else None,"Marge %":margin*100 if margin else None,
                        "Growth %":growth*100,"Div %":div*100,
                        "Perf 6M %":p6m,"Cap $B":cap/1e9 if cap else None,"Score /100":score})

    df3 = pd.DataFrame(rows)
    if df3.empty:
        st.warning("Aucun stock ne matche les filtres. Assouplis-les ou change de preset.")
    else:
        df3 = df3.sort_values("Score /100", ascending=False).reset_index(drop=True)
        status = f"✅ {n_live}/{len(rows)} stocks avec prix live" if n_live > 0 else "⚠️ yfinance temporairement indisponible (prix N/A affiches)"
        st.info(f"{len(df3)} stocks matchent (preset: {preset}) — {status}")
        st.dataframe(df3, use_container_width=True, hide_index=True, column_config={
            "Score /100": st.column_config.ProgressColumn("Score /100", min_value=0, max_value=100, format="%d"),
            "Prix $": st.column_config.NumberColumn(format="$%.2f"),
            "PE": st.column_config.NumberColumn(format="%.1f"),
            "P/B": st.column_config.NumberColumn(format="%.1f"),
            "EV/EBITDA": st.column_config.NumberColumn(format="%.1f"),
            "PEG": st.column_config.NumberColumn(format="%.2f"),
            "ROE %": st.column_config.NumberColumn(format="%.1f%%"),
            "Marge %": st.column_config.NumberColumn(format="%.1f%%"),
            "Growth %": st.column_config.NumberColumn(format="%+.1f%%"),
            "Div %": st.column_config.NumberColumn(format="%.2f%%"),
            "Perf 6M %": st.column_config.NumberColumn(format="%+.1f%%"),
            "Cap $B": st.column_config.NumberColumn(format="%.0f B"),
        })
        st.success(f"🥇 Top 3 (score composite) : {' | '.join(df3.head(3)['Ticker'].tolist())}")

# ==========================================================
# TAB 4 : BACKTEST
# ==========================================================
with tab4:
    st.header("📈 Backtest 5 stratégies vs Buy & Hold Monde")
    STRATS = [("Buy & Hold Monde","VT","#1a3a52"),("Value","SPYV","#4A90E2"),
              ("Growth","SPYG","#4a9c3a"),("Quality","QUAL","#e8a86a"),
              ("Dividend Aristo","NOBL","#c93838"),("Momentum","MTUM","#8e44ad")]

    @st.cache_data(ttl=3600)
    def fetch_h(sym, years):
        try:
            h = yf.Ticker(sym).history(period=f"{years}y", interval="1mo")
            return h["Close"] if not h.empty else None
        except: return None

    c1,c2,c3 = st.columns(3)
    years = c1.slider("Horizon (années)", 3, 10, 10, key="t4_yrs")
    initial = c2.number_input("Initial ($)", 1000, 100000, 10000, 1000, key="t4_init")
    mode = c3.radio("Mode", ["Lump sum","DCA $100/mois"], key="t4_mode")

    with st.spinner(f"Backtest {years} ans..."):
        data = {n:{"p":fetch_h(s,years),"c":c,"s":s} for n,s,c in STRATS}
        results, curves = [], {}
        for n,dd in data.items():
            p = dd["p"]
            if p is None or len(p)<12: continue
            if mode == "Lump sum":
                shares = initial/p.iloc[0]; curve = shares*p; final = curve.iloc[-1]; inv = initial
            else:
                total_inv, shares, vals = 0, 0, []
                for price in p:
                    shares += 100/price; total_inv += 100; vals.append(shares*price)
                curve = pd.Series(vals, index=p.index); final = vals[-1]; inv = total_inv
            r = (final-inv)/inv*100
            mr = p.pct_change().dropna()
            cagr = (final/inv)**(1/(len(p)/12))-1 if inv>0 else 0
            dd_max = ((curve-curve.cummax())/curve.cummax()).min()*100
            sharpe = (mr.mean()*12)/(mr.std()*np.sqrt(12)) if mr.std()>0 else 0
            results.append({"Stratégie":n,"ETF":dd["s"],"Final $":final,"CAGR %":cagr*100,
                          "Max DD %":dd_max,"Sharpe":sharpe})
            curves[n] = curve

    df4 = pd.DataFrame(results).sort_values("CAGR %", ascending=False).reset_index(drop=True)
    st.dataframe(df4, use_container_width=True, hide_index=True, column_config={
        "Final $": st.column_config.NumberColumn(format="$%.0f"),
        "CAGR %": st.column_config.NumberColumn(format="%+.2f%%"),
        "Max DD %": st.column_config.NumberColumn(format="%.1f%%"),
        "Sharpe": st.column_config.NumberColumn(format="%.2f"),
    })

    fig = go.Figure()
    for n, curve in curves.items():
        col = next((c for nn,s,c in STRATS if nn==n), "#333")
        fig.add_trace(go.Scatter(x=curve.index, y=curve.values, mode='lines', name=n, line=dict(color=col, width=2)))
    fig.update_layout(xaxis_title="Date", yaxis_title="Valeur $", template="plotly_white", height=450,
                     legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.caption(f"Généré {datetime.now().strftime('%Y-%m-%d %H:%M')} | Sources: Yahoo Finance | Dashboard v2 single-page")
