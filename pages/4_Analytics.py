import streamlit as st
import pandas as pd
import plotly.express as px
from src.data_access import load_scheduling

st.title("📈 Analytics – Resource Allocation")

# Load data
df = load_scheduling()

# Month columns
month_prefixes = ["gen","feb","mar","apr","mag","giu","lug","ago","set","ott","nov","dic"]
month_cols = [c for c in df.columns if c[:3].lower() in month_prefixes and not c.lower().endswith("1")]

# Ensure year column
if "YEAR" not in df.columns:
    if "START_DATE" in df.columns:
        df["YEAR"] = pd.to_datetime(df["START_DATE"], errors="coerce").dt.year.astype("Int64")
    else:
        df["YEAR"] = pd.NA

# Cast to int for selector, ignore NA
years = sorted(df["YEAR"].dropna().astype(int).unique())
selected_year = st.selectbox("Select year", options=years, index=len(years)-1 if years else 0)
df_year = df[df["YEAR"] == selected_year] if years else df

# Melt dataframe to long format with FTE
long_df = df_year.melt(id_vars=df_year.columns.difference(month_cols), value_vars=month_cols, var_name="MONTH", value_name="FTE")

# Pie Chart – % FTE by selected dimension
st.subheader("FTE distribution")
dimension = st.selectbox("Group by", ["AREA_CC", "ITEM_TYPE", "CLIENT", "PM", "STATUS"], index=0)

pie_df = long_df.groupby(dimension, as_index=False)["FTE"].sum()

fig_pie = px.pie(pie_df, names=dimension, values="FTE", title=f"FTE % by {dimension} – {selected_year}")
fig_pie.update_traces(textposition='inside', textinfo='percent+label')
st.plotly_chart(fig_pie, use_container_width=True)

# Monthly workload line/bar per user
st.subheader("Monthly FTE per user")

# Independent year selector for this chart
year_user = st.selectbox("Select year for user chart", options=years, index=len(years)-1 if years else 0, key="year_user_chart")

df_user_year = df[df["YEAR"] == year_user] if years else df

long_user = df_user_year.melt(id_vars=df_user_year.columns.difference(month_cols), value_vars=month_cols, var_name="MONTH", value_name="FTE")

user_filter = st.multiselect("Filter users", sorted(df_user_year["USER"].dropna().unique()), key="user_filter")

# Only proceed if at least one user selected
if user_filter:
    long_user = long_user[long_user["USER"].isin(user_filter)]
    user_month = long_user.groupby(["USER", "MONTH"], as_index=False)["FTE"].sum()
    fig_user = px.line(user_month, x="MONTH", y="FTE", color="USER", markers=True, title=f"Monthly FTE – {year_user}")
    st.plotly_chart(fig_user, use_container_width=True)
else:
    st.info("Select at least one user to visualize the chart.")
