
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="StockScope",
    page_icon="📊",
    layout="wide"
)
st.markdown("""
<style>
/* Make financial metric titles white */
[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] p {
    color: #F1F5F9 !important;
    }
/* Make sidebar filter labels white */
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] label p {
    color: #F1F5F9 !important;
}
/* Improve general text readability */
.stApp p {
    color: #E2E8F0;
}

    .stApp {
        background-color: #0B1426;
        color: #F1F5F9;
    }

    h1, h2, h3 {
        color: #E2E8F0 !important;
    }

    [data-testid="stSidebar"] {
        background-color: #14233B;
    }

    [data-testid="stMetric"] {
        background-color: #1B2D49;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #34547A;
    }

    [data-testid="stMetricValue"] {
        color: #60A5FA;
    }
</style>
""", unsafe_allow_html=True)
st.title("StockScope 📊")
st.subheader("Discover the Warning Signs Behind Every Stock")

st.write(
    "Analyze companies using key financial indicators, including "
    "Gross Profitability (GPA), Sloan Accruals (STA), and Book-to-Market (B/M). "
    "Customize screening criteria, uncover potential financial weaknesses, "
    "and identify stocks that may be candidates for selling."
)

@st.cache_data
def load_data():
    return pd.read_csv("short_analysis_data.csv")

df = load_data()

st.sidebar.header("Financial Screening Filters")

gpa_limit = st.sidebar.slider(
    "Maximum Gross Profitability (GPA)",
    0.0, 1.0, 0.25, 0.01
)

sta_limit = st.sidebar.slider(
    "Minimum Sloan Accruals (STA)",
    -0.20, 0.20, 0.00, 0.01
)

bm_limit = st.sidebar.slider(
    "Maximum Book-to-Market (B/M)",
    0.0, 1.0, 0.10, 0.01
)

min_signals = st.sidebar.slider(
    "Minimum Warning Signals for SELL",
    1, 3, 2
)

sectors = st.sidebar.multiselect(
    "Select Sectors",
    sorted(df["sector"].dropna().unique()),
    default=sorted(df["sector"].dropna().unique())
)

df = df[df["sector"].isin(sectors)].copy()

# Financial warning signals
df["Low GPA"] = df["GPA"] < gpa_limit
df["High STA"] = df["STA"] > sta_limit
df["Low B/M"] = (
    df["valid_BM"].fillna(False).astype(bool)
    & (df["BM"] < bm_limit)
)

df["Warning Signals"] = (
    df["Low GPA"].astype(int)
    + df["High STA"].astype(int)
    + df["Low B/M"].astype(int)
)

df["Recommendation"] = df["Warning Signals"].apply(
    lambda x: "Potential SELL"
    if x >= min_signals else "No SELL Signal"
)

sell = df[df["Recommendation"] == "Potential SELL"]

col1, col2, col3 = st.columns(3)
col1.metric("Companies Screened", len(df))
col2.metric("Potential SELL Candidates", len(sell))
col3.metric("SELL Percentage",
            f"{len(sell)/len(df)*100:.1f}%"
            if len(df) else "0.0%")

st.subheader("Potential SELL Candidates")
st.dataframe(
    sell[
        ["ticker", "company", "sector", "GPA",
         "STA", "BM", "Warning Signals",
         "Recommendation"]
    ].sort_values("Warning Signals", ascending=False),
    use_container_width=True
)

st.subheader("📊 Potential SELL Candidates by Sector")

if not sell.empty:
    sector_counts = sell["sector"].value_counts()
    st.bar_chart(sector_counts)
else:
    st.info("No SELL candidates match the current filters.")
st.subheader("Financial Warning Signal Breakdown")

st.bar_chart(
    pd.Series({
        "Low GPA": int(df["Low GPA"].sum()),
        "High STA": int(df["High STA"].sum()),
        "Low B/M": int(df["Low B/M"].sum())
    })
)

st.subheader("Financial Interpretation")
st.write("""
**Low GPA:** Lower gross profit relative to total assets
may indicate weaker asset profitability.

**High STA:** Higher accruals suggest earnings may be
less supported by operating cash flow.

**Low B/M:** A low book-to-market ratio may indicate
a relatively high market valuation compared with
accounting book equity.

**Important:** These are screening signals, not proof
of overvaluation or a recommendation to short a stock.
The results depend on the selected thresholds.
""")

st.subheader("All Screened Companies")
st.dataframe(df, use_container_width=True)

st.download_button(
    "Download SELL Candidates",
    sell.to_csv(index=False),
    "sell_candidates.csv",
    "text/csv"
)



# Investment Conclusions
st.header("Investment Conclusions")

st.write(
    "The following companies are potential SELL candidates "
    "based on the financial screening thresholds selected."
)

if sell.empty:
    st.info("No companies currently meet the SELL criteria.")
else:
    top_candidates = sell.sort_values(
        "Warning Signals", ascending=False
    ).head(5)

    for _, company in top_candidates.iterrows():
        st.subheader(
            f"{company['ticker']} - {company['company']}"
        )

        reasons = []

        if company["Low GPA"]:
            reasons.append(
                "Low gross profitability may indicate "
                "weaker operating performance."
            )

        if company["High STA"]:
            reasons.append(
                "High Sloan accruals may suggest earnings "
                "are less supported by operating cash flow."
            )

        if company["Low B/M"]:
            reasons.append(
                "Low book-to-market may indicate a "
                "relatively high market valuation."
            )

        st.write(
            f"**Warning Signals: {company['Warning Signals']}**"
        )

        for reason in reasons:
            st.write("- " + reason)

        st.write(
            "**Conclusion:** This company warrants further "
            "investigation as a potential SELL candidate. "
            "These screening signals alone do not prove "
            "that the stock is overvalued."
        )

        st.divider()
