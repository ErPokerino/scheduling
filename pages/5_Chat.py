import streamlit as st
import os
import pandas as pd
from google import genai
from dotenv import load_dotenv
from src.data_access import load_scheduling
import difflib
import base64
from PIL import Image
import io


# Carica variabili da .env
load_dotenv()

st.set_page_config(page_title="Chat", page_icon="💬", layout="wide")

st.title("💬 Chat Assistant")

st.caption("LLM integration to ask natural-language questions about your schedules and analyze images.")

# Istruzioni per l'uso
with st.expander("ℹ️ Come usare la chat", expanded=False):
    st.markdown("""
    **✍️ Input Testuale:**
    - Scrivi direttamente nella casella di testo
    - Supporta domande complesse e multi-riga
    
    **📷 Analisi Immagini:**
    - Carica immagini nella sezione superiore
    - Chiedi domande sulle immagini caricate
    - Il bot analizzerà automaticamente il contenuto
    
    **💡 Suggerimenti:**
    - "Dammi info su [nome utente]"
    - "Quali progetti sono in stato [stato]?"
    - "Quanti FTE sono allocati a [mese]?"
    - "Chi lavora per il cliente [nome cliente]?"
    - "Mostrami i progetti completati"
    - "Qual è il progetto con più FTE?"
    """)

# Store chat messages in session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Store uploaded images in session state
if 'uploaded_images' not in st.session_state:
    st.session_state.uploaded_images = []

# Configura API key
API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

# Crea client Gemini
client = None
if API_KEY:
    client = genai.Client(api_key=API_KEY)
else:
    st.warning("⚠️ Imposta la variabile d'ambiente GOOGLE_API_KEY per utilizzare il chatbot.")

# Nome del chatbot
BOT_NAME = "Schedulo"
BOT_DESCRIPTION = "Sono Schedulo, il tuo assistente AI per la pianificazione, l'analisi e la gestione dei progetti e delle risorse. Posso rispondere a domande sui dati di scheduling, generare report, analizzare immagini e aiutarti a ottimizzare il lavoro del team."

def normalize_string(s):
    import re
    return re.sub(r'[^a-z0-9]', '', s.lower())

def get_table_structure():
    """Ottiene la struttura della tabella Scheduling per il contesto."""
    try:
        df = load_scheduling()
        structure_info = f"""
STRUTTURA TABELLA SCHEDULING:
- Colonne totali: {len(df.columns)}
- Righe totali: {len(df)}
- Colonne principali:
"""
        
        # Categorizza le colonne
        project_cols = ["PROJECT_DESCR", "CLIENT", "PM_SM", "SOW_ID", "JIRA_KEY"]
        classification_cols = ["ITEM_TYPE", "DELIVERY_TYPE", "WORKSTREAM", "PROJECT_STREAM", "AREA_CC"]
        timeline_cols = ["START_DATE", "END_DATE", "YEAR", "YEAR_OF_COMPETENCE"]
        resource_cols = ["USER", "JOB", "PLANNED_FTE", "ACTUAL_FTE", "STATUS", "PROGRESS_%"]
        
        # Colonne mese
        month_prefixes = ["gen","feb","mar","apr","mag","giu","lug","ago","set","ott","nov","dic"]
        month_cols = [c for c in df.columns if c[:3].lower() in month_prefixes and not c.lower().endswith("1")]
        
        structure_info += f"""
  • Informazioni Progetto: {', '.join([col for col in project_cols if col in df.columns])}
  • Classificazione: {', '.join([col for col in classification_cols if col in df.columns])}
  • Timeline: {', '.join([col for col in timeline_cols if col in df.columns])}
  • Gestione Risorse: {', '.join([col for col in resource_cols if col in df.columns])}
  • Allocazioni Mensili: {', '.join(month_cols)}
"""
        
        # Aggiungi esempi di valori per colonne importanti
        structure_info += "\nESEMPI DI VALORI:\n"
        
        if "STATUS" in df.columns:
            statuses = df["STATUS"].dropna().unique()[:5]
            structure_info += f"  • STATUS: {', '.join(statuses)}\n"
        
        if "ITEM_TYPE" in df.columns:
            item_types = df["ITEM_TYPE"].dropna().unique()[:5]
            structure_info += f"  • ITEM_TYPE: {', '.join(item_types)}\n"
        
        if "USER" in df.columns:
            users = df["USER"].dropna().unique()[:5]
            structure_info += f"  • USER: {', '.join(users)}\n"
        
        if "CLIENT" in df.columns:
            clients = df["CLIENT"].dropna().unique()[:5]
            structure_info += f"  • CLIENT: {', '.join(clients)}\n"
        
        return structure_info
    except Exception as e:
        return f"Errore nel caricamento della struttura: {e}"

def normalize(s):
    import unicodedata, re
    s = str(s).lower().strip()
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r'[^a-z0-9 ]', '', s)
    return s

def query_scheduling_data(query_description: str) -> str:
    import pandas as pd
    import re
    import unicodedata

    def normalize(s):
        s = str(s).lower().strip()
        s = unicodedata.normalize('NFKD', s)
        s = ''.join(c for c in s if not unicodedata.combining(c))
        s = re.sub(r'[^a-z0-9 ]', '', s)
        return s

    try:
        df = load_scheduling()
        user_col = "USER" if "USER" in df.columns else "user"
        if user_col not in df.columns:
            return "Nessuna colonna USER trovata nei dati."
        query_norm = normalize(query_description)
        df["USER_NORM"] = df[user_col].apply(normalize)
        user_rows = df[df["USER_NORM"].apply(lambda x: query_norm in x or x in query_norm)]
        if not user_rows.empty:
            found_user = user_rows.iloc[0][user_col]
            # Forza Series per .dropna() e .unique()
            def safe_unique(col):
                return pd.Series(col).dropna().astype(str).unique().tolist()
            projects = safe_unique(user_rows["PROJECT_DESCR"]) if "PROJECT_DESCR" in user_rows.columns else []
            pm_list = safe_unique(user_rows["PM_SM"]) if "PM_SM" in user_rows.columns else []
            client_list = safe_unique(user_rows["CLIENT"]) if "CLIENT" in user_rows.columns else []
            month_prefixes = ["gen","feb","mar","apr","mag","giu","lug","ago","set","ott","nov","dic"]
            month_cols = [c for c in df.columns if c[:3].lower() in month_prefixes and not c.lower().endswith("1")]
            fte_per_month = user_rows[month_cols].sum().to_dict() if month_cols else {}
            total_fte = sum(fte_per_month.values()) if fte_per_month else 0
            # Gestione robusta periodo attività
            period = ""
            if "START_DATE" in user_rows.columns and "END_DATE" in user_rows.columns:
                try:
                    start_dates = pd.to_datetime(user_rows["START_DATE"], errors="coerce")
                    end_dates = pd.to_datetime(user_rows["END_DATE"], errors="coerce")
                    if hasattr(start_dates, 'min') and hasattr(end_dates, 'max'):
                        start_min = start_dates.min()
                        end_max = end_dates.max()
                        if isinstance(start_min, pd.Timestamp) and isinstance(end_max, pd.Timestamp) and pd.notna(start_min) and pd.notna(end_max):
                            period = f"{start_min.strftime('%Y-%m-%d')} → {end_max.strftime('%Y-%m-%d')}"
                except Exception:
                    period = ""
            return (
                f"Utente: {found_user}\n"
                f"- Progetti: {', '.join(projects) if projects else 'Nessuno'}\n"
                f"- PM: {', '.join(pm_list) if pm_list else 'Nessuno'}\n"
                f"- Clienti: {', '.join(client_list) if client_list else 'Nessuno'}\n"
                f"- FTE totale: {total_fte}\n"
                f"- FTE per mese: {', '.join([f'{k}={v}' for k,v in fte_per_month.items()]) if fte_per_month else 'Nessuno'}\n"
                f"- Periodo: {period if period else 'N/A'}\n"
            )
        else:
            users_list = pd.Series(df[user_col]).dropna().astype(str).unique().tolist()
            return "Utente non trovato. Utenti disponibili: " + ", ".join(users_list[:10])
    except Exception as e:
        return f"Errore nell'esecuzione della query: {e}"

def encode_image_to_base64(image_bytes):
    """Converte un'immagine in base64 per l'invio a Gemini."""
    return base64.b64encode(image_bytes).decode('utf-8')





# =======================
# PROMPT PER ESTRAZIONE DATI (PRIMA CHIAMATA LLM)
# =======================
EXTRACTION_PROMPT = (
    "Sei un assistente AI che analizza domande e genera comandi Pandas per estrarre dati da un DataFrame.\n"
    "Il DataFrame contiene dati di scheduling progetti con queste colonne:\n"
    "- PROJECT_DESCR: Nome del progetto\n"
    "- USER: Nome della risorsa/utente\n"
    "- CLIENT: Cliente\n"
    "- PM_SM: Project Manager/Scrum Master\n"
    "- ITEM_TYPE: Tipologia attività\n"
    "- DELIVERY_TYPE: Tipo delivery\n"
    "- WORKSTREAM: Flusso di lavoro\n"
    "- START_DATE, END_DATE: Date inizio/fine progetto\n"
    "- PLANNED_FTE, ACTUAL_FTE: FTE pianificato/effettivo\n"
    "- STATUS: Stato progetto\n"
    "- PROGRESS_%: Avanzamento %\n"
    "- YEAR: Anno\n"
    "- gen, feb, mar, ..., dic: FTE allocato per ciascun mese\n"
    "\n"
    "ISTRUZIONI:\n"
    "1. Analizza la domanda dell'utente e le immagini fornite (se presenti).\n"
    "2. Se per rispondere servono dati dal DataFrame, genera comandi Pandas per estrarre i dati rilevanti.\n"
    "3. Se NON servono dati dal DataFrame, rispondi: 'Non è necessaria alcuna estrazione dati.'\n"
    "4. Restituisci SOLO i comandi Pandas/Python necessari, senza spiegazioni.\n"
    "\n"
    "ESEMPI:\n"
    "Domanda: 'Dammi info su M. Gomitoni'\n"
    "Output:\n"
    "user_rows = df[df['USER'] == 'M. Gomitoni']\n"
    "result = {\n"
    "  'progetti': user_rows['PROJECT_DESCR'].unique().tolist(),\n"
    "  'pm': user_rows['PM_SM'].unique().tolist(),\n"
    "  'clienti': user_rows['CLIENT'].unique().tolist(),\n"
    "  'fte_mensile': user_rows[['gen','feb','mar','apr','mag','giu','lug','ago','set','ott','nov','dic']].sum().to_dict()\n"
    "}\n"
    "\n"
    "Domanda: 'Come si usa la funzione di filtro?'\n"
    "Output: Non è necessaria alcuna estrazione dati.\n"
)

# =======================
# PROMPT PER RISPOSTA FINALE (SECONDA CHIAMATA LLM)
# =======================
SYSTEM_PROMPT = (
    "Sei un assistente AI che risponde a domande su una tabella di scheduling progetti e analizza immagini.\n"
    "La tabella contiene queste colonne principali:\n"
    "- PROJECT_DESCR: Nome del progetto (es: 'CRM Upgrade')\n"
    "- USER: Nome della risorsa/utente (es: 'M. Sorrentino')\n"
    "- CLIENT: Cliente (es: 'ACME S.p.A.')\n"
    "- PM_SM: Project Manager/Scrum Master (es: 'L. Mangili')\n"
    "- ITEM_TYPE: Tipologia attività (es: 'Development')\n"
    "- DELIVERY_TYPE: Tipo delivery (es: 'Internal')\n"
    "- WORKSTREAM: Flusso di lavoro (es: 'WS1')\n"
    "- YEAR_OF_COMPETENCE: Anno di competenza (es: '2024')\n"
    "- START_DATE, END_DATE: Date inizio/fine progetto (es: '2024-01-01')\n"
    "- SOW_ID, JIRA_KEY: Riferimenti contrattuali o ticket\n"
    "- PROJECT_STREAM, AREA_CC, JOB: Altri metadati\n"
    "- PLANNED_FTE, ACTUAL_FTE: FTE pianificato/effettivo (interi)\n"
    "- STATUS: Stato progetto (es: 'In Progress')\n"
    "- PROGRESS_%: Avanzamento %\n"
    "- YEAR: Anno (es: 2024)\n"
    "- gen, feb, mar, ..., dic: FTE allocato per ciascun mese (interi)\n"
    "\n"
    "Esempi di valori:\n"
    "- USER: 'A. Di Pietro', 'E. Storti', 'L. Mangili', 'C. Esposito', 'M. Sorrentino'\n"
    "- STATUS: 'Not Started', 'In Progress', 'Completed', 'On Hold', 'Cancelled'\n"
    "- ITEM_TYPE: 'Development', 'Analysis', 'Testing'\n"
    "- CLIENT: 'ACME', 'Beta', 'Client A'\n"
    "\n"
    "---\n"
    "Quando ricevi una domanda, segui queste regole:\n"
    "- Se sono presenti immagini, analizzale attentamente e descrivi cosa vedi.\n"
    "- Se le immagini contengono dati di scheduling, tabelle, grafici, cerca di estrarre informazioni utili.\n"
    "- Usa solo i dati forniti nel contesto.\n"
    "- Se la domanda riguarda un utente, mostra: progetti, FTE mensile, PM, clienti, periodo attività, totale FTE, ecc.\n"
    "- Se la domanda riguarda un progetto, mostra: utenti coinvolti, FTE allocato, periodo, stato, PM, cliente, ecc.\n"
    "- Se la domanda riguarda clienti, FTE, periodi, stati, aggrega e riassumi i dati pertinenti.\n"
    "- Se la risposta non è nei dati forniti, dillo esplicitamente.\n"
    "- Usa tabelle o elenchi puntati se utile.\n"
    "- Sii sintetico e preciso.\n"
    "\n"
    "---\n"
    "Esempi di domande e risposte:\n"
    "\n"
    "Domanda: 'Dammi info su M. Sorrentino'\n"
    "Risposta:\n"
    "- Progetti: CRM Upgrade, Data Migration\n"
    "- PM: L. Mangili, E. Storti\n"
    "- Clienti: ACME, Beta\n"
    "- FTE totale: 8\n"
    "- FTE per mese: gen=1, feb=1, mar=2, ...\n"
    "- Periodo: 2024-01-01 → 2024-06-30\n"
    "\n"
    "Domanda: 'Quali progetti sono in stato In Progress?'\n"
    "Risposta:\n"
    "- CRM Upgrade (PM: L. Mangili, Cliente: ACME)\n"
    "- Data Migration (PM: E. Storti, Cliente: Beta)\n"
    "\n"
    "Domanda: 'Quanti FTE sono allocati a marzo 2024?'\n"
    "Risposta:\n"
    "- FTE totale allocato a marzo 2024: 12\n"
    "\n"
    "Domanda: 'Chi lavora per il cliente ACME?'\n"
    "Risposta:\n"
    "- M. Sorrentino (Progetti: CRM Upgrade)\n"
    "- C. Esposito (Progetti: CRM Upgrade, Data Migration)\n"
    "\n"
    "---\n"
    "IMPORTANTE:\n"
    "Se la domanda richiede un riepilogo, aggrega i dati (es: somma FTE, conta progetti, ecc.).\n"
    "Se la domanda è generica, fornisci statistiche generali (es: numero utenti, progetti, clienti, ecc.).\n"
    "Se sono presenti immagini, analizzale e fornisci insights basati su quello che vedi.\n"
    "\n"
    "Rispondi sempre in italiano, in modo chiaro e strutturato."
)

def generate_llm_response(user_input: str, images: list = []) -> str:
    """
    Orchestrazione RAG a due step con supporto immagini:
    1. Prima chiamata LLM (Gemini Flash 2.5) con domanda utente, immagini e struttura dati
    2. Se il modello suggerisce query, il backend le esegue e passa i risultati come contesto a una seconda chiamata LLM
    3. Se non servono dati, la seconda chiamata LLM riceve solo domanda, immagini e struttura dati
    """
    # Risposta custom se l'utente chiede il nome del bot
    name_queries = [
        "come ti chiami", "qual è il tuo nome", "chi sei", "come si chiama il bot", "nome del bot", "come ti posso chiamare", "presentati", "parlami di te"
    ]
    if any(q in user_input.lower() for q in name_queries):
        return f"{BOT_DESCRIPTION} Il mio nome è **{BOT_NAME}**."

    if client is None:
        return "⚠️ API key mancante. Impossibile contattare il modello."

    try:
        # 1. Prepara il contenuto per la prima chiamata LLM (estrazione query)
        parts = []
        text_content = f"""
{EXTRACTION_PROMPT}

Domanda utente: {user_input}
Struttura dati:
{get_table_structure()}
"""
        parts.append(text_content)
        if images:
            for img_bytes, mime_type in images:
                parts.append({
                    "inline_data": {
                        "data": encode_image_to_base64(img_bytes),
                        "mime_type": mime_type
                    }
                })
        extraction_response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=parts,
        )
        extraction_code = extraction_response.text.strip() if (hasattr(extraction_response, 'text') and extraction_response.text is not None) else ""
        extracted_data = None
        if extraction_code and "Non è necessaria alcuna estrazione dati" not in extraction_code:
            try:
                local_vars = {'df': load_scheduling()}
                exec(extraction_code, {}, local_vars)
                if 'result' in local_vars:
                    extracted_data = local_vars['result']
                elif 'user_rows' in local_vars:
                    extracted_data = local_vars['user_rows']
                else:
                    extracted_data = {k: v for k, v in local_vars.items() if k not in ['df']}
            except Exception as e:
                extracted_data = query_scheduling_data(user_input)
        if extracted_data is None:
            extracted_data = query_scheduling_data(user_input)
        final_parts = []
        final_text = f"""
{SYSTEM_PROMPT}

Domanda utente: {user_input}
Struttura dati:
{get_table_structure()}
"""
        if extracted_data is not None:
            final_text += f"\nRisultati estratti dal DataFrame:\n{extracted_data}\n"
        final_parts.append(final_text)
        if images:
            for img_bytes, mime_type in images:
                final_parts.append({
                    "inline_data": {
                        "data": encode_image_to_base64(img_bytes),
                        "mime_type": mime_type
                    }
                })
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=final_parts,
        )
        if response and hasattr(response, 'text') and response.text:
            return response.text.strip()
        else:
            return "❌ Risposta vuota dal modello."
    except Exception as e:
        return f"❌ Errore durante la chiamata al modello: {e}"

# Funzione per pulire la conversazione
def clear_conversation():
    st.session_state.messages = []
    st.session_state.uploaded_images = []

# Upload immagini in alto
st.subheader("📷 Carica Immagini")
uploaded_files = st.file_uploader(
    "Seleziona immagini da analizzare",
    type=['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'],
    accept_multiple_files=True,
    help="Carica screenshot, grafici, tabelle o documenti da analizzare"
)

# Gestisci le immagini caricate
if uploaded_files:
    for uploaded_file in uploaded_files:
        if uploaded_file not in [img['file'] for img in st.session_state.uploaded_images]:
            image_bytes = uploaded_file.read()
            uploaded_file.seek(0)
            mime_type = f"image/{uploaded_file.name.split('.')[-1].lower()}"
            if mime_type == "image/jpg":
                mime_type = "image/jpeg"
            st.session_state.uploaded_images.append({
                'file': uploaded_file,
                'name': uploaded_file.name,
                'bytes': image_bytes,
                'mime_type': mime_type
            })

if st.session_state.uploaded_images:
    st.subheader("🖼️ Immagini Caricate")
    for i, img_data in enumerate(st.session_state.uploaded_images):
        col_img1, col_img2 = st.columns([3, 1])
        with col_img1:
            st.image(img_data['file'], caption=img_data['name'], width=150)
        with col_img2:
            if st.button("❌", key=f"remove_img_{i}", help="Rimuovi immagine"):
                st.session_state.uploaded_images.pop(i)
                st.rerun()

# Pulsante per pulire la conversazione
if st.button("🗑️ Clear Conversation", help="Clear all chat history and images"):
    clear_conversation()
    st.rerun()

# CHAT: messaggi e input nel body principale
st.subheader("💬 Chat")

# Render all messages
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.write(message['content'])
        if message['role'] == 'user' and 'images' in message and message['images']:
            st.write("📷 **Immagini analizzate:**")
            for i, (img_bytes, mime_type) in enumerate(message['images']):
                st.image(img_bytes, caption=f"Immagine {i+1}", width=200)

# Input per nuovo messaggio
prompt = st.chat_input("Ask me anything...", key="chat_input")
if prompt:
    current_images = []
    if st.session_state.uploaded_images:
        current_images = [(img['bytes'], img['mime_type']) for img in st.session_state.uploaded_images]
    st.session_state.messages.append({
        'role': 'user',
        'content': prompt,
        'images': current_images
    })
    assistant_reply = generate_llm_response(prompt, current_images)
    st.session_state.messages.append({'role': 'assistant', 'content': assistant_reply})
    st.rerun() 