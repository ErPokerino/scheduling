
import streamlit as st
import pandas as pd
from src.data_access import load_scheduling, save_scheduling, load_lovs

st.title("📋 Projects")

df = load_scheduling()

with st.expander("Add a new project"):
    with st.form(key="add_project"):
        cols = st.columns(2)
        project_descr = cols[0].text_input("Project description")
        client = cols[1].text_input("Client")
        item_type = st.selectbox("Item type", load_lovs()["ITEM_TYPE"].dropna().unique())
        delivery_type = st.selectbox("Delivery type", load_lovs()["DELIVERY_TYPE"].dropna().unique())
        start_date = st.date_input("Start date")
        end_date = st.date_input("End date")
        submitted = st.form_submit_button("Add")

    if submitted:
        new_row = {
            "PROJECT_DESCR": project_descr,
            "CLIENT": client,
            "ITEM_TYPE": item_type,
            "DELIVERY_TYPE": delivery_type,
            "START_DATE": pd.to_datetime(start_date),
            "END_DATE": pd.to_datetime(end_date),
        }
        df = df.append(new_row, ignore_index=True)
        save_scheduling(df)
        st.success("Project added!")

st.subheader("Existing projects")
st.dataframe(df[['PROJECT_DESCR','CLIENT','START_DATE','END_DATE']])
