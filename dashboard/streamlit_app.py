import sqlite3
import os
from pathlib import Path

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st

# ────────── Page Config ──────────
st.set_page_config(
    page_title="Bluestock Mutual Fund Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ────────── Constants / Paths ──────────
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "db" / "bluestock_mf.db"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

BLUESTOCK_BLUE = "#1F4E79"
BLUESTOCK_MEDIUM = "#2E75B6"
BLUESTOCK_ORANGE = "#FF6B35"
BLUESTOCK_BG = "#F5F7FA"
BLUESTOCK_LIGHT_BLUE = "#D6E4F0"
BLUESTOCK_GREEN = "#2E8B57"

COLORSCALE_BLUES = [[0, BLUESTOCK_LIGHT_BLUE], [1, BLUESTOCK_BLUE]]
PLOTLY_TEMPLATE = "plotly_white"


# ────────── CSS Styling ──────────
def apply_custom_css():
    st.markdown(
        f"""
        <style>
        /* Root variables */
        :root {{
            --primary: {BLUESTOCK_BLUE};
            --secondary: {BLUESTOCK_MEDIUM};
            --accent: {BLUESTOCK_ORANGE};
            --background: {BLUESTOCK_BG};
        }}

        /* Global */
        .stApp {{
            background-color: {BLUESTOCK_BG};
        }}

        /* Sidebar */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {BLUESTOCK_BLUE} 0%, #163A5C 100%);
            padding-top: 1rem;
        }}
        [data-testid="stSidebar"] * {{
            color: #FFFFFF !important;
        }}
        [data-testid="stSidebar"] .stRadio label,
        [data-testid="stSidebar"] .stSelectbox label,
        [data-testid="stSidebar"] .stMarkdown {{
            color: #FFFFFF !important;
        }}
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
            color: #D6E4F0 !important;
        }}
        [data-testid="stSidebar"] .stRadio [data-baseweb="radio"] {{
            background-color: rgba(255,255,255,0.08);
            border-radius: 8px;
            padding: 4px 12px;
            margin-bottom: 4px;
        }}
        [data-testid="stSidebar"] .stRadio [data-baseweb="radio"]:hover {{
            background-color: rgba(255,255,255,0.15);
        }}

        /* Metric cards */
        [data-testid="stMetric"] {{
            background: #FFFFFF;
            border-radius: 10px;
            padding: 16px 20px;
            box-shadow: 0 2px 8px rgba(31, 78, 121, 0.10);
            border-left: 4px solid {BLUESTOCK_MEDIUM};
        }}
        [data-testid="stMetricLabel"] {{
            color: #555555 !important;
            font-size: 0.85rem !important;
        }}
        [data-testid="stMetricValue"] {{
            color: {BLUESTOCK_BLUE} !important;
            font-weight: 700 !important;
        }}

        /* DataFrame */
        [data-testid="stDataFrame"] {{
            border-radius: 8px;
            overflow: hidden;
        }}
        [data-testid="stDataFrame"] thead th {{
            background-color: {BLUESTOCK_BLUE} !important;
            color: #FFFFFF !important;
            font-weight: 600 !important;
        }}

        /* Headers */
        h1, h2, h3 {{
            color: {BLUESTOCK_BLUE} !important;
        }}

        /* Expander */
        [data-testid="stExpander"] {{
            border-radius: 8px;
            border: 1px solid #D6E4F0;
        }}

        /* Chart container card effect */
        .chart-card {{
            background: #FFFFFF;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 12px rgba(31, 78, 121, 0.08);
            margin-bottom: 1rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ────────── Data Loading (Cached) ──────────
@st.cache_data(ttl=600)
def load_sql_data(query: str, params=None) -> pd.DataFrame:
    """Execute a SQL query and return a DataFrame."""
    if not DB_PATH.exists():
        st.error(f"Database not found at {DB_PATH}")
        return pd.DataFrame()
    try:
        conn = sqlite3.connect(str(DB_PATH))
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Database query failed: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=600)
def load_csv(filename: str) -> pd.DataFrame:
    """Load a CSV from the processed directory."""
    fp = PROCESSED_DIR / filename
    if not fp.exists():
        return pd.DataFrame()
    return pd.read_csv(fp)


def fmt_inr_cr(val: float) -> str:
    """Format a value in crore to readable INR."""
    if val is None or pd.isna(val):
        return "N/A"
    if abs(val) >= 1e7:
        return f"₹{val/1e7:.2f}L Cr"
    if abs(val) >= 1e5:
        return f"₹{val/1e5:.2f}K Cr"
    if abs(val) >= 100:
        return f"₹{val:,.0f} Cr"
    return f"₹{val:,.2f}"


def fmt_num(val, decimals=2):
    """Safe numeric formatter."""
    if val is None or pd.isna(val):
        return "N/A"
    try:
        return f"{float(val):,.{decimals}f}"
    except (ValueError, TypeError):
        return str(val)


# ────────── Chart Styling Helpers ──────────
def chart_layout(fig, title=None, x_title=None, y_title=None, height=450):
    """Apply consistent Bluestock styling to a Plotly figure."""
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title=dict(text=title, font=dict(size=16, color=BLUESTOCK_BLUE, family="Segoe UI,Arial"), x=0.01)
        if title
        else None,
        xaxis=dict(title=x_title, gridcolor="#E8ECF0", tickfont=dict(color="#444444")),
        yaxis=dict(title=y_title, gridcolor="#E8ECF0", tickfont=dict(color="#444444")),
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Segoe UI,Arial"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=20, t=60, b=40),
        height=height,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0.01, font=dict(color="#555555")),
        dragmode=False,
    )
    return fig


# ────────── Sidebar ──────────
def render_sidebar():
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align:center; padding-bottom:10px;">
                <div style="font-size:2rem;">📊</div>
                <h2 style="color:#FFFFFF; margin:0; font-size:1.3rem;">Bluestock</h2>
                <p style="color:#D6E4F0; margin:0; font-size:0.8rem;">Mutual Fund Analytics</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("---")

        page = st.radio(
            "Navigation",
            [
                "🏠 Industry Overview",
                "📈 Fund Performance",
                "👥 Investor Analytics",
                "💰 SIP & Market Trends",
            ],
            label_visibility="collapsed",
        )

        st.markdown("---")
        st.markdown(
            """
            <div style="font-size:0.75rem; color:#B0C4D8;">
            <strong>About</strong><br>
            Comprehensive mutual fund analytics dashboard tracking
            industry trends, fund performance, investor behaviour,
            and SIP/market data.
            <br><br>
            Data sourced from AMFI, internal transactions,
            and market benchmarks.
            </div>
            """,
            unsafe_allow_html=True,
        )
        return page


# ═══════════════════════════════════════════
# PAGE 1: Industry Overview
# ═══════════════════════════════════════════
def page_industry_overview():
    st.markdown(
        "<h1 style='margin-bottom:0;'>Industry Overview</h1>"
        "<p style='color:#777; margin-top:0;'>Key metrics and trends across the Indian mutual fund industry</p>",
        unsafe_allow_html=True,
    )

    # ── KPI Cards ──
    aum_df = load_sql_data("SELECT * FROM fact_aum")
    sip_csv = load_csv("04_monthly_sip_inflows.csv")
    folio_csv = load_csv("06_industry_folio_count.csv")

    # Total AUM (latest date, lakh crore)
    total_aum_lc = 0
    total_schemes = 0
    if not aum_df.empty:
        latest_date = aum_df["date"].max()
        latest_aum = aum_df[aum_df["date"] == latest_date]
        total_aum_lc = latest_aum["aum_lakh_crore"].sum()
        total_schemes = int(latest_aum["num_schemes"].sum())

    # Latest SIP inflow (crore)
    latest_sip = 0
    if not sip_csv.empty:
        sip_csv["month_dt"] = pd.to_datetime(sip_csv["month"], errors="coerce")
        latest_row = sip_csv.loc[sip_csv["month_dt"].idxmax()]
        latest_sip = latest_row.get("sip_inflow_crore", 0)

    # Latest folios (crore)
    latest_folios = 0
    if not folio_csv.empty:
        folio_csv["month_dt"] = pd.to_datetime(folio_csv["month"], errors="coerce")
        folio_latest = folio_csv.loc[folio_csv["month_dt"].idxmax()]
        latest_folios = folio_latest.get("total_folios_crore", 0)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(
            "Total AUM",
            f"₹{total_aum_lc:,.2f}L Cr",
            help="Sum of AUM across all AMCs for latest quarter",
        )
    with c2:
        st.metric(
            "SIP Inflows (Monthly)",
            f"₹{latest_sip:,.0f} Cr",
            delta=f"{float(latest_sip):,.0f} Cr",
            delta_color="off",
            help="Latest monthly SIP inflow amount",
        )
    with c3:
        st.metric(
            "Folios",
            f"{latest_folios:,.2f} Cr",
            help="Total investor folios across the industry",
        )
    with c4:
        st.metric(
            "Schemes",
            f"{total_schemes:,}",
            help="Total number of mutual fund schemes",
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Industry AUM Trend ──
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.subheader("Industry AUM Trend (2022–2025)")
        if not aum_df.empty:
            aum_trend = aum_df.groupby("date")["aum_lakh_crore"].sum().reset_index()
            aum_trend["date"] = pd.to_datetime(aum_trend["date"])
            aum_trend = aum_trend.sort_values("date")

            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=aum_trend["date"],
                    y=aum_trend["aum_lakh_crore"],
                    mode="lines+markers",
                    line=dict(color=BLUESTOCK_MEDIUM, width=3),
                    marker=dict(size=8, color=BLUESTOCK_BLUE),
                    fill="tozeroy",
                    fillcolor="rgba(46, 117, 182, 0.12)",
                    name="Total AUM",
                    hovertemplate="<b>%{x|%b %Y}</b><br>AUM: ₹%{y:.2f} L Cr<extra></extra>",
                )
            )
            chart_layout(fig, x_title=None, y_title="AUM (₹ Lakh Crore)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("AUM data not available.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.subheader("AUM by AMC (Latest Quarter)")
        if not aum_df.empty:
            latest_date = aum_df["date"].max()
            latest_aum = aum_df[aum_df["date"] == latest_date].copy()
            latest_aum = latest_aum.sort_values("aum_lakh_crore", ascending=True)

            fig = go.Figure()
            fig.add_trace(
                go.Bar(
                    y=latest_aum["fund_house"],
                    x=latest_aum["aum_lakh_crore"],
                    orientation="h",
                    marker=dict(
                        color=latest_aum["aum_lakh_crore"],
                        colorscale=COLORSCALE_BLUES,
                        showscale=False,
                        line=dict(color=BLUESTOCK_BLUE, width=0.5),
                    ),
                    hovertemplate="<b>%{y}</b><br>AUM: ₹%{x:.2f} L Cr<extra></extra>",
                )
            )
            chart_layout(fig, x_title="AUM (₹ Lakh Crore)", y_title=None, height=420)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("AUM data not available.")
        st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════
# PAGE 2: Fund Performance
# ═══════════════════════════════════════════
def page_fund_performance():
    st.markdown(
        "<h1 style='margin-bottom:0;'>Fund Performance</h1>"
        "<p style='color:#777; margin-top:0;'>Risk-return analysis, NAV tracking, and fund comparison</p>",
        unsafe_allow_html=True,
    )

    # Load data
    perf_df = load_sql_data("SELECT * FROM fact_performance")
    fund_df = load_sql_data("SELECT * FROM dim_fund")
    nav_raw = load_sql_data("""
        SELECT f.amfi_code, f.scheme_name, n.nav, d.full_date
        FROM fact_nav n
        JOIN dim_date d ON n.date_id = d.date_id
        JOIN dim_fund f ON n.amfi_code = f.amfi_code
        ORDER BY d.full_date
    """)
    bench_csv = load_csv("10_benchmark_indices.csv")

    if perf_df.empty:
        st.warning("Fund performance data not available.")
        return

    # Preprocess
    if "fund_house" not in perf_df.columns and "scheme_name" in perf_df.columns and not fund_df.empty:
        perf_df = perf_df.merge(fund_df[["amfi_code", "fund_house", "plan", "sub_category"]], on="amfi_code", how="left")
        if "plan_x" in perf_df.columns:
            perf_df["plan"] = perf_df["plan_x"]
        if "sub_category" in perf_df.columns:
            perf_df["category_display"] = perf_df["sub_category"]
    else:
        if "category" in perf_df.columns:
            perf_df["category_display"] = perf_df["category"]
        else:
            perf_df["category_display"] = "All"

    fund_houses = ["All"] + sorted(perf_df["fund_house"].dropna().unique().tolist())
    categories = ["All"] + sorted(perf_df["category_display"].dropna().unique().tolist())
    plans = ["All"] + sorted(perf_df["plan"].dropna().unique().tolist())

    # ── Slicers ──
    c1, c2, c3 = st.columns(3)
    with c1:
        selected_house = st.selectbox("Fund House", fund_houses)
    with c2:
        selected_category = st.selectbox("Category", categories)
    with c3:
        selected_plan = st.selectbox("Plan", plans)

    # Filter
    filtered = perf_df.copy()
    if selected_house != "All":
        filtered = filtered[filtered["fund_house"] == selected_house]
    if selected_category != "All":
        filtered = filtered[filtered["category_display"] == selected_category]
    if selected_plan != "All":
        filtered = filtered[filtered["plan"] == selected_plan]

    if filtered.empty:
        st.warning("No funds match the selected filters.")
        return

    # ── Scatter Plot ──
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.subheader("Risk vs Return (3-Year)")

    scatter_df = filtered.dropna(subset=["return_3yr_pct", "std_dev_ann_pct"]).copy()
    if not scatter_df.empty:
        fig = px.scatter(
            scatter_df,
            x="return_3yr_pct",
            y="std_dev_ann_pct",
            size=scatter_df["aum_crore"].fillna(0).clip(lower=1),
            color="fund_house",
            hover_name="scheme_name",
            size_max=35,
            color_discrete_sequence=px.colors.qualitative.Set2,
            labels={
                "return_3yr_pct": "3-Year Return (%)",
                "std_dev_ann_pct": "Annualised Std Dev (%)",
                "fund_house": "AMC",
                "aum_crore": "AUM (₹ Cr)",
            },
        )
        fig.update_traces(marker=dict(line=dict(width=0.8, color="white")))
        chart_layout(fig, height=500)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Insufficient data for scatter plot.")
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Fund Scorecard Table ──
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.subheader("Fund Scorecard")

    score_cols = ["scheme_name", "return_3yr_pct", "sharpe_ratio", "alpha", "expense_ratio_pct", "aum_crore"]
    available_cols = [c for c in score_cols if c in filtered.columns]
    score_df = filtered[available_cols].copy()
    score_df = score_df.sort_values("return_3yr_pct", ascending=False)

    for col in available_cols:
        if col == "scheme_name":
            continue
        if pd.api.types.is_float_dtype(score_df[col]):
            score_df[col] = score_df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "—")
        elif col == "aum_crore":
            score_df[col] = score_df[col].apply(lambda x: f"₹{x:,.0f} Cr" if pd.notna(x) else "—")

    score_df.rename(
        columns={
            "scheme_name": "Scheme Name",
            "return_3yr_pct": "3Y Return (%)",
            "sharpe_ratio": "Sharpe Ratio",
            "alpha": "Alpha",
            "expense_ratio_pct": "Expense (%)",
            "aum_crore": "AUM (₹ Cr)",
        },
        inplace=True,
    )

    st.dataframe(
        score_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Scheme Name": st.column_config.TextColumn(width="large"),
        },
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # ── NAV Line Chart vs Benchmark ──
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.subheader("NAV Trend vs Benchmark")

    fund_names = sorted(perf_df["scheme_name"].dropna().unique())
    selected_fund = st.selectbox(
        "Select a fund to view NAV chart",
        fund_names,
        key="nav_fund_select",
    )

    fund_nav = nav_raw[nav_raw["scheme_name"] == selected_fund].copy() if not nav_raw.empty else pd.DataFrame()

    if not fund_nav.empty:
        fund_nav["full_date"] = pd.to_datetime(fund_nav["full_date"])
        fund_nav = fund_nav.sort_values("full_date").drop_duplicates(subset=["full_date"])

        # Normalise NAV to base 100
        base_nav = fund_nav["nav"].iloc[0] if len(fund_nav) > 0 else 100
        fund_nav["nav_idx"] = (fund_nav["nav"] / base_nav) * 100

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=fund_nav["full_date"],
                y=fund_nav["nav_idx"],
                mode="lines",
                name=f"{selected_fund} (NAV Base 100)",
                line=dict(color=BLUESTOCK_MEDIUM, width=2.5),
                hovertemplate="<b>%{x|%d %b %Y}</b><br>NAV Index: %{y:.2f}<extra></extra>",
            )
        )

        # Overlay NIFTY benchmark (normalised to same start date)
        if not bench_csv.empty:
            nifty = bench_csv[bench_csv["index_name"] == "NIFTY50"].copy()
            if not nifty.empty:
                nifty["date"] = pd.to_datetime(nifty["date"])
                nifty = nifty.sort_values("date")
                start_date = fund_nav["full_date"].min()
                nifty_window = nifty[nifty["date"] >= start_date]
                if not nifty_window.empty:
                    base_nifty = nifty_window["close_value"].iloc[0]
                    nifty_window = nifty_window.copy()
                    nifty_window["nifty_idx"] = (nifty_window["close_value"] / base_nifty) * 100
                    fig.add_trace(
                        go.Scatter(
                            x=nifty_window["date"],
                            y=nifty_window["nifty_idx"],
                            mode="lines",
                            name="NIFTY 50 (Base 100)",
                            line=dict(color=BLUESTOCK_ORANGE, width=2, dash="dot"),
                            hovertemplate="<b>%{x|%d %b %Y}</b><br>NIFTY Index: %{y:.2f}<extra></extra>",
                        )
                    )

        chart_layout(fig, y_title="Index (Base = 100)", height=450)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("NAV history data not available for this fund.")
    st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════
# PAGE 3: Investor Analytics
# ═══════════════════════════════════════════
def page_investor_analytics():
    st.markdown(
        "<h1 style='margin-bottom:0;'>Investor Analytics</h1>"
        "<p style='color:#777; margin-top:0;'>Transaction patterns, demographics, and investor behaviour</p>",
        unsafe_allow_html=True,
    )

    txn_df = load_sql_data("""
        SELECT * FROM fact_transactions
    """)

    if txn_df.empty:
        st.warning("Transaction data not available.")
        return

    txn_df["transaction_date"] = pd.to_datetime(txn_df["transaction_date"], errors="coerce")
    txn_df["month"] = txn_df["transaction_date"].dt.to_period("M").dt.to_timestamp()

    # ── Slicers ──
    c1, c2 = st.columns(2)
    with c1:
        states = ["All"] + sorted(txn_df["state"].dropna().unique().tolist())
        selected_state = st.selectbox("State", states)
    with c2:
        tiers = ["All"] + sorted(txn_df["city_tier"].dropna().unique().tolist())
        selected_tier = st.selectbox("City Tier", tiers)

    # Apply filters
    txn_filtered = txn_df.copy()
    if selected_state != "All":
        txn_filtered = txn_filtered[txn_filtered["state"] == selected_state]
    if selected_tier != "All":
        txn_filtered = txn_filtered[txn_filtered["city_tier"] == selected_tier]

    # ── Row 1: State bar + Donut ──
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.subheader("Transaction Amount by State")
        state_txn = txn_filtered.groupby("state")["amount_inr"].sum().reset_index()
        state_txn["amount_cr"] = state_txn["amount_inr"] / 1e7
        state_txn = state_txn.sort_values("amount_cr", ascending=True)

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                y=state_txn["state"],
                x=state_txn["amount_cr"],
                orientation="h",
                marker=dict(
                    color=state_txn["amount_cr"],
                    colorscale=COLORSCALE_BLUES,
                    showscale=False,
                    line=dict(color=BLUESTOCK_BLUE, width=0.5),
                ),
                hovertemplate="<b>%{y}</b><br>Amount: ₹%{x:.2f} Cr<extra></extra>",
            )
        )
        chart_layout(fig, x_title="Transaction Amount (₹ Cr)", height=400)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.subheader("Transaction Type Split")
        type_split = txn_filtered.groupby("transaction_type")["amount_inr"].sum().reset_index()
        type_split["pct"] = (type_split["amount_inr"] / type_split["amount_inr"].sum()) * 100

        colors_donut = {
            "SIP": BLUESTOCK_GREEN,
            "LUMPSUM": BLUESTOCK_MEDIUM,
            "REDEMPTION": BLUESTOCK_ORANGE,
        }

        fig = go.Figure()
        fig.add_trace(
            go.Pie(
                labels=type_split["transaction_type"],
                values=type_split["amount_inr"],
                hole=0.55,
                marker=dict(
                    colors=[colors_donut.get(t, BLUESTOCK_BLUE) for t in type_split["transaction_type"]],
                    line=dict(color="white", width=2),
                ),
                textinfo="label+percent",
                textfont=dict(size=12),
                hovertemplate="<b>%{label}</b><br>Amount: ₹%{value:,.0f}<br>Share: %{percent}<extra></extra>",
            )
        )
        chart_layout(fig, height=400)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Row 2: Age group + Monthly trend ──
    col_left2, col_right2 = st.columns([1, 2])

    with col_left2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.subheader("Avg SIP Amount by Age Group")
        sip_by_age = (
            txn_filtered[txn_filtered["transaction_type"] == "SIP"]
            .groupby("age_group")["amount_inr"]
            .mean()
            .reset_index()
        )
        sip_by_age["amount_disp"] = sip_by_age["amount_inr"].apply(lambda x: f"₹{x:,.0f}")

        # Sort by age group order
        age_order = ["18-25", "26-35", "36-45", "46-55", "56+"]
        sip_by_age["sort_key"] = sip_by_age["age_group"].apply(
            lambda x: age_order.index(x) if x in age_order else 99
        )
        sip_by_age = sip_by_age.sort_values("sort_key")

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=sip_by_age["age_group"],
                y=sip_by_age["amount_inr"],
                marker=dict(
                    color=[BLUESTOCK_MEDIUM if i % 2 == 0 else BLUESTOCK_BLUE for i in range(len(sip_by_age))],
                    line=dict(color="white", width=1),
                ),
                text=sip_by_age["amount_disp"],
                textposition="outside",
                textfont=dict(size=10, color="#444444"),
                hovertemplate="<b>%{x}</b><br>Avg SIP: ₹%{y:,.0f}<extra></extra>",
            )
        )
        chart_layout(fig, x_title="Age Group", y_title="Avg SIP (₹)", height=380)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right2:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.subheader("Monthly Transaction Volume")
        monthly_txn = txn_filtered.groupby("month").agg(
            total_amount=("amount_inr", "sum"),
            transaction_count=("transaction_id", "count"),
        ).reset_index()
        monthly_txn["total_cr"] = monthly_txn["total_amount"] / 1e7

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Bar(
                x=monthly_txn["month"],
                y=monthly_txn["total_cr"],
                name="Amount (₹ Cr)",
                marker=dict(color=BLUESTOCK_LIGHT_BLUE, line=dict(color=BLUESTOCK_MEDIUM, width=1)),
                hovertemplate="<b>%{x|%b %Y}</b><br>Amount: ₹%{y:.2f} Cr<extra></extra>",
            ),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(
                x=monthly_txn["month"],
                y=monthly_txn["transaction_count"],
                name="# Transactions",
                mode="lines+markers",
                line=dict(color=BLUESTOCK_ORANGE, width=2.5),
                marker=dict(size=6),
                hovertemplate="<b>%{x|%b %Y}</b><br>Transactions: %{y:,}<extra></extra>",
            ),
            secondary_y=True,
        )
        fig.update_layout(template=PLOTLY_TEMPLATE, height=400)
        fig.update_yaxes(title_text="Amount (₹ Cr)", secondary_y=False)
        fig.update_yaxes(title_text="# Txns", secondary_y=True)
        chart_layout(fig, height=400)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════
# PAGE 4: SIP & Market Trends
# ═══════════════════════════════════════════
def page_sip_market():
    st.markdown(
        "<h1 style='margin-bottom:0;'>SIP & Market Trends</h1>"
        "<p style='color:#777; margin-top:0;'>Systematic investment plan inflows vs market benchmarks</p>",
        unsafe_allow_html=True,
    )

    sip_csv = load_csv("04_monthly_sip_inflows.csv")
    bench_csv = load_csv("10_benchmark_indices.csv")
    cat_csv = load_csv("05_category_inflows.csv")

    # ── Dual-axis: SIP Inflow + NIFTY ──
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.subheader("Monthly SIP Inflows vs NIFTY 50")

    if not sip_csv.empty and not bench_csv.empty:
        sip_csv["month_dt"] = pd.to_datetime(sip_csv["month"])
        sip_csv = sip_csv.sort_values("month_dt")

        nifty = bench_csv[bench_csv["index_name"] == "NIFTY50"].copy()
        nifty["date"] = pd.to_datetime(nifty["date"])
        nifty_monthly = nifty.set_index("date").resample("ME")["close_value"].last().reset_index()

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Bar(
                x=sip_csv["month_dt"],
                y=sip_csv["sip_inflow_crore"],
                name="SIP Inflow (₹ Cr)",
                marker=dict(color=BLUESTOCK_MEDIUM, opacity=0.85, line=dict(color=BLUESTOCK_BLUE, width=0.5)),
                hovertemplate="<b>%{x|%b %Y}</b><br>SIP Inflow: ₹%{y:,.0f} Cr<extra></extra>",
            ),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(
                x=nifty_monthly["date"],
                y=nifty_monthly["close_value"],
                name="NIFTY 50",
                mode="lines+markers",
                line=dict(color=BLUESTOCK_ORANGE, width=2.5),
                marker=dict(size=5),
                hovertemplate="<b>%{x|%b %Y}</b><br>NIFTY: %{y:,.0f}<extra></extra>",
            ),
            secondary_y=True,
        )
        fig.update_layout(template=PLOTLY_TEMPLATE, height=450, hovermode="x unified")
        fig.update_yaxes(title_text="SIP Inflow (₹ Cr)", secondary_y=False, gridcolor="#E8ECF0")
        fig.update_yaxes(title_text="NIFTY 50", secondary_y=True, gridcolor="#E8ECF0")
        chart_layout(fig, height=450)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("SIP inflow or benchmark data not available.")
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Category Inflow Heatmap ──
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)

    if not cat_csv.empty:
        col_h, col_t = st.columns([3, 2])

        with col_h:
            st.subheader("Category Net Inflows Heatmap")
            cat_csv["month"] = pd.to_datetime(cat_csv["month"])
            pivot = cat_csv.pivot_table(
                index="category",
                columns="month",
                values="net_inflow_crore",
                aggfunc="sum",
            ).fillna(0)

            fig = px.imshow(
                pivot,
                labels=dict(x="Month", y="Category", color="Net Inflow (₹ Cr)"),
                aspect="auto",
                color_continuous_scale=[
                    [0, "#F5C6CB"],
                    [0.5, "#FFFFFF"],
                    [1, BLUESTOCK_GREEN],
                ],
            )
            fig.update_xaxes(side="bottom", tickangle=-45)
            chart_layout(fig, height=450)
            st.plotly_chart(fig, use_container_width=True)

        with col_t:
            st.subheader("Top 5 Categories by Net Inflow")
            # Latest year
            cat_csv["year"] = cat_csv["month"].dt.year
            latest_year = int(cat_csv["year"].max())
            year_data = cat_csv[cat_csv["year"] == latest_year]
            top_cats = year_data.groupby("category")["net_inflow_crore"].sum().reset_index()
            top_cats = top_cats.sort_values("net_inflow_crore", ascending=False).head(5)

            fig = go.Figure()
            fig.add_trace(
                go.Bar(
                    x=top_cats["net_inflow_crore"],
                    y=top_cats["category"],
                    orientation="h",
                    marker=dict(
                        color=top_cats["net_inflow_crore"],
                        colorscale=[
                            [0, BLUESTOCK_LIGHT_BLUE],
                            [1, BLUESTOCK_GREEN],
                        ],
                        showscale=False,
                        line=dict(color=BLUESTOCK_BLUE, width=0.5),
                    ),
                    hovertemplate="<b>%{y}</b><br>Net Inflow: ₹%{x:,.0f} Cr<extra></extra>",
                )
            )
            chart_layout(fig, x_title="Net Inflow (₹ Cr)", height=400)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Category inflows data not available.")
        st.subheader("Category Net Inflows Heatmap")
    st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════
def main():
    apply_custom_css()
    page = render_sidebar()

    if "Industry Overview" in page:
        page_industry_overview()
    elif "Fund Performance" in page:
        page_fund_performance()
    elif "Investor Analytics" in page:
        page_investor_analytics()
    elif "SIP & Market" in page:
        page_sip_market()


if __name__ == "__main__":
    main()
