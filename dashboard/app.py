from __future__ import annotations

from html import escape

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine, text

from pme_data_stack.config import Settings


st.set_page_config(page_title="Orbit — Pilotage PME", page_icon="✦", layout="wide")

st.markdown(
    """
    <style>
    :root {
        --void: #050611;
        --deep: #090b1d;
        --panel: rgba(15, 18, 42, 0.72);
        --line: rgba(153, 166, 255, 0.15);
        --text: #f4f2ff;
        --muted: #9298b8;
        --violet: #9c7cff;
        --cyan: #42e8e0;
        --pink: #ff71c8;
        --amber: #ffc46b;
    }

    html, body, [class*="css"] {
        font-family: Inter, "SF Pro Display", "Segoe UI", sans-serif;
    }

    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(circle at 88% 2%, rgba(105, 71, 255, 0.18), transparent 28rem),
            radial-gradient(circle at 4% 42%, rgba(0, 226, 214, 0.08), transparent 24rem),
            radial-gradient(circle at 54% 110%, rgba(255, 63, 173, 0.09), transparent 32rem),
            linear-gradient(145deg, #050610 0%, #080a19 52%, #050611 100%);
        color: var(--text);
    }

    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        opacity: 0.44;
        background-image:
            radial-gradient(circle, rgba(255,255,255,.72) 0 1px, transparent 1.3px),
            radial-gradient(circle, rgba(102,234,255,.45) 0 1px, transparent 1.2px);
        background-position: 0 0, 37px 51px;
        background-size: 83px 83px, 137px 137px;
        mask-image: linear-gradient(to bottom, black, transparent 78%);
    }

    [data-testid="stHeader"] {
        background: rgba(5, 6, 17, 0.58);
        backdrop-filter: blur(16px);
    }

    [data-testid="stMainBlockContainer"] {
        max-width: 1480px;
        padding: 2.4rem 3.4rem 5rem;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(9, 11, 29, 0.98), rgba(5, 7, 20, 0.98));
        border-right: 1px solid var(--line);
    }

    [data-testid="stSidebar"] > div:first-child { padding-top: 1.8rem; }
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p { color: #abb0cb; letter-spacing: .02em; }

    [data-baseweb="select"] > div,
    [data-baseweb="input"] > div,
    [data-testid="stDateInput"] > div > div {
        background: rgba(255, 255, 255, 0.035) !important;
        border-color: rgba(153, 166, 255, 0.18) !important;
        border-radius: 12px !important;
    }

    .sidebar-brand { display: flex; align-items: center; gap: .75rem; margin: .2rem 0 2.8rem; }
    .sidebar-mark {
        display: grid;
        place-items: center;
        width: 2.25rem;
        height: 2.25rem;
        border: 1px solid rgba(105, 232, 226, .45);
        border-radius: 50%;
        color: var(--cyan);
        box-shadow: inset 0 0 18px rgba(66, 232, 224, .15), 0 0 22px rgba(66, 232, 224, .1);
    }
    .sidebar-name { color: #f7f5ff; font-size: .88rem; font-weight: 750; letter-spacing: .18em; }
    .sidebar-sub { color: #6e7598; font-size: .58rem; letter-spacing: .18em; margin-top: .18rem; }
    .side-label { margin: 1.3rem 0 .5rem; color: #676e92; font-size: .58rem; font-weight: 700; letter-spacing: .2em; text-transform: uppercase; }
    .sidebar-status {
        margin-top: 2rem;
        padding: 1rem;
        border: 1px solid rgba(66, 232, 224, .12);
        border-radius: 14px;
        background: rgba(66, 232, 224, .035);
        color: #8d94b5;
        font-size: .72rem;
        line-height: 1.55;
    }
    .sidebar-status strong { color: #d9fff8; font-weight: 650; }
    .live-dot {
        display: inline-block;
        width: 7px;
        height: 7px;
        margin-right: .45rem;
        border-radius: 50%;
        background: var(--cyan);
        box-shadow: 0 0 0 4px rgba(66,232,224,.09), 0 0 13px var(--cyan);
        animation: pulse 2.6s ease-in-out infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: .55; transform: scale(.82); }
    }

    .cosmic-hero {
        position: relative;
        min-height: 335px;
        display: grid;
        grid-template-columns: 1.25fr .75fr;
        align-items: center;
        overflow: hidden;
        padding: 3.4rem 4rem;
        margin-bottom: 1.35rem;
        border: 1px solid rgba(153, 166, 255, .16);
        border-radius: 28px;
        background:
            linear-gradient(120deg, rgba(21, 23, 55, .89), rgba(8, 11, 31, .78)),
            radial-gradient(circle at 85% 50%, rgba(122, 81, 255, .19), transparent 32%);
        box-shadow: inset 0 1px 0 rgba(255,255,255,.05), 0 30px 80px rgba(0,0,0,.32);
    }
    .cosmic-hero::after {
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(105deg, transparent 38%, rgba(119, 235, 255, .04) 48%, transparent 58%);
        transform: translateX(-75%);
        animation: scan 9s ease-in-out infinite;
        pointer-events: none;
    }
    @keyframes scan {
        0%, 25% { transform: translateX(-75%); }
        65%, 100% { transform: translateX(78%); }
    }
    .eyebrow {
        display: inline-flex;
        align-items: center;
        gap: .55rem;
        padding: .46rem .72rem;
        border: 1px solid rgba(66, 232, 224, .16);
        border-radius: 99px;
        color: #b9fdf8;
        background: rgba(66, 232, 224, .055);
        font-size: .61rem;
        font-weight: 700;
        letter-spacing: .17em;
        text-transform: uppercase;
    }
    .hero-copy { position: relative; z-index: 2; }
    .hero-copy h1 {
        max-width: 800px;
        margin: 1.25rem 0 .9rem;
        color: #f7f5ff;
        font-size: clamp(2.65rem, 5vw, 5rem);
        font-weight: 650;
        letter-spacing: -.065em;
        line-height: .94;
    }
    .hero-copy h1 span {
        color: transparent;
        background: linear-gradient(92deg, #ac91ff, #62e6eb 58%, #ff86cf);
        -webkit-background-clip: text;
        background-clip: text;
    }
    .hero-copy p { max-width: 630px; margin: 0; color: #979dbd; font-size: .98rem; line-height: 1.65; }
    .hero-meta { display: flex; gap: 1.2rem; flex-wrap: wrap; margin-top: 1.55rem; color: #6f769b; font-size: .62rem; font-weight: 650; letter-spacing: .13em; text-transform: uppercase; }
    .hero-meta b { color: #d5d9ef; font-weight: 650; }

    .orbital-system { position: relative; justify-self: center; width: 250px; height: 250px; filter: drop-shadow(0 0 42px rgba(113, 86, 255, .28)); }
    .orbit, .orbit-two {
        position: absolute;
        inset: 10px;
        border: 1px solid rgba(132, 225, 255, .24);
        border-radius: 50%;
        transform: rotateX(66deg) rotateZ(-18deg);
    }
    .orbit-two { inset: 36px -5px; border-color: rgba(255, 113, 200, .16); transform: rotateX(72deg) rotateZ(47deg); }
    .planet {
        position: absolute;
        inset: 45px;
        overflow: hidden;
        border: 1px solid rgba(255,255,255,.2);
        border-radius: 50%;
        background:
            radial-gradient(circle at 34% 28%, rgba(255,255,255,.75), transparent 4%),
            radial-gradient(circle at 33% 28%, rgba(112,246,244,.7), transparent 17%),
            linear-gradient(140deg, #5c3cff 4%, #22265b 45%, #081523 66%, #e05ab4 125%);
        box-shadow: inset -28px -24px 55px rgba(0,0,0,.48), inset 18px 10px 35px rgba(98,230,235,.16), 0 0 60px rgba(126,94,255,.3);
    }
    .planet::after { content: ""; position: absolute; inset: 0; background: repeating-linear-gradient(165deg, transparent 0 10px, rgba(132,232,255,.07) 11px, transparent 13px); mix-blend-mode: screen; }
    .satellite { position: absolute; top: 35px; right: 42px; width: 8px; height: 8px; border-radius: 50%; background: #fff; box-shadow: 0 0 15px 4px rgba(83, 236, 232, .8); }

    .metric-card {
        position: relative;
        min-height: 158px;
        overflow: hidden;
        padding: 1.25rem 1.2rem 1.1rem;
        border: 1px solid rgba(153, 166, 255, .14);
        border-radius: 19px;
        background: linear-gradient(145deg, rgba(20, 23, 52, .84), rgba(10, 12, 31, .76));
        box-shadow: inset 0 1px 0 rgba(255,255,255,.035), 0 18px 40px rgba(0,0,0,.18);
        transition: transform .25s ease, border-color .25s ease;
    }
    .metric-card:hover { transform: translateY(-3px); border-color: rgba(156, 124, 255, .38); }
    .metric-card::after { content: ""; position: absolute; right: -35px; bottom: -55px; width: 110px; height: 110px; border-radius: 50%; background: var(--card-glow); filter: blur(28px); opacity: .22; }
    .metric-top { display: flex; justify-content: space-between; align-items: center; }
    .metric-label { color: #8d94b5; font-size: .64rem; font-weight: 700; letter-spacing: .13em; text-transform: uppercase; }
    .metric-glyph { color: var(--card-accent); font-size: 1rem; text-shadow: 0 0 16px var(--card-accent); }
    .metric-value { margin-top: 1rem; color: #f7f5ff; font-size: clamp(1.35rem, 2vw, 2rem); font-weight: 650; letter-spacing: -.045em; }
    .metric-note { margin-top: .38rem; color: #616989; font-size: .62rem; letter-spacing: .08em; text-transform: uppercase; }
    .accent-violet { --card-accent: #a184ff; --card-glow: #7f5cff; }
    .accent-cyan { --card-accent: #4de7df; --card-glow: #31dad1; }
    .accent-pink { --card-accent: #ff76c8; --card-glow: #ff4fae; }
    .accent-amber { --card-accent: #ffc46b; --card-glow: #ff9e47; }
    .accent-red { --card-accent: #ff768c; --card-glow: #ff496b; }

    .section-header { display: flex; align-items: end; justify-content: space-between; gap: 1rem; margin: 2.35rem 0 .85rem; }
    .section-kicker { color: #777e9f; font-size: .58rem; font-weight: 700; letter-spacing: .2em; text-transform: uppercase; }
    .section-title { margin-top: .22rem; color: #edeaff; font-size: 1.18rem; font-weight: 600; letter-spacing: -.02em; }
    .section-index { color: rgba(156,124,255,.52); font-size: .65rem; letter-spacing: .14em; }
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: rgba(153, 166, 255, .14) !important;
        border-radius: 20px !important;
        background: linear-gradient(145deg, rgba(17, 20, 46, .72), rgba(8, 10, 27, .65)) !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,.03), 0 18px 42px rgba(0,0,0,.16);
    }
    [data-testid="stDataFrame"] { border: 1px solid rgba(153, 166, 255, .1); border-radius: 14px; overflow: hidden; }
    .panel-heading { margin: .15rem 0 0; color: #eae7fa; font-size: .95rem; font-weight: 600; }
    .panel-caption { margin: .25rem 0 .35rem; color: #697090; font-size: .69rem; }
    .signal-strip { display: flex; align-items: center; justify-content: space-between; gap: 1rem; margin-top: 1rem; padding: .85rem 1.05rem; border: 1px solid rgba(255, 196, 107, .13); border-radius: 14px; background: linear-gradient(90deg, rgba(255,196,107,.055), rgba(255,113,200,.035)); color: #9ca2bf; font-size: .72rem; }
    .signal-strip b { color: #ffe2b5; font-weight: 650; }
    .signal-tag { color: #ffca7a; font-size: .57rem; font-weight: 750; letter-spacing: .16em; text-transform: uppercase; white-space: nowrap; }
    .quality-card { min-height: 110px; padding: 1rem; border: 1px solid rgba(66,232,224,.12); border-radius: 16px; background: rgba(66,232,224,.025); }
    .quality-state { color: #68eadf; font-size: .62rem; font-weight: 750; letter-spacing: .15em; text-transform: uppercase; }
    .quality-name { margin-top: .75rem; color: #d9ddf2; font-size: .78rem; line-height: 1.35; }
    .quality-value { margin-top: .35rem; color: #656d91; font-size: .62rem; }
    [data-testid="stExpander"] { border: 1px solid rgba(153,166,255,.14); border-radius: 16px; background: rgba(14,17,39,.54); }
    #MainMenu, footer { visibility: hidden; }

    @media (max-width: 900px) {
        [data-testid="stMainBlockContainer"] { padding: 1.5rem 1rem 3rem; }
        .cosmic-hero { grid-template-columns: 1fr; padding: 2.3rem 1.5rem; min-height: 390px; }
        .hero-copy h1 { font-size: 2.8rem; }
        .orbital-system { position: absolute; width: 175px; height: 175px; right: -35px; bottom: -45px; opacity: .55; }
        .planet { inset: 32px; }
        .hero-copy p { max-width: 80%; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def engine():
    return create_engine(Settings().sqlalchemy_url, pool_pre_ping=True)


@st.cache_data(ttl=60)
def load_data() -> dict[str, pd.DataFrame]:
    queries = {
        "kpis": "select * from marts.executive_kpis",
        "sales": "select * from marts.sales_daily order by order_date",
        "inventory": "select * from marts.inventory_status order by stock_status, product_name",
        "receivables": "select * from marts.accounts_receivable order by overdue_amount desc, due_date",
        "quality": """
            select distinct on (check_name)
                check_name, status, observed_value, threshold, checked_at
            from observability.quality_results
            order by check_name, checked_at desc
        """,
    }
    with engine().connect() as connection:
        return {name: pd.read_sql(text(query), connection) for name, query in queries.items()}


def euro(value: float) -> str:
    return f"{value:,.0f} €".replace(",", " ")


def metric_card(label: str, value: str, note: str, glyph: str, accent: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card {accent}">
            <div class="metric-top"><span class="metric-label">{escape(label)}</span><span class="metric-glyph">{glyph}</span></div>
            <div class="metric-value">{escape(value)}</div>
            <div class="metric-note">{escape(note)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(index: str, kicker: str, title: str) -> None:
    st.markdown(
        f"""
        <div class="section-header">
            <div><div class="section-kicker">{escape(kicker)}</div><div class="section-title">{escape(title)}</div></div>
            <div class="section-index">{escape(index)} / 03</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


try:
    data = load_data()
except Exception as exc:
    st.markdown(
        """
        <div class="cosmic-hero"><div class="hero-copy"><div class="eyebrow">Signal indisponible</div>
        <h1>Le noyau attend<br><span>ses premières données.</span></h1>
        <p>Lancez <code>make demo</code>, puis actualisez cette page.</p></div></div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("Diagnostic technique"):
        st.code(str(exc))
    st.stop()


st.sidebar.markdown(
    """
    <div class="sidebar-brand"><div class="sidebar-mark">✦</div><div><div class="sidebar-name">ORBIT</div><div class="sidebar-sub">PME DATA CORE</div></div></div>
    <div class="side-label">Périmètre du signal</div>
    """,
    unsafe_allow_html=True,
)

sales = data["sales"].copy()
regions = sorted(sales["region"].dropna().unique().tolist())
selected_regions = st.sidebar.multiselect("Régions actives", regions, default=regions)
if selected_regions:
    sales = sales[sales["region"].isin(selected_regions)]
active_region_count = len(selected_regions) if selected_regions else len(regions)

min_date = pd.to_datetime(sales["order_date"]).min().date()
max_date = pd.to_datetime(sales["order_date"]).max().date()
date_range = st.sidebar.date_input(
    "Fenêtre temporelle", value=(min_date, max_date), min_value=min_date, max_value=max_date
)
if len(date_range) == 2:
    order_dates = pd.to_datetime(sales["order_date"]).dt.date
    sales = sales[(order_dates >= date_range[0]) & (order_dates <= date_range[1])]
    display_start, display_end = date_range
else:
    display_start, display_end = min_date, max_date

kpis = data["kpis"].iloc[0]
refreshed_at = pd.to_datetime(kpis["refreshed_at"])
if refreshed_at.tzinfo is not None:
    refreshed_at = refreshed_at.tz_convert("Europe/Paris")
refresh_label = refreshed_at.strftime("%d.%m.%Y · %H:%M")

st.sidebar.markdown(
    f"""
    <div class="sidebar-status"><span class="live-dot"></span><strong>Noyau synchronisé</strong><br>
    Dernière matérialisation<br>{escape(refresh_label)}</div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="cosmic-hero">
        <div class="hero-copy">
            <div class="eyebrow"><span class="live-dot"></span>Signal opérationnel · {active_region_count} régions</div>
            <h1>Votre entreprise,<br><span>vue depuis l’orbite.</span></h1>
            <p>Un poste de commandement vivant pour suivre la valeur, détecter les tensions et décider avant que les signaux faibles ne deviennent des urgences.</p>
            <div class="hero-meta">
                <span>Fenêtre <b>{display_start.strftime('%d.%m')} → {display_end.strftime('%d.%m.%Y')}</b></span>
                <span>Modèles <b>10 actifs</b></span><span>Qualité <b>surveillée</b></span>
            </div>
        </div>
        <div class="orbital-system" aria-hidden="true"><div class="orbit"></div><div class="orbit-two"></div><div class="planet"></div><div class="satellite"></div></div>
    </div>
    """,
    unsafe_allow_html=True,
)

revenue = float(sales["revenue"].sum())
margin = float(sales["gross_margin"].sum())
margin_rate = margin / revenue * 100 if revenue else 0
overdue = float(kpis["overdue_receivables"])
stockouts = int(kpis["stockouts"])

metric_columns = st.columns(5, gap="small")
with metric_columns[0]:
    metric_card("Chiffre d'affaires", euro(revenue), "flux commercial cumulé", "↗", "accent-violet")
with metric_columns[1]:
    metric_card("Marge brute", euro(margin), "valeur capturée", "◒", "accent-cyan")
with metric_columns[2]:
    metric_card("Taux de marge", f"{margin_rate:.1f} %", "efficacité économique", "◎", "accent-pink")
with metric_columns[3]:
    metric_card("Impayés échus", euro(overdue), "capital à recouvrer", "⌁", "accent-amber")
with metric_columns[4]:
    metric_card("Ruptures", str(stockouts), "alertes logistiques", "△", "accent-red")

late_count = int(kpis["overdue_invoices"])
low_stock = int(kpis["low_stock_products"])
st.markdown(
    f"""
    <div class="signal-strip"><span><b>{late_count} factures</b> requièrent une relance et <b>{low_stock} références</b> approchent leur seuil de réapprovisionnement.</span>
    <span class="signal-tag">Signal prioritaire ↗</span></div>
    """,
    unsafe_allow_html=True,
)

section_header("01", "Trajectoire commerciale", "Ventes & création de valeur")
left, right = st.columns((1.65, 1), gap="medium")
chart_config = {"displaylogo": False, "responsive": True}

with left:
    with st.container(border=True):
        st.markdown(
            '<div class="panel-heading">Trajectoire de performance</div><div class="panel-caption">Évolution quotidienne du revenu et de la marge brute</div>',
            unsafe_allow_html=True,
        )
        trend = sales.groupby("order_date", as_index=False)[["revenue", "gross_margin"]].sum()
        trend = trend.rename(columns={"revenue": "Chiffre d'affaires", "gross_margin": "Marge brute"})
        melted = trend.melt(id_vars="order_date", var_name="Indicateur", value_name="Montant")
        figure = px.line(
            melted,
            x="order_date",
            y="Montant",
            color="Indicateur",
            markers=True,
            color_discrete_map={"Chiffre d'affaires": "#9C7CFF", "Marge brute": "#42E8E0"},
        )
        figure.update_traces(line={"width": 2.7}, marker={"size": 4})
        figure.update_layout(
            height=355,
            margin={"l": 8, "r": 8, "t": 25, "b": 8},
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={"color": "#858CAB", "size": 11},
            legend={"title": "", "orientation": "h", "y": 1.12, "x": 0},
            hovermode="x unified",
            xaxis={"title": "", "gridcolor": "rgba(140,150,200,.07)", "showline": False},
            yaxis={"title": "", "gridcolor": "rgba(140,150,200,.08)", "ticksuffix": " €", "zeroline": False},
        )
        st.plotly_chart(figure, width="stretch", config=chart_config)

with right:
    with st.container(border=True):
        st.markdown(
            '<div class="panel-heading">Constellation des canaux</div><div class="panel-caption">Répartition du chiffre d’affaires consolidé</div>',
            unsafe_allow_html=True,
        )
        by_channel = sales.groupby("channel", as_index=False)["revenue"].sum()
        figure = px.pie(
            by_channel,
            names="channel",
            values="revenue",
            hole=0.68,
            color_discrete_sequence=["#9C7CFF", "#42E8E0", "#FF71C8"],
        )
        figure.update_traces(
            textinfo="percent",
            textfont={"color": "#F4F2FF", "size": 12},
            marker={"line": {"color": "#0B0D20", "width": 4}},
            hovertemplate="<b>%{label}</b><br>%{value:,.0f} €<extra></extra>",
        )
        figure.update_layout(
            height=355,
            margin={"l": 5, "r": 5, "t": 25, "b": 5},
            paper_bgcolor="rgba(0,0,0,0)",
            font={"color": "#8D94B5"},
            legend={"title": "", "orientation": "h", "y": -0.04, "x": 0.08},
            annotations=[
                {
                    "text": f"<b>{euro(revenue)}</b><br><span style='font-size:10px;color:#747B9B'>SIGNAL TOTAL</span>",
                    "x": 0.5,
                    "y": 0.5,
                    "showarrow": False,
                    "font": {"color": "#F4F2FF", "size": 16},
                }
            ],
        )
        st.plotly_chart(figure, width="stretch", config=chart_config)

section_header("02", "Tensions à traiter", "Stocks & recouvrement")
inventory_column, receivables_column = st.columns(2, gap="medium")

with inventory_column:
    with st.container(border=True):
        st.markdown(
            '<div class="panel-heading">Radar des stocks</div><div class="panel-caption">Références sous seuil et quantités recommandées</div>',
            unsafe_allow_html=True,
        )
        inventory = data["inventory"]
        inventory = inventory[inventory["stock_status"] != "sain"].copy()
        inventory["stock_status"] = inventory["stock_status"].map({"rupture": "RUPTURE", "a_reapprovisionner": "À COMMANDER"})
        inventory_table = inventory[
            ["product_name", "stock_quantity", "reorder_point", "stock_status", "suggested_reorder_quantity"]
        ].rename(
            columns={"product_name": "Produit", "stock_quantity": "Stock", "reorder_point": "Seuil", "stock_status": "Signal", "suggested_reorder_quantity": "À commander"}
        )
        st.dataframe(
            inventory_table,
            hide_index=True,
            width="stretch",
            height=310,
            column_config={
                "Stock": st.column_config.ProgressColumn("Stock", min_value=0, max_value=100, format="%d"),
                "Seuil": st.column_config.NumberColumn("Seuil", format="%d"),
                "À commander": st.column_config.NumberColumn("À commander", format="%d"),
            },
        )

with receivables_column:
    with st.container(border=True):
        st.markdown(
            '<div class="panel-heading">File de recouvrement</div><div class="panel-caption">Factures échues classées par montant à recouvrer</div>',
            unsafe_allow_html=True,
        )
        late = data["receivables"]
        late = late[late["overdue_amount"] > 0].copy()
        late_table = late[["invoice_id", "company_name", "due_date", "days_late", "overdue_amount"]].rename(
            columns={"invoice_id": "Facture", "company_name": "Client", "due_date": "Échéance", "days_late": "Retard", "overdue_amount": "Montant dû"}
        )
        st.dataframe(
            late_table,
            hide_index=True,
            width="stretch",
            height=310,
            column_config={
                "Échéance": st.column_config.DateColumn("Échéance", format="DD.MM.YYYY"),
                "Retard": st.column_config.NumberColumn("Retard", format="%d j"),
                "Montant dû": st.column_config.NumberColumn("Montant dû", format="%.0f €"),
            },
        )

section_header("03", "Intégrité du noyau", "Observabilité & confiance")
quality = data["quality"].copy()
quality_columns = st.columns(len(quality), gap="small")
for column, (_, check) in zip(quality_columns, quality.iterrows()):
    readable_name = str(check["check_name"]).replace("_", " ")
    state = "Signal stable" if check["status"] == "pass" else "Anomalie"
    observed = str(check["observed_value"])
    with column:
        st.markdown(
            f"""
            <div class="quality-card"><div class="quality-state"><span class="live-dot"></span>{escape(state)}</div>
            <div class="quality-name">{escape(readable_name)}</div>
            <div class="quality-value">Observé {escape(observed[:12])} · Attendu {escape(str(check['threshold']))}</div></div>
            """,
            unsafe_allow_html=True,
        )

st.markdown(
    f"""
    <div style="margin-top:2.3rem;padding-top:1rem;border-top:1px solid rgba(153,166,255,.1);display:flex;justify-content:space-between;color:#545b7c;font-size:.6rem;letter-spacing:.13em;text-transform:uppercase">
        <span>Orbit PME Data Core · Decision intelligence</span><span>{escape(refresh_label)} · Europe/Paris</span>
    </div>
    """,
    unsafe_allow_html=True,
)

