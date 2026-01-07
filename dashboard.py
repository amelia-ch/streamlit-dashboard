import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# Page & Theme
# --------------------------------------------------
st.set_page_config(
    page_title="Generational AUM Dashboard",
    layout="wide"
)

st.markdown("""
<style>
    .block-container {padding-top: 2rem;}
    h1, h2, h3 {color: #003366;}
</style>
""", unsafe_allow_html=True)

st.title("📊 Generational Investors & AUM Dashboard")

# --------------------------------------------------
# Load Data
# --------------------------------------------------
DATA_PATH = "dashboard.xlsx"

@st.cache_data
def load_data():
    df = pd.read_excel(DATA_PATH)
    df["Aperd"] = df["Aperd"].astype(str)
    return df

df = load_data()

# --------------------------------------------------
# Sidebar Controls (Cascading Filters)
# --------------------------------------------------
st.sidebar.header("Controls")

metric_type = st.sidebar.radio(
    "Metric",
    ["AUM", "Investors"]
)

# Aperd filter
aperd_order = list(df["Aperd"].dropna().unique())

aperd_sel = st.sidebar.multiselect(
    "Aperd",
    options=aperd_order,
    default=None
)

df_aperd_filtered = df[df["Aperd"].isin(aperd_sel)]

# Fund filter depends on Aperd
available_funds = sorted(df_aperd_filtered["FundName"].unique())

fund_sel = st.sidebar.multiselect(
    "Fund Name",
    options=available_funds,
    default=available_funds
)

filtered_df = df_aperd_filtered[
    df_aperd_filtered["FundName"].isin(fund_sel)
]

if filtered_df.empty:
    st.warning("No data available for the selected filters. Choose Aperd/multiple Aperd in sidebar to show the Graphics.")
    st.stop()

# --------------------------------------------------
# Column Definitions
# --------------------------------------------------
gen_cols = {
    "Baby Boomers": ("Baby Boomers", "AUM Baby Boomers"),
    "Gen X": ("Gen X", "AUM Gen X"),
    "Gen Y": ("Gen Y", "AUM Gen Y"),
    "Gen Z": ("Gen Z", "AUM Gen Z"),
    "Gen Alpha": ("Gen Alpha", "AUM Gen Alpha"),
}

value_cols = [
    v[0] if metric_type == "Investors" else v[1]
    for v in gen_cols.values()
]

# --------------------------------------------------
# KPI
# --------------------------------------------------
total_value = filtered_df[value_cols].sum().sum()

st.metric(
    f"Total {metric_type}",
    f"{total_value:,.2f}" if metric_type == "AUM" else f"{int(total_value):,}"
)

# --------------------------------------------------
# % Share by Generation
# --------------------------------------------------
share_df = (
    filtered_df[value_cols]
    .sum()
    .reset_index()
)

share_df.columns = ["Generation", "Value"]
share_df["% Share"] = share_df["Value"] / share_df["Value"].sum() * 100

fig_share = px.pie(
    share_df,
    names="Generation",
    values="% Share",
    hole=0.45,
    title=f"% Share by Generation ({metric_type})"
)

# --------------------------------------------------
# Bar Chart by Aperd (Categorical)
# --------------------------------------------------
aperd_df = (
    filtered_df
    .groupby("Aperd", observed=True)[value_cols]
    .sum()
    .reset_index()
)

aperd_df = aperd_df.melt(
    id_vars="Aperd",
    var_name="Generation",
    value_name="Value"
)

fig_aperd = px.bar(
    aperd_df,
    x="Aperd",
    y="Value",
    color="Generation",
    barmode="group",
    title=f"{metric_type} by Aperd"
)

fig_aperd.update_xaxes(
    categoryorder="array",
    categoryarray=aperd_order
)

# --------------------------------------------------
# Fund-wise Stacked Bar
# --------------------------------------------------
fund_df = (
    filtered_df
    .groupby("FundName")[value_cols]
    .sum()
    .reset_index()
)

fund_df = fund_df.melt(
    id_vars="FundName",
    var_name="Generation",
    value_name="Value"
)

fig_fund = px.bar(
    fund_df,
    x="FundName",
    y="Value",
    color="Generation",
    barmode="stack",
    title=f"Fund-wise {metric_type} Distribution"
)

# --------------------------------------------------
# Layout
# --------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig_aperd, use_container_width=True)

with col2:
    st.plotly_chart(fig_share, use_container_width=True)

st.plotly_chart(fig_fund, use_container_width=True)

# --------------------------------------------------
# Data Preview
# --------------------------------------------------
with st.expander("📄 View Filtered Data"):
    st.dataframe(filtered_df, use_container_width=True)
