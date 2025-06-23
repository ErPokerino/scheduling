import streamlit as st
import pandas as pd
from src.data_access import load_scheduling, save_scheduling, load_lovs

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

# Helper per colonne mese
month_prefixes = ["gen","feb","mar","apr","mag","giu","lug","ago","set","ott","nov","dic"]
# Escludiamo colonne derivate che terminano con '1'
month_cols = [c for c in df.columns if c[:3].lower() in month_prefixes and not c.lower().endswith("1")]

# Suggerimenti per USER basati su dataset esistente
user_suggestions = sorted(df["USER"].dropna().unique())

# ---------------------- ADD PROJECT ----------------------
st.header("Add a new project")

with st.form(key="add_project", clear_on_submit=True):
    meta_cols = st.columns(3)

    # Existing suggestions
    proj_suggestions = sorted(df["PROJECT_DESCR"].dropna().unique())
    client_suggestions = sorted(df["CLIENT"].dropna().unique())
    pm_suggestions = sorted(df["PM"].dropna().unique())

    # --- Project description with option new ---
    sel_proj = meta_cols[0].selectbox(
        "Project description (select or create)",
        options=["<New project>"] + proj_suggestions,
        index=0,
    )
    if sel_proj == "<New project>":
        project_descr = meta_cols[0].text_input("New project description", key="new_proj_descr")
    else:
        project_descr = sel_proj

    # --- Client ---
    sel_client = meta_cols[1].selectbox(
        "Client (select or create)",
        options=["<New client>"] + client_suggestions,
        index=0,
    )
    if sel_client == "<New client>":
        client = meta_cols[1].text_input("New client", key="new_client")
    else:
        client = sel_client

    # --- PM ---
    sel_pm = meta_cols[2].selectbox(
        "Project Manager (PM)",
        options=["<New PM>"] + pm_suggestions,
        index=0,
    )
    if sel_pm == "<New PM>":
        pm = meta_cols[2].text_input("New PM", key="new_pm")
    else:
        pm = sel_pm

    item_type = st.selectbox("Item type", load_lovs()["ITEM_TYPE"].dropna().unique())
    delivery_type = st.selectbox("Delivery type", load_lovs()["DELIVERY_TYPE"].dropna().unique())

    date_cols = st.columns(2)
    start_date = date_cols[0].date_input("Start date")
    end_date = date_cols[1].date_input("End date")

    st.markdown("### Resource allocation (FTE per month)")
    # Editor per inserire USER e FTE sui mesi
    alloc_template = pd.DataFrame(columns=["USER"] + month_cols)

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
    if not project_descr:
        st.error("Project description is required.")
    else:
        new_rows = []
        # Costruiamo una riga per ogni user inserito
        for _, alloc_row in allocations.dropna(subset=["USER"]).iterrows():
            base_record = {col: None for col in df.columns}
            base_record.update({
                "PROJECT_DESCR": project_descr,
                "CLIENT": client,
                "PM": pm,
                "ITEM_TYPE": item_type,
                "DELIVERY_TYPE": delivery_type,
                "START_DATE": pd.to_datetime(start_date),
                "END_DATE": pd.to_datetime(end_date),
                "USER": alloc_row["USER"],
            })

            # Copia allocazioni mensili, converte a int (NaN -> 0)
            for mc in month_cols:
                val = alloc_row.get(mc, 0) or 0
                base_record[mc] = int(val)

            new_rows.append(base_record)

        if new_rows:
            new_df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
            # Aggiorna colonna YEAR in base a START_DATE se presente
            if "YEAR" not in new_df.columns:
                new_df["YEAR"] = pd.NA
            new_df.loc[new_df["YEAR"].isna(), "YEAR"] = pd.to_datetime(new_df.loc[new_df["YEAR"].isna(), "START_DATE"], errors="coerce").dt.year.astype("Int64")
            save_scheduling(new_df)
            st.success("Project added and visible in Schedule.")
        else:
            st.warning("Please enter at least one USER in the allocation table.")

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
        "PM",
        "ITEM_TYPE",
        "DELIVERY_TYPE",
        "START_DATE",
        "END_DATE",
    ]
    # Colonne numeriche di riepilogo FTE
    summary_cols = ["PLANNED_FTE", "ACTUAL_FTE"]

    # Ordine delle colonne nell'editor: DELETE a sinistra, poi meta, summary, mesi
    desired_cols = ["DELETE"] + base_cols + summary_cols + month_cols

    # Se la colonna flag non esiste la creiamo
    if "DELETE" not in proj_df.columns:
        proj_df["DELETE"] = False
    # Assicuriamo dtype boolean
    proj_df["DELETE"] = proj_df["DELETE"].fillna(False).astype(bool)

    existing_cols = [c for c in desired_cols if c in proj_df.columns]

    edit_col_conf = {}
    # build column configs only for existing columns
    if "USER" in existing_cols:
        edit_col_conf["USER"] = cc.SelectboxColumn("USER", options=user_suggestions, required=True)
    if "CLIENT" in existing_cols:
        edit_col_conf["CLIENT"] = cc.TextColumn("Client")
    if "PM" in existing_cols:
        edit_col_conf["PM"] = cc.TextColumn("PM")
    if "ITEM_TYPE" in existing_cols:
        edit_col_conf["ITEM_TYPE"] = cc.TextColumn("Item type")
    if "DELIVERY_TYPE" in existing_cols:
        edit_col_conf["DELIVERY_TYPE"] = cc.TextColumn("Delivery type")
    for mc in month_cols:
        if mc in existing_cols:
            edit_col_conf[mc] = cc.NumberColumn(mc.upper(), min_value=0, step=1)

    # Colonne integer di riepilogo
    if "PLANNED_FTE" in existing_cols:
        edit_col_conf["PLANNED_FTE"] = cc.NumberColumn("Planned FTE", min_value=0, step=1)
    if "ACTUAL_FTE" in existing_cols:
        edit_col_conf["ACTUAL_FTE"] = cc.NumberColumn("Actual FTE", min_value=0, step=1)

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
            edited_df["DELETE"] = edited_df["DELETE"].fillna(False).astype(bool)
            to_keep = edited_df[~edited_df["DELETE"]].copy()

            df_no_proj = df[df["PROJECT_DESCR"] != proj_selected]
            # Assicuriamo INT per mesi e colonne riepilogo
            for col_int in month_cols + ["PLANNED_FTE", "ACTUAL_FTE"]:
                if col_int in to_keep.columns:
                    to_keep[col_int] = to_keep[col_int].fillna(0).astype(int)
            # Aggiungiamo/aggiorniamo YEAR basato su START_DATE
            to_keep["YEAR"] = pd.to_datetime(to_keep["START_DATE"], errors="coerce").dt.year.astype("Int64")
            if "YEAR" not in df_no_proj.columns:
                df_no_proj["YEAR"] = pd.to_datetime(df_no_proj["START_DATE"], errors="coerce").dt.year.astype("Int64")

            # Rimuoviamo la colonna di servizio prima di salvare
            to_keep = to_keep.drop(columns=["DELETE"], errors="ignore")
            updated_df = pd.concat([df_no_proj.drop(columns=["DELETE"], errors="ignore"), to_keep], ignore_index=True)
            save_scheduling(updated_df)
            st.success("Project updated.")

            # Se non resta alcuna riga per il progetto, informare utente
            if to_keep.empty:
                st.info("Tutte le righe del progetto sono state eliminate. Il progetto non esisterà più nella schedule.")

    with save_col2:
        if st.button("Delete project", type="primary"):
            df_after = df[df["PROJECT_DESCR"] != proj_selected]
            save_scheduling(df_after)
            st.success(f"Project '{proj_selected}' deleted.")
