# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Load and clean data ---
st.set_page_config(
    page_title="Fund Dashboard",
    layout="wide"
)
@st.cache_data
def load_data():
    df = pd.read_excel("dashboard.xlsx")
    df.columns = df.columns.str.strip()  # remove extra spaces
    return df

df = load_data()

st.title("📊 Fund Dashboard by Generation, Gender, and Aperd")

# --- Sidebar Filters ---
st.sidebar.header("Filters")

# Aperd selection
aperd_options = df['Aperd'].unique().tolist()
selected_aperd = st.sidebar.multiselect("Select Aperd", aperd_options, default=None)

# Fund options dependent on selected Aperd
fund_options = df[df['Aperd'].isin(selected_aperd)]['FundName'].unique().tolist()
if fund_options:
    selected_fund = st.sidebar.multiselect("Select FundName", fund_options, default=fund_options)
else:
    # st.sidebar.warning("No funds available for the selected Aperd(s).")
    selected_fund = []

# Filter dataframe
filtered_df = df[
    (df['Aperd'].isin(selected_aperd)) &
    (df['FundName'].isin(selected_fund))
]

if filtered_df.empty:
    st.warning("Select Aperd/multiple Aperd in sidebar to show the graphics.")
else:

    # --- Generations ---
    generations = ["Gen Baby Boomers", "Gen X", "Gen Y", "Gen Z", "Gen Alpha"]

    # --- Aggregate metrics by Aperd & Generation ---
    agg_data = []
    for aperd in filtered_df['Aperd'].unique():
        temp = filtered_df[filtered_df['Aperd'] == aperd]
        for gen in generations:
            female_col = f"Female {gen}"
            male_col = f"Male {gen}"
            aum_col = f"AUM {gen}"
            total_female = temp[female_col].sum()
            total_male = temp[male_col].sum()
            total_clients = total_female + total_male
            total_aum = temp[aum_col].sum()
            avg_aum_per_client = total_aum / total_clients if total_clients > 0 else 0
            female_ratio = total_female / total_clients if total_clients > 0 else 0
            male_ratio = total_male / total_clients if total_clients > 0 else 0
            agg_data.append({
                "Aperd": aperd,
                "Generation": gen,
                "Female": total_female,
                "Male": total_male,
                "Total Clients": total_clients,
                "Female Ratio": female_ratio,
                "Male Ratio": male_ratio,
                "Total AUM": total_aum,
                "Avg AUM per Client": avg_aum_per_client
            })

    agg_df = pd.DataFrame(agg_data)

    # --- Aggregated table ---
    st.subheader("Aggregated Metrics by Aperd and Generation")
    st.dataframe(agg_df.style.format({
        "Female Ratio": "{:.1%}",
        "Male Ratio": "{:.1%}",
        "Total AUM": "Rp{:,.0f}",
        "Avg AUM per Client": "Rp{:,.0f}"
    }))

    # --- Clients per Generation (Stacked Bar) ---
    st.subheader("Total Clients by Generation and Aperd")
    fig_clients = px.bar(
        agg_df,
        x="Generation",
        y="Total Clients",
        color="Aperd",
        barmode="stack",
        title="Total Clients by Generation and Aperd",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig_clients, use_container_width=True, key="clients_bar")

    # --- Total AUM per Generation (Stacked Bar) ---
    st.subheader("Total AUM by Generation and Aperd")
    fig_aum = px.bar(
        agg_df,
        x="Generation",
        y="Total AUM",
        color="Aperd",
        barmode="stack",
        title="Total AUM by Generation and Aperd",
        color_discrete_sequence=px.colors.qualitative.Set2,
        # text="Total AUM"
    )
    st.plotly_chart(fig_aum, use_container_width=True, key="aum_bar")

    # --- Gender Ratio pies (1 row per Aperd) ---
    st.subheader("Gender Ratio per Aperd and Generation (1 Row per Aperd)")

    for aperd in agg_df['Aperd'].unique():
        st.markdown(f"**{aperd}**")
        
        # Create 1 row with columns equal to number of generations
        cols = st.columns(len(generations))
        
        for i, gen in enumerate(generations):
            temp = agg_df[(agg_df['Aperd'] == aperd) & (agg_df['Generation'] == gen)]
            
            # Only draw pie if there is data
            if not temp.empty and (temp["Female"].values[0] + temp["Male"].values[0]) > 0:
                fig = px.pie(
                    names=["Female", "Male"],
                    values=[temp["Female"].values[0], temp["Male"].values[0]],
                    title=gen,
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
            else:
                # Draw empty pie for generations with no clients
                fig = px.pie(
                    names=["No Data"],
                    values=[1],
                    title=gen,
                    color_discrete_sequence=["#d3d3d3"]
                )
            
            cols[i].plotly_chart(fig, use_container_width=True, key=f"{aperd}_{gen}_pie")
    

    # --- Average AUM per Client ---
    st.subheader("Average AUM per Client by Generation and Aperd")
    fig_avg_aum = px.bar(
        agg_df,
        x="Generation",
        y="Avg AUM per Client",
        color="Aperd",
        barmode="group",
        title="Average AUM per Client by Generation and Aperd",
        color_discrete_sequence=px.colors.qualitative.Set2,
        # text="Avg AUM per Client"
    )
    st.plotly_chart(fig_avg_aum, use_container_width=True, key="avg_aum_bar")

    # --- Heatmap: AUM by Fund and Aperd ---
    st.subheader("AUM Heatmap by Fund and Aperd")
    heatmap_df = filtered_df.groupby(["FundName", "Aperd"])[[f"AUM {gen}" for gen in generations]].sum()
    fig_heatmap = go.Figure(data=go.Heatmap(
        z=heatmap_df.values,
        x=generations,
        y=[f"{fund} | {aperd}" for fund, aperd in heatmap_df.index],
        colorscale="turbo",
        hovertemplate="Fund & Aperd: %{y}<br>Generation: %{x}<br>AUM: %{z:Rp,.0f}<extra></extra>"
    ))
    fig_heatmap.update_layout(title="AUM Heatmap by Fund and Aperd", height=400 + 30*len(heatmap_df))
    st.plotly_chart(fig_heatmap, use_container_width=True, key="heatmap")

    # --- Heatmap: AUM by Fund and Aperd with y-axis on right and colorbar on left ---
    # st.subheader("AUM Heatmap by Fund and Aperd (y-axis right, colorbar left)")

    # heatmap_df = filtered_df.groupby(["FundName", "Aperd"])[[f"AUM {gen}" for gen in generations]].sum()

    # # Prepare z, x, y
    # z = heatmap_df.values
    # x = generations
    # y = [f"{fund} | {aperd}" for fund, aperd in heatmap_df.index]

    # fig_heatmap = go.Figure(data=go.Heatmap(
    #     z=z,
    #     x=x,
    #     y=y,
    #     colorscale="Viridis",
    #     hovertemplate="Fund & Aperd: %{y}<br>Generation: %{x}<br>AUM: %{z:$,.0f}<extra></extra>",
    #     colorbar=dict(
    #         title="Total AUM",
    #         x=-1,         # move colorbar to the left outside the plot
    #         xanchor="left", # anchor the colorbar to the left
    #         y=0.5,          # center vertically
    #         len=1,          # full height
    #         thickness=20
    #     )
    # ))

    # fig_heatmap.update_layout(
    #     title=f"AUM Heatmap - {aperd}",
    #     yaxis=dict(side="right"),
    #     xaxis_title="Generation",
    #     yaxis_title="Fund | Aperd",
    #     margin=dict(l=80, r=80, t=50, b=50),  # leave space for colorbar on the left
    #     height=400 + 30*len(heatmap_df)
    # )

    # st.plotly_chart(fig_heatmap, use_container_width=True, key=f"heatmap_{aperd}")

    # --- Dynamic Rankings ---
    st.subheader("🏆 Top Rankings")

    # Top Aperd by Total Clients
    st.markdown("**Top Aperd by Total Clients**")
    top_aperd_clients = filtered_df.groupby("Aperd")[[f"Female {gen}" for gen in generations] + [f"Male {gen}" for gen in generations]].sum()
    top_aperd_clients["Total Clients"] = top_aperd_clients.sum(axis=1)
    top_aperd_clients = top_aperd_clients.sort_values("Total Clients", ascending=False).reset_index()
    st.table(top_aperd_clients[["Aperd", "Total Clients"]])

    # Top Aperd by Total AUM
    st.markdown("**Top Aperd by Total AUM**")
    top_aperd_aum = filtered_df.groupby("Aperd")[[f"AUM {gen}" for gen in generations]].sum()
    top_aperd_aum["Total AUM"] = top_aperd_aum.sum(axis=1)
    top_aperd_aum = top_aperd_aum.sort_values("Total AUM", ascending=False).reset_index()
    st.table(top_aperd_aum[["Aperd", "Total AUM"]].style.format({"Total AUM": "Rp{:,.0f}"}))

    # Top Fund by Total Clients
    st.markdown("**Top Fund by Total Clients**")
    top_fund_clients = filtered_df.groupby("FundName")[[f"Female {gen}" for gen in generations] + [f"Male {gen}" for gen in generations]].sum()
    top_fund_clients["Total Clients"] = top_fund_clients.sum(axis=1)
    top_fund_clients = top_fund_clients.sort_values("Total Clients", ascending=False).reset_index()
    st.table(top_fund_clients[["FundName", "Total Clients"]])

    # Top Fund by Total AUM
    st.markdown("**Top Fund by Total AUM**")
    top_fund_aum = filtered_df.groupby("FundName")[[f"AUM {gen}" for gen in generations]].sum()
    top_fund_aum["Total AUM"] = top_fund_aum.sum(axis=1)
    top_fund_aum = top_fund_aum.sort_values("Total AUM", ascending=False).reset_index()
    st.table(top_fund_aum[["FundName", "Total AUM"]].style.format({"Total AUM": "Rp{:,.0f}"}))

    # --- Raw Data ---
    with st.expander("Show Raw Data"):
        st.dataframe(filtered_df)
