
import streamlit as st
import pandas as pd
import plotly.express as px
from src.data_access import load_scheduling

st.title("📈 Analytics")

df = load_scheduling()

df_melt = df.melt(id_vars=['USER'], value_vars=[c for c in df.columns if c[:3] in ['gen','feb','mar','apr','mag','giu','lug','ago','set','ott','nov','dic']], var_name="month", value_name="fte")

agg = df_melt.groupby(['USER','month'], as_index=False)['fte'].sum()

st.write("Total FTE by user and month")

fig = px.bar(agg, x='month', y='fte', color='USER')
st.plotly_chart(fig, use_container_width=True)
