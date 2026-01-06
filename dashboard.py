import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- Page Setup ----------------
st.set_page_config(
    page_title="APERD Analytics Dashboard",
    layout="wide"
)

st.title("📊 APERD Analytics Dashboard")

# ---------------- Sample Data ----------------
# Replace with your real 30-row dataset
df = pd.read_excel('dashboard.xlsx')  # or pd.read_excel()

# ---------------- Sidebar Controls ----------------
st.sidebar.header("Controls")

selected_aperd = st.sidebar.multiselect(
    "Select APERD",
    options=df["APERD"].unique(),
    default=df["APERD"].unique()
)

sort_metric = st.sidebar.selectbox(
    "Sort by",
    ["AUM (Bn)", "SID", "IFUA"]
)

top_n = st.sidebar.selectbox(
    "Show Top",
    ["All", 5, 10, 15]
)

filtered_df = df[df["APERD"].isin(selected_aperd)]
filtered_df = filtered_df.sort_values(sort_metric, ascending=False)

if top_n != "All":
    filtered_df = filtered_df.head(top_n)

# ---------------- KPI Summary ----------------
st.subheader("📌 Overall Summary")

col1, col2, col3 = st.columns(3)
col1.metric("Total SID", f"{filtered_df['SID'].sum():,.0f}")
col2.metric("Total IFUA", f"{filtered_df['IFUA'].sum():,.0f}")
col3.metric("Total AUM (Bn)", f"{filtered_df['AUM (Bn)'].sum():,.2f}")

# ---------------- Financial Metrics Chart ----------------
st.subheader("💰 Financial Metrics Comparison")

metric = st.radio(
    "Metric",
    ["AUM (Bn)", "SID", "IFUA"],
    horizontal=True
)

fig_fin = px.bar(
    filtered_df,
    x=metric,
    y="APERD",
    orientation="h",
    color=metric,
    color_continuous_scale="Blues",
    title=f"{metric} by APERD"
)

fig_fin.update_layout(
    yaxis_title="APERD",
    xaxis_title=metric,
    height=600,
    coloraxis_showscale=False
)

st.plotly_chart(fig_fin, use_container_width=True)

# ---------------- Generation Distribution ----------------
st.subheader("👥 Investor Generation Mix (Percentage View)")

gen_cols = ["Baby Boomers", "Gen X", "Gen Y", "Gen Z", "Alpha"]

gen_df = filtered_df.copy()
gen_df["Total"] = gen_df[gen_cols].sum(axis=1)

for col in gen_cols:
    gen_df[col] = gen_df[col] / gen_df["Total"] * 100

gen_melt = gen_df.melt(
    id_vars="APERD",
    value_vars=gen_cols,
    var_name="Generation",
    value_name="Percentage"
)

fig_gen = px.bar(
    gen_melt,
    x="Percentage",
    y="APERD",
    color="Generation",
    orientation="h",
    title="Generation Distribution by APERD (100%)",
    color_discrete_sequence=px.colors.qualitative.Set2
)

fig_gen.update_layout(
    xaxis_title="Percentage (%)",
    yaxis_title="APERD",
    height=600
)

st.plotly_chart(fig_gen, use_container_width=True)

# ---------------- Data Table ----------------
with st.expander("📄 View Raw Data"):
    st.dataframe(filtered_df, use_container_width=True)
