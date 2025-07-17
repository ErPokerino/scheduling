import streamlit as st
import pandas as pd
from src.data_access import load_scheduling, save_scheduling
from src.utils import filter_dataframe
import io
import os
from dotenv import load_dotenv

# Carica variabili d'ambiente
load_dotenv()

st.set_page_config(page_title="Scheduling", page_icon="📅", layout="wide")

# =======================
# GESTIONE DATI CONDIVISI
# =======================
# Inizializza session state per i dati condivisi
if 'shared_scheduling_data' not in st.session_state:
    st.session_state.shared_scheduling_data = None
    st.session_state.data_last_updated = None

# Importa funzioni di utilità per i dati condivisi
from src.utils import update_shared_data, show_data_update_info

# =======================
# SISTEMA DI LOGIN
# =======================
# Codice di accesso (in produzione dovrebbe essere in .env)
ACCESS_CODE = os.getenv("ACCESS_CODE", "warhammer")

# Inizializza session state per login
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Se non autenticato, mostra login
if not st.session_state.authenticated:
    st.title("🔐 Accesso Scheduling")
    st.markdown("---")
    
    # Centra il form di login
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### Inserisci il codice di accesso")
        
        # Campo password nascosto
        access_code = st.text_input(
            "Codice di accesso",
            type="password",
            placeholder="Inserisci il codice...",
            help="Contatta l'amministratore per ottenere il codice di accesso"
        )
        
        if st.button("🔓 Accedi", type="primary", use_container_width=True):
            if access_code == ACCESS_CODE:
                st.session_state.authenticated = True
                st.success("✅ Accesso autorizzato!")
                st.rerun()
            else:
                st.error("❌ Codice di accesso non valido!")
        
        # Informazioni aggiuntive
        st.markdown("---")
        st.info("💡 **Informazioni:** Questa applicazione richiede un codice di accesso per garantire la sicurezza dei dati di scheduling.")
        
        # Blocca l'esecuzione del resto dell'app
        st.stop()

# =======================
# CONTENUTO PRINCIPALE (solo se autenticato)
# =======================
st.title("📅 Scheduling – Resource Planning")

# Caricamento dati di schedulazione
df = load_scheduling()

# Aggiorna i dati condivisi se non sono ancora stati impostati
if st.session_state.shared_scheduling_data is None:
    update_shared_data(df)

# =======================
# IMPORT/EXPORT DATI
# =======================
st.header("📁 Import/Export Dati")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📤 Esporta Dati")
    # Opzioni di export
    export_format = st.selectbox("Formato di esportazione", ["Excel (.xlsx)", "CSV (.csv)"])
    
    if st.button("💾 Scarica Dati Correnti"):
        if export_format == "Excel (.xlsx)":
            # Export come Excel
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Scheduling', index=False)
            buffer.seek(0)
            st.download_button(
                label="📥 Scarica Excel",
                data=buffer.getvalue(),
                file_name=f"scheduling_export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            # Export come CSV
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Scarica CSV",
                data=csv,
                file_name=f"scheduling_export_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

with col2:
    st.subheader("📥 Importa Dati")
    uploaded_file = st.file_uploader(
        "Carica file Excel o CSV",
        type=['xlsx', 'csv'],
        help="Il file deve contenere le stesse colonne del dataset corrente"
    )
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.xlsx'):
                new_df = pd.read_excel(uploaded_file)
            else:
                new_df = pd.read_csv(uploaded_file)
            
            st.success(f"✅ File caricato con successo! Righe: {len(new_df)}")
            
            # Mostra preview dei dati
            with st.expander("👀 Anteprima dati caricati"):
                st.dataframe(new_df.head(), use_container_width=True)
            
            # Opzioni di import
            import_mode = st.radio(
                "Modalità di import",
                ["Sostituisci tutti i dati", "Aggiungi ai dati esistenti"],
                help="Sostituisci: cancella tutto e usa i nuovi dati. Aggiungi: mantieni i dati esistenti e aggiungi i nuovi."
            )
            
            if st.button("🔄 Applica Import", type="primary"):
                if import_mode == "Sostituisci tutti i dati":
                    save_scheduling(new_df)
                    # Aggiorna i dati condivisi
                    update_shared_data(new_df)
                    st.success("✅ Dati sostituiti con successo e resi disponibili in tutte le sezioni!")
                    st.info("🔄 I dati sono ora accessibili in Analytics e Chat. Ricarica le altre pagine per vedere i nuovi dati.")
                    st.rerun()
                else:
                    # Aggiungi ai dati esistenti
                    combined_df = pd.concat([df, new_df], ignore_index=True)
                    save_scheduling(combined_df)
                    # Aggiorna i dati condivisi
                    update_shared_data(combined_df)
                    st.success("✅ Dati aggiunti con successo e resi disponibili in tutte le sezioni!")
                    st.info("🔄 I dati sono ora accessibili in Analytics e Chat. Ricarica le altre pagine per vedere i nuovi dati.")
                    st.rerun()
                    
        except Exception as e:
            st.error(f"❌ Errore nel caricamento del file: {str(e)}")

# Mostra informazioni sui dati condivisi
show_data_update_info()

# Pulsante logout
col1, col2, col3 = st.columns([2, 1, 1])
with col3:
    if st.button("🚪 Logout", type="secondary"):
        st.session_state.authenticated = False
        st.rerun()

st.markdown("---")

# Identifichiamo colonne mese
month_prefixes = ["gen","feb","mar","apr","mag","giu","lug","ago","set","ott","nov","dic"]
month_cols = [c for c in df.columns if c[:3].lower() in month_prefixes]

# Filtriamo solo su colonne non-mese
non_month_df = df.drop(columns=month_cols, errors="ignore")
filtered_non_month = filter_dataframe(non_month_df)
filtered_full = df.loc[filtered_non_month.index]

st.dataframe(filtered_full, use_container_width=True)
