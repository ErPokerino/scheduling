# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from src.data_access import load_scheduling

st.set_page_config(page_title="Analytics", page_icon="📈", layout="wide")

st.title("📈 Analytics – Resource Allocation & Project Insights")

# =======================
# GESTIONE DATI CONDIVISI
# =======================
from src.utils import show_data_update_info
show_data_update_info()

# Load data
@st.cache_data
def load_data():
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
    return df, month_cols

df, month_cols = load_data()

# =======================
# DASHBOARD KPI
# =======================
st.header("🎯 Dashboard KPI")

total_projects = int(df["PROJECT_DESCR"].nunique())
total_users = int(df["USER"].nunique()) if "USER" in df.columns else 0
total_clients = int(df["CLIENT"].nunique()) if "CLIENT" in df.columns else 0
total_pms = int(df["PM_SM"].nunique()) if "PM_SM" in df.columns else 0

if month_cols:
    total_fte_by_year = df.groupby("YEAR")[month_cols].sum().sum(axis=1)
    current_year_fte = float(total_fte_by_year.iloc[-1]) if len(total_fte_by_year) > 0 else 0.0
else:
    current_year_fte = 0.0

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("📊 Progetti Totali", total_projects)
with col2:
    st.metric("👥 Utenti", total_users)
with col3:
    st.metric("🏢 Clienti", total_clients)
with col4:
    st.metric("👨‍💼 Project Manager", total_pms)
with col5:
    st.metric("⚡ FTE Anno Corrente", f"{current_year_fte:.1f}")

# =======================
# SELEZIONE REPORT SPECIFICO
# =======================
st.header("📋 Report Specifici")

report_type = st.selectbox(
    "Seleziona tipo di report",
    ["Dashboard Generale", "Report per Progetto", "Report per Utente", "Report per PM", "Report per Cliente"],
    index=0
)

# =======================
# DASHBOARD GENERALE
# =======================
if report_type == "Dashboard Generale":
    st.subheader("📊 Panoramica Generale")
    years = sorted([int(y) for y in pd.Series(df["YEAR"]).dropna().unique()])
    selected_year = st.selectbox("Seleziona anno", options=years, index=len(years)-1 if years else 0)
    df_year = df[df["YEAR"] == selected_year] if years else df
    df_year = pd.DataFrame(df_year)  # Forza DataFrame
    long_df = df_year.melt(id_vars=df_year.columns.difference(month_cols), value_vars=month_cols, var_name="MONTH", value_name="FTE")
    col1, col2 = st.columns(2)
    with col1:
        dimension = st.selectbox("Raggruppa per", ["AREA_CC", "ITEM_TYPE", "CLIENT", "PM_SM", "STATUS"], index=0)
        if dimension in df_year.columns:
            pie_df = long_df.groupby(dimension, as_index=False)["FTE"].sum()
            pie_df = pie_df[pie_df["FTE"] > 0]
            if pie_df.shape[0] > 0:
                fig_pie = px.pie(pie_df, names=dimension, values="FTE", title=f"Distribuzione FTE per {dimension} - {selected_year}")
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info(f"Nessun dato FTE disponibile per {dimension}")
    with col2:
        monthly_fte = long_df.groupby("MONTH")["FTE"].sum().reset_index()
        month_order = ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"]
        monthly_fte["MONTH"] = pd.Categorical(monthly_fte["MONTH"], categories=month_order, ordered=True)
        monthly_fte = monthly_fte.sort_values("MONTH")
        fig_trend = px.line(monthly_fte, x="MONTH", y="FTE", markers=True, title=f"Trend FTE Mensile - {selected_year}")
        st.plotly_chart(fig_trend, use_container_width=True)
    st.subheader("🔥 Heatmap Allocazione Mensile")
    if "USER" in df_year.columns:
        user_filter = st.multiselect("Filtra utenti", sorted([str(u) for u in pd.Series(df_year["USER"]).dropna().unique()]))
        if user_filter:
            df_filtered = df_year[df_year["USER"].isin(user_filter)]
        else:
            df_filtered = df_year
        df_filtered = pd.DataFrame(df_filtered)  # Forza DataFrame
        user_month_fte = df_filtered.groupby("USER")[month_cols].sum()
        if isinstance(user_month_fte, (pd.DataFrame, pd.Series)) and getattr(user_month_fte, 'shape', [0])[0] > 0:
            fig_heatmap = px.imshow(user_month_fte, aspect="auto", title=f"Heatmap FTE per Utente - {selected_year}", labels=dict(x="Mese", y="Utente", color="FTE"))
            st.plotly_chart(fig_heatmap, use_container_width=True)
        else:
            st.info("Nessun dato disponibile per la heatmap")

# =======================
# REPORT PER PROGETTO
# =======================
if report_type == "Report per Progetto":
    st.subheader("📁 Report per Progetto")
    progetti = sorted(list(pd.Series(df["PROJECT_DESCR"]).dropna().unique()))
    selected_project = st.selectbox("Seleziona progetto", progetti)
    df_proj = df[df["PROJECT_DESCR"] == selected_project]
    if isinstance(df_proj, np.ndarray):
        df_proj = pd.DataFrame(df_proj)
    if df_proj.shape[0] == 0:
        st.info("Nessun dato disponibile per il progetto selezionato.")
    else:
        st.markdown(f"**Cliente:** {str(pd.Series(df_proj['CLIENT']).iloc[0]) if 'CLIENT' in df_proj.columns else '-'}  ")
        st.markdown(f"**PM:** {str(pd.Series(df_proj['PM_SM']).iloc[0]) if 'PM_SM' in df_proj.columns else '-'}  ")
        st.markdown(f"**Stato:** {str(pd.Series(df_proj['STATUS']).iloc[0]) if 'STATUS' in df_proj.columns else '-'}  ")
        st.markdown(f"**Periodo:** {str(pd.Series(df_proj['START_DATE']).min())} → {str(pd.Series(df_proj['END_DATE']).max())}")
        utenti_coinvolti = list(pd.Series(df_proj['USER']).dropna().unique()) if 'USER' in df_proj.columns else []
        st.markdown(f"**Utenti coinvolti:** {', '.join(sorted([str(u) for u in utenti_coinvolti]))}")
        st.metric("FTE Totale", float(df_proj[month_cols].sum().sum()) if month_cols else 0)
        if month_cols:
            fte_trend = df_proj[month_cols].sum().reset_index()
            fte_trend.columns = ["Mese", "FTE"]
            fte_trend["Mese"] = pd.Categorical(fte_trend["Mese"], categories=month_cols, ordered=True)
            fte_trend = fte_trend.sort_values("Mese")
            fig = px.bar(fte_trend, x="Mese", y="FTE", title="Allocazione FTE per mese")
            st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df_proj[[c for c in ["USER","JOB","PLANNED_FTE","ACTUAL_FTE","STATUS","PROGRESS_%"] if c in df_proj.columns] + month_cols])

# =======================
# REPORT PER UTENTE
# =======================
if report_type == "Report per Utente":
    st.subheader("👤 Report per Utente")
    utenti = sorted(list(pd.Series(df["USER"]).dropna().unique()))
    selected_user = st.selectbox("Seleziona utente", utenti)
    df_user = df[df["USER"] == selected_user]
    if isinstance(df_user, np.ndarray):
        df_user = pd.DataFrame(df_user)
    if df_user.shape[0] == 0:
        st.info("Nessun dato disponibile per l'utente selezionato.")
    else:
        st.markdown(f"**Job:** {str(pd.Series(df_user['JOB']).iloc[0]) if 'JOB' in df_user.columns else '-'}  ")
        progetti_assegnati = list(pd.Series(df_user['PROJECT_DESCR']).dropna().unique()) if 'PROJECT_DESCR' in df_user.columns else []
        st.markdown(f"**Progetti assegnati:** {', '.join(sorted([str(p) for p in progetti_assegnati]))}")
        clienti = list(pd.Series(df_user['CLIENT']).dropna().unique()) if 'CLIENT' in df_user.columns else []
        st.markdown(f"**Clienti:** {', '.join(sorted([str(c) for c in clienti]))}")
        st.markdown(f"**Periodo attività:** {str(pd.Series(df_user['START_DATE']).min())} → {str(pd.Series(df_user['END_DATE']).max())}")
        st.metric("FTE Totale", float(df_user[month_cols].sum().sum()) if month_cols else 0)
        if "PROJECT_DESCR" in df_user.columns and month_cols:
            fte_proj = df_user.groupby("PROJECT_DESCR")[month_cols].sum().sum(axis=1).reset_index()
            fte_proj.columns = ["Progetto", "FTE"]
            fig = px.bar(fte_proj, x="Progetto", y="FTE", title="FTE per Progetto")
            st.plotly_chart(fig, use_container_width=True)
        if month_cols:
            fte_trend = df_user[month_cols].sum().reset_index()
            fte_trend.columns = ["Mese", "FTE"]
            fte_trend["Mese"] = pd.Categorical(fte_trend["Mese"], categories=month_cols, ordered=True)
            fte_trend = fte_trend.sort_values("Mese")
            fig = px.line(fte_trend, x="Mese", y="FTE", markers=True, title="Trend FTE Mensile")
            st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df_user[[c for c in ["PROJECT_DESCR","CLIENT","PM_SM","PLANNED_FTE","ACTUAL_FTE","STATUS","PROGRESS_%"] if c in df_user.columns] + month_cols])

# =======================
# REPORT PER PM
# =======================
if report_type == "Report per PM":
    st.subheader("👨‍💼 Report per Project Manager")
    pms = sorted(list(pd.Series(df["PM_SM"]).dropna().unique()))
    selected_pm = st.selectbox("Seleziona PM", pms)
    df_pm = df[df["PM_SM"] == selected_pm]
    if isinstance(df_pm, np.ndarray):
        df_pm = pd.DataFrame(df_pm)
    if df_pm.shape[0] == 0:
        st.info("Nessun dato disponibile per il PM selezionato.")
    else:
        progetti_gestiti = list(pd.Series(df_pm['PROJECT_DESCR']).dropna().unique()) if 'PROJECT_DESCR' in df_pm.columns else []
        st.markdown(f"**Progetti gestiti:** {', '.join(sorted([str(p) for p in progetti_gestiti]))}")
        clienti = list(pd.Series(df_pm['CLIENT']).dropna().unique()) if 'CLIENT' in df_pm.columns else []
        st.markdown(f"**Clienti:** {', '.join(sorted([str(c) for c in clienti]))}")
        st.metric("FTE Totale gestito", float(df_pm[month_cols].sum().sum()) if month_cols else 0)
        if "PROJECT_DESCR" in df_pm.columns and month_cols:
            fte_proj = df_pm.groupby("PROJECT_DESCR")[month_cols].sum().sum(axis=1).reset_index()
            fte_proj.columns = ["Progetto", "FTE"]
            fig = px.bar(fte_proj, x="Progetto", y="FTE", title="FTE per Progetto")
            st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df_pm[[c for c in ["USER","PROJECT_DESCR","CLIENT","PLANNED_FTE","ACTUAL_FTE","STATUS","PROGRESS_%"] if c in df_pm.columns] + month_cols])

# =======================
# REPORT PER CLIENTE
# =======================
if report_type == "Report per Cliente":
    st.subheader("🏢 Report per Cliente")
    clienti = sorted(list(pd.Series(df["CLIENT"]).dropna().unique()))
    selected_client = st.selectbox("Seleziona cliente", clienti)
    df_client = df[df["CLIENT"] == selected_client]
    if isinstance(df_client, np.ndarray):
        df_client = pd.DataFrame(df_client)
    if df_client.shape[0] == 0:
        st.info("Nessun dato disponibile per il cliente selezionato.")
    else:
        progetti = list(pd.Series(df_client['PROJECT_DESCR']).dropna().unique()) if 'PROJECT_DESCR' in df_client.columns else []
        st.markdown(f"**Progetti:** {', '.join(sorted([str(p) for p in progetti]))}")
        pms = list(pd.Series(df_client['PM_SM']).dropna().unique()) if 'PM_SM' in df_client.columns else []
        st.markdown(f"**PM coinvolti:** {', '.join(sorted([str(pm) for pm in pms]))}")
        st.metric("FTE Totale", float(df_client[month_cols].sum().sum()) if month_cols else 0)
        if "PROJECT_DESCR" in df_client.columns and month_cols:
            fte_proj = df_client.groupby("PROJECT_DESCR")[month_cols].sum().sum(axis=1).reset_index()
            fte_proj.columns = ["Progetto", "FTE"]
            fig = px.bar(fte_proj, x="Progetto", y="FTE", title="FTE per Progetto")
            st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df_client[[c for c in ["USER","PROJECT_DESCR","PM_SM","PLANNED_FTE","ACTUAL_FTE","STATUS","PROGRESS_%"] if c in df_client.columns] + month_cols]) 