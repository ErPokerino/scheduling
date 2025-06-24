import streamlit as st
import pandas as pd
from src.data_access import load_scheduling, save_scheduling
from src.utils import filter_dataframe

st.set_page_config(page_title="Scheduling", page_icon="📅", layout="wide")

st.title("📅 Scheduling – Resource Planning")

# Caricamento dati di schedulazione

df = load_scheduling()

# Identifichiamo colonne mese
month_prefixes = ["gen","feb","mar","apr","mag","giu","lug","ago","set","ott","nov","dic"]
month_cols = [c for c in df.columns if c[:3].lower() in month_prefixes]

# Filtriamo solo su colonne non-mese
non_month_df = df.drop(columns=month_cols, errors="ignore")
filtered_non_month = filter_dataframe(non_month_df)
filtered_full = df.loc[filtered_non_month.index]

st.dataframe(filtered_full, use_container_width=True)

st.info("Editing grid coming soon – consider using streamlit-aggrid or handsontable.")
