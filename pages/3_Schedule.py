import streamlit as st
import pandas as pd
from src.data_access import load_scheduling, save_scheduling
from src.utils import filter_dataframe

st.title("🗓️ Schedule")

# Carica dati
df = load_scheduling()

# Colonne mese da escludere dai filtri
month_prefixes = ["gen","feb","mar","apr","mag","giu","lug","ago","set","ott","nov","dic"]
month_cols = [c for c in df.columns if c[:3].lower() in month_prefixes]

# Applichiamo filtri solo sulle colonne non-mese
non_month_df = df.drop(columns=month_cols, errors="ignore")
filtered_non_month = filter_dataframe(non_month_df)

# Manteniamo lo stesso subset di righe sul df completo
filtered_full = df.loc[filtered_non_month.index]

st.dataframe(filtered_full, use_container_width=True)

st.info("Editing grid coming soon – consider using streamlit-aggrid or handsontable.")
