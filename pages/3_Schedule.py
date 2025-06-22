
import streamlit as st
import pandas as pd
from src.data_access import load_scheduling, save_scheduling

st.title("🗓️ Schedule")

df = load_scheduling()

st.dataframe(df)

st.info("Editing grid coming soon – consider using streamlit-aggrid or handsontable.")
