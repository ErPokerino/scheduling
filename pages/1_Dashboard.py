
import streamlit as st
import pandas as pd
from src.data_access import load_scheduling

st.title("📊 Dashboard")

df = load_scheduling()
st.subheader("Upcoming Projects")
st.dataframe(df[['PROJECT_DESCR','CLIENT','START_DATE','END_DATE','STATUS']].sort_values('START_DATE').head(15))

st.subheader("Workload Snapshot")
st.caption("Placeholder for KPIs and charts (e.g., capacity vs allocation).")
