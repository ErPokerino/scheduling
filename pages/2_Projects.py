import streamlit as st
import pandas as pd
from src.data_access import load_scheduling, save_scheduling, load_lovs

# ---------------------- PAGE LAYOUT ----------------------
st.title("📋 Manage Projects")

# Load data and ensure optional columns exist
df = load_scheduling()
for optional_col in ["PM", "CLIENT", "ITEM_TYPE", "DELIVERY_TYPE"]:
    if optional_col not in df.columns:
        df[optional_col] = None

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
            save_scheduling(new_df)
            st.success("Project added and visible in Schedule.")
        else:
            st.warning("Please enter at least one USER in the allocation table.")

# ---------------------- MODIFY / DELETE PROJECT ----------------------
st.header("Edit or delete existing project")
project_options = sorted(df["PROJECT_DESCR"].dropna().unique())
proj_selected = st.selectbox("Select project", project_options, index=None, placeholder="Select...")

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
    desired_cols = base_cols + month_cols
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

    edited_df = st.data_editor(
        proj_df[existing_cols],
        key="edit_proj",
        use_container_width=True,
        column_config=edit_col_conf,
    )

    save_col1, save_col2 = st.columns(2)
    with save_col1:
        if st.button("Save changes"):
            # Rimuovi vecchie righe e sostituisci con quelle modificate
            df_no_proj = df[df["PROJECT_DESCR"] != proj_selected]
            # Assicuriamo INT per mesi
            for mc in month_cols:
                edited_df[mc] = edited_df[mc].fillna(0).astype(int)
            updated_df = pd.concat([df_no_proj, edited_df], ignore_index=True)
            save_scheduling(updated_df)
            st.success("Project updated.")

    with save_col2:
        if st.button("Delete project", type="primary"):
            df_after = df[df["PROJECT_DESCR"] != proj_selected]
            save_scheduling(df_after)
            st.success(f"Project '{proj_selected}' deleted.")
