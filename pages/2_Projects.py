import streamlit as st
import pandas as pd
from src.data_access import load_scheduling, save_scheduling, load_lovs
from streamlit_tags import st_tags

# ---------------------- PAGE LAYOUT ----------------------
st.title("📋 Manage Projects")

# Load data and ensure optional columns exist
df = load_scheduling()
# Ensure text-based metadata columns exist and are stored as strings/object dtype
for optional_col in ["PM", "CLIENT", "ITEM_TYPE", "DELIVERY_TYPE"]:
    if optional_col not in df.columns:
        # create empty string column so dtype becomes 'object'
        df[optional_col] = ""
    else:
        # Cast to string to guarantee compatibility with TextColumn in data_editor
        df[optional_col] = df[optional_col].fillna("").astype(str)

# Ensure YEAR_OF_COMPETENCE is consistently string type to avoid Arrow conversion issues
if "YEAR_OF_COMPETENCE" in df.columns:
    df["YEAR_OF_COMPETENCE"] = df["YEAR_OF_COMPETENCE"].fillna("").astype(str)
else:
    df["YEAR_OF_COMPETENCE"] = ""

# Ensure other text columns are also strings
text_columns = ["PM_SM", "WORKSTREAM", "SOW_ID", "JIRA_KEY", "PROJECT_STREAM", "AREA_CC", "JOB", "STATUS"]
for col in text_columns:
    if col in df.columns:
        df[col] = df[col].fillna("").astype(str)
    else:
        df[col] = ""

# Ensure numeric columns are properly typed
numeric_columns = ["YEAR", "PROGRESS_%", "PLANNED_FTE", "ACTUAL_FTE"]
for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    else:
        df[col] = 0

# Helper per colonne mese
month_prefixes = ["gen","feb","mar","apr","mag","giu","lug","ago","set","ott","nov","dic"]
# Escludiamo colonne derivate che terminano con '1'
month_cols = [c for c in df.columns if c[:3].lower() in month_prefixes and not c.lower().endswith("1")]

# Suggerimenti per USER basati su dataset esistente
user_suggestions = sorted(df["USER"].dropna().unique())

# ---------------------- ADD PROJECT ----------------------
st.header("Add a new project")

with st.form(key="add_project", clear_on_submit=True):
    # Project metadata section
    st.markdown("### Project Information")
    
    # First row - Project description, Client, PM/SM
    meta_cols1 = st.columns(3)
    with meta_cols1[0]:
        project_descr = st.text_input("PROJECT_DESCR", key="project_descr_input")
    with meta_cols1[1]:
        client = st.text_input("CLIENT", key="client_input")
    with meta_cols1[2]:
        pm_sm = st.text_input("PM_SM", key="pm_sm_input")

    # Second row - Item type, Delivery type, Workstream
    meta_cols2 = st.columns(3)
    with meta_cols2[0]:
        item_type = st.text_input("ITEM_TYPE", key="item_type_input")
    with meta_cols2[1]:
        delivery_type = st.text_input("DELIVERY_TYPE", key="delivery_type_input")
    with meta_cols2[2]:
        workstream = st.text_input("WORKSTREAM", key="workstream_input")

    # Third row - SOW ID, JIRA Key, Project Stream
    meta_cols3 = st.columns(3)
    with meta_cols3[0]:
        sow_id = st.text_input("SOW_ID", key="sow_id_input")
    with meta_cols3[1]:
        jira_key = st.text_input("JIRA_KEY", key="jira_key_input")
    with meta_cols3[2]:
        project_stream = st.text_input("PROJECT_STREAM", key="project_stream_input")

    # Fourth row - Area CC, Job, Year of Competence
    meta_cols4 = st.columns(3)
    with meta_cols4[0]:
        area_cc = st.text_input("AREA_CC", key="area_cc_input")
    with meta_cols4[1]:
        job = st.text_input("JOB", key="job_input")
    with meta_cols4[2]:
        year_of_competence = st.number_input("YEAR_OF_COMPETENCE", min_value=2020, max_value=2035, value=2024, step=1, key="year_of_competence_input")

    # Fifth row - Dates and Year
    date_cols = st.columns(3)
    start_date = date_cols[0].date_input("START_DATE")
    end_date = date_cols[1].date_input("END_DATE")
    year = date_cols[2].number_input("YEAR", min_value=2020, max_value=2035, value=2024, step=1, key="year_input")

    # Sixth row - FTE and Status
    fte_cols = st.columns(3)
    planned_fte = fte_cols[0].number_input("PLANNED_FTE", min_value=0, step=1, value=0)
    actual_fte = fte_cols[1].number_input("ACTUAL_FTE", min_value=0, step=1, value=0)
    progress_pct = fte_cols[2].number_input("PROGRESS_%", min_value=0, max_value=100, value=0, step=1)

    # STATUS: selectbox con opzione Altro...
    status_suggestions = sorted(df["STATUS"].dropna().unique()) if "STATUS" in df.columns else []
    status_options = status_suggestions + ["Altro..."]
    status_sel = st.selectbox("STATUS", [""] + status_options, key="status_selectbox")
    status = status_sel
    if status_sel == "Altro...":
        status = st.text_input("Nuovo STATUS", key="status_input")

    st.markdown("### Resource allocation (FTE per month)")
    # Editor per inserire USER e FTE sui mesi
    alloc_template = pd.DataFrame(columns=pd.Index(["USER"] + month_cols))

    # Configurazioni delle colonne per suggerimenti e interi
    from streamlit import column_config as cc

    col_conf = {
        "USER": cc.SelectboxColumn("USER", options=user_suggestions, required=True),
    }
    for mc in month_cols:
        col_conf[mc] = cc.NumberColumn(mc.upper(), min_value=0, step=1, required=False)

    allocations = st.data_editor(
        alloc_template,
        num_rows="dynamic",
        use_container_width=True,
        key="alloc_editor",
        column_config=col_conf,
    )

    submitted = st.form_submit_button("Add project")

if submitted:
    # Permetti inserimento anche con info parziali: basta PROJECT_DESCR
    project_descr = project_descr.strip() if isinstance(project_descr, str) else ""
    alloc_rows = allocations.dropna(how='all')  # prendi tutte le righe non completamente vuote
    new_rows = []
    if not project_descr:
        st.error("PROJECT_DESCR is required.")
    else:
        # Se almeno un USER è inserito, aggiungi una riga per ogni USER
        valid_alloc = alloc_rows[alloc_rows["USER"].astype(str).str.strip() != ""] if "USER" in alloc_rows.columns else pd.DataFrame()
        if not valid_alloc.empty:
            for _, alloc_row in valid_alloc.iterrows():
                base_record = {
                    "PROJECT_DESCR": project_descr,
                    "CLIENT": client,
                    "PM_SM": pm_sm,
                    "ITEM_TYPE": item_type,
                    "DELIVERY_TYPE": delivery_type,
                    "WORKSTREAM": workstream,
                    "YEAR_OF_COMPETENCE": str(year_of_competence) if year_of_competence else "",
                    "START_DATE": pd.to_datetime(start_date),
                    "END_DATE": pd.to_datetime(end_date),
                    "SOW_ID": sow_id,
                    "JIRA_KEY": jira_key,
                    "PROJECT_STREAM": project_stream,
                    "AREA_CC": area_cc,
                    "JOB": job,
                    "PLANNED_FTE": int(planned_fte),
                    "ACTUAL_FTE": int(actual_fte),
                    "STATUS": status,
                    "PROGRESS_%": progress_pct,
                    "YEAR": year,
                    "USER": alloc_row["USER"],
                }
                for mc in month_cols:
                    base_record[mc] = int(alloc_row.get(mc, 0) or 0)
                new_rows.append(base_record)
        else:
            # Nessun USER: aggiungi una riga con USER vuoto e warning
            base_record = {
                "PROJECT_DESCR": project_descr,
                "CLIENT": client,
                "PM_SM": pm_sm,
                "ITEM_TYPE": item_type,
                "DELIVERY_TYPE": delivery_type,
                "WORKSTREAM": workstream,
                "YEAR_OF_COMPETENCE": str(year_of_competence) if year_of_competence else "",
                "START_DATE": pd.to_datetime(start_date),
                "END_DATE": pd.to_datetime(end_date),
                "SOW_ID": sow_id,
                "JIRA_KEY": jira_key,
                "PROJECT_STREAM": project_stream,
                "AREA_CC": area_cc,
                "JOB": job,
                "PLANNED_FTE": int(planned_fte),
                "ACTUAL_FTE": int(actual_fte),
                "STATUS": status,
                "PROGRESS_%": progress_pct,
                "YEAR": year,
                "USER": "",
            }
            for mc in month_cols:
                base_record[mc] = 0
            new_rows.append(base_record)
            st.warning("Nessun USER inserito: il progetto sarà aggiunto senza allocazione risorse. Potrai modificarlo subito dopo.")
        if new_rows:
            new_df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
            save_scheduling(new_df)
            st.success("Project added and visible in Schedule. Puoi modificarlo subito sotto.")

# ---------------------- MODIFY / DELETE PROJECT ----------------------
st.header("Edit or delete existing project")
project_options = sorted(df["PROJECT_DESCR"].dropna().unique())
# Multiselect mostra la scelta come "tag" con X per rimuoverla
proj_selected_list = st.multiselect(
    "Select project (tag removable)",
    project_options,
    default=[],
    key="select_project_tag",
)
# Consideriamo solo il primo elemento selezionato (uno alla volta)
proj_selected = proj_selected_list[0] if proj_selected_list else None

if proj_selected:
    proj_df = df[df["PROJECT_DESCR"] == proj_selected].copy()

    # Mostriamo editor per modificare allocazioni e metadati
    base_cols = [
        "PROJECT_DESCR",
        "USER",
        "CLIENT",
        "PM_SM",
        "ITEM_TYPE",
        "DELIVERY_TYPE",
        "WORKSTREAM",
        "YEAR_OF_COMPETENCE",
        "START_DATE",
        "END_DATE",
        "SOW_ID",
        "JIRA_KEY",
        "PROJECT_STREAM",
        "AREA_CC",
        "JOB",
        "PLANNED_FTE",
        "ACTUAL_FTE",
        "STATUS",
        "PROGRESS_%",
        "YEAR",
    ]

    # Ordine delle colonne nell'editor: DELETE a sinistra, poi meta, mesi
    desired_cols = ["DELETE"] + base_cols + month_cols

    # Se la colonna flag non esiste la creiamo
    if "DELETE" not in proj_df.columns:
        proj_df["DELETE"] = False
    # Assicuriamo dtype boolean
    if isinstance(proj_df["DELETE"], pd.Series):
        proj_df["DELETE"] = proj_df["DELETE"].fillna(False).astype(bool)
    else:
        proj_df["DELETE"] = False

    existing_cols = [c for c in desired_cols if c in proj_df.columns]

    edit_col_conf = {}
    # build column configs only for existing columns
    if "USER" in existing_cols:
        edit_col_conf["USER"] = cc.SelectboxColumn("USER", options=user_suggestions, required=True)
    if "CLIENT" in existing_cols:
        edit_col_conf["CLIENT"] = cc.TextColumn("CLIENT")
    if "PM_SM" in existing_cols:
        edit_col_conf["PM_SM"] = cc.TextColumn("PM_SM")
    if "ITEM_TYPE" in existing_cols:
        edit_col_conf["ITEM_TYPE"] = cc.TextColumn("ITEM_TYPE")
    if "DELIVERY_TYPE" in existing_cols:
        edit_col_conf["DELIVERY_TYPE"] = cc.TextColumn("DELIVERY_TYPE")
    if "WORKSTREAM" in existing_cols:
        edit_col_conf["WORKSTREAM"] = cc.TextColumn("WORKSTREAM")
    if "YEAR_OF_COMPETENCE" in existing_cols:
        edit_col_conf["YEAR_OF_COMPETENCE"] = cc.TextColumn("YEAR_OF_COMPETENCE")
    if "SOW_ID" in existing_cols:
        edit_col_conf["SOW_ID"] = cc.TextColumn("SOW_ID")
    if "JIRA_KEY" in existing_cols:
        edit_col_conf["JIRA_KEY"] = cc.TextColumn("JIRA_KEY")
    if "PROJECT_STREAM" in existing_cols:
        edit_col_conf["PROJECT_STREAM"] = cc.TextColumn("PROJECT_STREAM")
    if "AREA_CC" in existing_cols:
        edit_col_conf["AREA_CC"] = cc.TextColumn("AREA_CC")
    if "JOB" in existing_cols:
        edit_col_conf["JOB"] = cc.TextColumn("JOB")
    if "STATUS" in existing_cols:
        edit_col_conf["STATUS"] = cc.SelectboxColumn("STATUS", options=["Not Started", "In Progress", "Completed", "On Hold", "Cancelled"])
    if "PROGRESS_%" in existing_cols:
        edit_col_conf["PROGRESS_%"] = cc.NumberColumn("PROGRESS_%", min_value=0, max_value=100, step=1)
    if "YEAR" in existing_cols:
        edit_col_conf["YEAR"] = cc.NumberColumn("YEAR", min_value=2020, max_value=2030, step=1)
    for mc in month_cols:
        if mc in existing_cols:
            edit_col_conf[mc] = cc.NumberColumn(mc.upper(), min_value=0, step=1)

    # Colonne integer di riepilogo
    if "PLANNED_FTE" in existing_cols:
        edit_col_conf["PLANNED_FTE"] = cc.NumberColumn("PLANNED_FTE", min_value=0, step=1)
    if "ACTUAL_FTE" in existing_cols:
        edit_col_conf["ACTUAL_FTE"] = cc.NumberColumn("ACTUAL_FTE", min_value=0, step=1)

    # Colonna checkbox per eliminare singola riga
    if "DELETE" in existing_cols:
        edit_col_conf["DELETE"] = cc.CheckboxColumn("Del.")

    edited_df = st.data_editor(
        proj_df[existing_cols],
        key="edit_proj",
        use_container_width=True,
        column_config=edit_col_conf,
    )

    save_col1, save_col2 = st.columns(2)
    with save_col1:
        if st.button("Save changes"):
            # Righe da mantenere (non flaggate)
            if "DELETE" in edited_df.columns and isinstance(edited_df["DELETE"], pd.Series):
                edited_df["DELETE"] = edited_df["DELETE"].fillna(False).astype(bool)
                to_keep = edited_df[~edited_df["DELETE"]].copy()
            else:
                to_keep = edited_df.copy()

            df_no_proj = df[df["PROJECT_DESCR"] != proj_selected].copy()
            # Assicuriamo INT per mesi e colonne riepilogo
            for col_int in month_cols + ["YEAR", "PROGRESS_%", "PLANNED_FTE", "ACTUAL_FTE"]:
                if col_int in to_keep.columns:
                    to_keep[col_int] = pd.to_numeric(to_keep[col_int], errors="coerce").fillna(0).astype(int)
            if "YEAR_OF_COMPETENCE" in to_keep.columns:
                to_keep["YEAR_OF_COMPETENCE"] = to_keep["YEAR_OF_COMPETENCE"].astype(str)
            # Aggiungiamo/aggiorniamo YEAR basato su START_DATE
            if "START_DATE" in to_keep.columns:
                start_dates = pd.to_datetime(to_keep["START_DATE"], errors="coerce")
                to_keep["YEAR"] = start_dates.dt.year.fillna(2024).astype(int)
            if "YEAR" not in df_no_proj.columns and "START_DATE" in df_no_proj.columns:
                start_dates = pd.to_datetime(df_no_proj["START_DATE"], errors="coerce")
                df_no_proj["YEAR"] = start_dates.dt.year.fillna(2024).astype(int)

            # Rimuoviamo la colonna di servizio prima di salvare
            to_keep = to_keep.drop(columns=["DELETE"], errors="ignore")
            updated_df = pd.concat([df_no_proj.drop(columns=["DELETE"], errors="ignore"), to_keep], ignore_index=True)
            if not isinstance(updated_df, pd.DataFrame):
                updated_df = pd.DataFrame(updated_df)
            save_scheduling(updated_df)
            st.success("Project updated.")

            # Se non resta alcuna riga per il progetto, informare utente
            if to_keep.empty:
                st.info("Tutte le righe del progetto sono state eliminate. Il progetto non esisterà più nella schedule.")

    with save_col2:
        if st.button("Delete project", type="primary"):
            df_after = df[df["PROJECT_DESCR"] != proj_selected].copy()
            if not isinstance(df_after, pd.DataFrame):
                df_after = pd.DataFrame(df_after)
            save_scheduling(df_after)
            st.success(f"Project '{proj_selected}' deleted.")
