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

    column_map = {
        'status': ['status', 'stato', 'ongoing', 'in progress', 'completato', 'completed', 'on hold', 'cancellato', 'cancelled', 'chiusi', 'chiuso', 'conclusi', 'terminati', 'closed'],
        'client': ['client', 'cliente'],
        'pm_sm': ['pm', 'project manager', 'scrum master', 'pm_sm'],
        'user': ['user', 'utente', 'risorsa', 'persona', 'collaboratore'],
        'project_descr': ['progetto', 'project', 'project_descr', 'nome progetto', 'descrizione progetto'],
        'item_type': ['item_type', 'tipologia', 'tipo attività'],
        'delivery_type': ['delivery_type', 'tipo delivery'],
    }
    priority = ['status', 'client', 'pm_sm', 'user', 'project_descr', 'item_type', 'delivery_type']

    def make_table(rows):
        # Raggruppa per progetto e mostra solo una riga per PROJECT_DESCR
        header = "| Progetto | PM | Cliente |\n|---|---|---|"
        lines = []
        if 'PROJECT_DESCR' in rows.columns:
            grouped = rows.groupby('PROJECT_DESCR').first().reset_index()
            for _, row in grouped.iterrows():
                descr = str(row['PROJECT_DESCR']) if 'PROJECT_DESCR' in row else ''
                pm = str(row['PM_SM']) if 'PM_SM' in row else ''
                client = str(row['CLIENT']) if 'CLIENT' in row else ''
                lines.append(f"| {descr} | {pm} | {client} |")
        else:
            for _, row in rows.iterrows():
                descr = str(row['PROJECT_DESCR']) if 'PROJECT_DESCR' in row else ''
                pm = str(row['PM_SM']) if 'PM_SM' in row else ''
                client = str(row['CLIENT']) if 'CLIENT' in row else ''
                lines.append(f"| {descr} | {pm} | {client} |")
        return header + "\n" + "\n".join(lines)

    def make_bullet_list(items, title=None):
        out = f"{title}\n" if title else ""
        for item in items:
            out += f"- {item}\n"
        return out

    def list_to_table_or_bullets(lst):
        # Se la lista contiene tuple o dict, prova a fare una tabella
        if lst and (isinstance(lst[0], (tuple, list)) and len(lst[0]) >= 2):
            # Tabella generica
            header = "| " + " | ".join([f"Col{i+1}" for i in range(len(lst[0]))]) + " |\n"
            header += "|" + "---|" * len(lst[0])
            lines = ["| " + " | ".join(str(x) for x in row) + " |" for row in lst]
            return header + "\n" + "\n".join(lines)
        elif lst and isinstance(lst[0], dict):
            # Tabella con chiavi del dict
            keys = list(lst[0].keys())
            header = "| " + " | ".join(keys) + " |\n"
            header += "|" + "---|" * len(keys)
            lines = ["| " + " | ".join(str(row[k]) for k in keys) + " |" for row in lst]
            return header + "\n" + "\n".join(lines)
        else:
            return make_bullet_list(lst)

    try:
        df = load_scheduling()
        question = normalize(query_description)
        filter_col = None
        filter_value = None
        for col_key in priority:
            for synonym in column_map[col_key]:
                if synonym in question:
                    filter_col = col_key.upper() if col_key != 'project_descr' else 'PROJECT_DESCR'
                    match = re.search(synonym + r"[\s:]*([\w .-]+)", question)
                    if match:
                        filter_value = match.group(1).strip()
                    else:
                        filter_value = question.split()[-1]
                    break
            if filter_col:
                break
        if not filter_col:
            if 'ongoing' in question or 'on going' in question:
                filter_col = 'STATUS'
                filter_value = 'ON GOING'
            elif 'in progress' in question:
                filter_col = 'STATUS'
                filter_value = 'IN PROGRESS'
            elif 'completed' in question or 'completato' in question or 'chiusi' in question or 'chiuso' in question or 'conclusi' in question or 'terminati' in question or 'closed' in question:
                filter_col = 'STATUS'
                filter_value = 'CLOSED'
        if not filter_col:
            return ("Non ho capito su quale campo filtrare. Puoi chiedere per: status, cliente, project manager, utente, progetto, tipologia, delivery type. ")
        if filter_col not in df.columns:
            return f"La colonna '{filter_col}' non esiste nei dati. Colonne disponibili: {', '.join(df.columns)}"
        norm_col = df[filter_col].astype(str).apply(normalize)
        norm_value = normalize(filter_value)
        filtered = df[norm_col.str.contains(norm_value, na=False)]
        if not filtered.empty:
            if filter_col in ['STATUS', 'CLIENT', 'PM_SM', 'USER', 'PROJECT_DESCR']:
                return f"Progetti trovati per {filter_col} = '{filter_value}':\n" + make_table(filtered)
            else:
                return f"Risultati trovati:\n" + filtered.head(5).to_string(index=False)
        else:
            available = df[filter_col].dropna().unique().tolist()
            return f"Nessun risultato trovato per {filter_col} = '{filter_value}'. Valori disponibili: {', '.join(str(a) for a in available[:10])}"
    except Exception as e:
        # Fallback: se per errore viene generato un dict/list, convertilo in testo leggibile
        import traceback
        import sys
        exc_type, exc_value, exc_tb = sys.exc_info()
        if isinstance(e, dict):
            for k, v in e.items():
                if isinstance(v, list):
                    return list_to_table_or_bullets(v,)
            return str(e)
        elif isinstance(e, list):
            return list_to_table_or_bullets(e)
        # Se il messaggio di errore contiene una lista, estraila e formatta
        tb_str = traceback.format_exc()
        if '[' in str(e) and ']' in str(e):
            try:
                import ast
                lst = ast.literal_eval(str(e))
                if isinstance(lst, list):
                    return list_to_table_or_bullets(lst)
            except Exception:
                pass
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

# === INTENT CLASSIFICATION LLM ===
def classify_intent_with_llm(user_input):
    """
    Classifica l'intento della domanda come 'generica' (conversazione, help, spiegazione, onboarding, ecc.)
    oppure 'dati' (richiesta di consultazione, filtro, analisi, aggregazione dati di scheduling).
    Usa un prompt strutturato e ricco di contesto.
    """
    prompt = f"""
# Ruolo
Sei un classificatore di intenti per un assistente AI integrato in un'applicazione di scheduling e resource planning.

# Task
Classifica la domanda utente come:
- 'generica' se è una richiesta di aiuto, saluto, spiegazione, onboarding, conversazione, o riguarda l'app in generale
- 'dati' se richiede di consultare, filtrare, analizzare o aggregare i dati di scheduling

# Contesto Applicazione
L'app permette di:
- Gestire progetti, risorse, clienti, FTE, timeline, ecc.
- Visualizzare dashboard e report analitici sui dati di scheduling
- Usare una chat AI per chiedere informazioni sui dati o ricevere aiuto/conversare

# Struttura base dati principale
Colonne: PROJECT_DESCR (nome progetto), CLIENT (cliente), PM_SM (project manager), USER (utente/risorsa), STATUS (stato), PLANNED_FTE, ACTUAL_FTE, ITEM_TYPE, DELIVERY_TYPE, START_DATE, END_DATE, colonne mensili (gen, feb, ... dic) per FTE allocato.

# Esempi domande generiche
- "Ciao"
- "Come si usa la chat?"
- "Spiegami le funzionalità dell'app"
- "Quali sono le possibilità di analisi?"
- "Come posso aggiungere un nuovo progetto?"
- "A cosa serve questa applicazione?"
- "Quali sono le feature principali?"
- "Come posso ricevere supporto?"

# Esempi domande dati
- "Mostrami i progetti in corso"
- "Quanti FTE sono allocati a marzo?"
- "Chi lavora per il cliente ACME?"
- "Elenca i progetti gestiti da L. Mangili"
- "Qual è lo stato del progetto CRM Upgrade?"
- "Dammi la lista degli utenti attivi nel 2024"
- "Quali progetti sono terminati quest'anno?"
- "Report FTE per ogni mese"

# Reminder
Rispondi solo con 'generica' o 'dati'.
Non aggiungere spiegazioni.

Domanda utente: {user_input}
"""
    if client is None:
        return "generica"  # fallback prudente
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt],
        )
        if hasattr(response, 'text') and response.text:
            label = response.text.strip().lower()
            if 'generica' in label:
                return 'generica'
            if 'dati' in label:
                return 'dati'
        # fallback prudente
        return 'generica'
    except Exception:
        return 'generica'

def format_result_for_user(result):
    """
    Formatta dizionari/liste in output leggibile per l'utente (elenco puntato o tabella Markdown).
    """
    import pandas as pd
    if isinstance(result, dict):
        # Se tutte le voci sono liste di uguale lunghezza, tabella
        if all(isinstance(v, list) for v in result.values()) and len(set(len(v) for v in result.values())) == 1:
            df = pd.DataFrame(result)
            return df.to_markdown(index=False)
        # Altrimenti elenco puntato
        out = ""
        for k, v in result.items():
            if isinstance(v, list):
                out += f"**{k}:**\n"
                for item in v:
                    out += f"- {item}\n"
            elif isinstance(v, dict):
                out += f"**{k}:**\n"
                for subk, subv in v.items():
                    out += f"- {subk}: {subv}\n"
            else:
                out += f"- **{k}:** {v}\n"
        return out
    elif isinstance(result, list):
        # Se lista di dict, tabella
        if result and isinstance(result[0], dict):
            df = pd.DataFrame(result)
            return df.to_markdown(index=False)
        return "\n".join(f"- {item}" for item in result)
    else:
        return str(result)

def generate_llm_response(user_input: str, images: list = []) -> str:
    """
    Orchestrazione RAG a due step con supporto immagini:
    1. Classifica l'intento con LLM: 'generica' o 'dati'
    2. Se 'generica', rispondi con prompt solo contesto app
    3. Se 'dati', esegui il flusso attuale con query e dati
    """
    # Risposta custom se l'utente chiede il nome del bot
    name_queries = [
        "come ti chiami", "qual è il tuo nome", "chi sei", "come si chiama il bot", "nome del bot", "come ti posso chiamare", "presentati", "parlami di te"
    ]
    if any(q in user_input.lower() for q in name_queries):
        return f"{BOT_DESCRIPTION} Il mio nome è **{BOT_NAME}**."

    if client is None:
        return "⚠️ API key mancante. Impossibile contattare il modello."

    # 1. Classificazione intento
    intent = classify_intent_with_llm(user_input)
    if intent == 'generica':
        # Prompt solo contesto app, nessun dato
        generic_prompt = f"""
# Ruolo
Sei l'assistente AI dell'app Scheduling, piattaforma per la pianificazione e gestione risorse/progetti.

# Task
Rispondi in modo amichevole, chiaro e utile a domande generiche, onboarding, spiegazioni, saluti, richieste di aiuto, ecc. Non fornire dati specifici di scheduling.

# Contesto Applicazione
- L'app permette di gestire progetti, risorse, clienti, FTE, timeline, ecc.
- Dashboard e report analitici
- Chat AI per domande e supporto
- Funzionalità: CRUD progetti, allocazione risorse, validazione dati, backup automatici, analisi avanzate, AI multimodale

# Esempi domande generiche e risposte
- "Ciao" → "Ciao! Come posso aiutarti?"
- "Come si usa la chat?" → "Scrivi la tua domanda o richiesta nella casella in basso. Puoi chiedere sia informazioni sui dati che aiuto sull'app."
- "Quali sono le funzionalità principali?" → "L'app offre gestione progetti, analisi risorse, dashboard KPI, chat AI, backup automatici e molto altro."
- "Come posso ricevere supporto?" → "Puoi consultare la documentazione o contattare il team di sviluppo."

# Reminder
Rispondi sempre in italiano, in modo amichevole e sintetico.

Domanda utente: {user_input}
"""
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[generic_prompt],
        )
        if hasattr(response, 'text') and response.text:
            return response.text.strip()
        return "Posso aiutarti con informazioni sull'app o sulle sue funzionalità."
    else:
        # Flusso attuale: prompt con contesto + dati
        # Logica per identificare se la domanda riguarda una colonna chiave
        def question_targets_key_column(question: str) -> bool:
            question = question.lower()
            key_words = [
                'status', 'stato', 'ongoing', 'in progress', 'completato', 'completed', 'on hold', 'cancellato', 'cancelled',
                'client', 'cliente',
                'pm', 'project manager', 'scrum master', 'pm_sm',
                'user', 'utente', 'risorsa', 'persona', 'collaboratore',
                'progetto', 'project', 'project_descr', 'nome progetto', 'descrizione progetto',
                'item_type', 'tipologia', 'tipo attività',
                'delivery_type', 'tipo delivery'
            ]
            return any(k in question for k in key_words)
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
            # (MODIFICA) Se la domanda riguarda una colonna chiave, chiama SEMPRE la funzione di query generalizzata
            if question_targets_key_column(user_input):
                extracted_data = query_scheduling_data(user_input)
            elif extraction_code and "Non è necessaria alcuna estrazione dati" not in extraction_code:
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
            else:
                extracted_data = query_scheduling_data(user_input)
            final_parts = []
            final_text = f"""
{SYSTEM_PROMPT}

Domanda utente: {user_input}
Struttura dati:
{get_table_structure()}
"""
            if extracted_data is not None:
                final_text += f"\nRisultati estratti dal DataFrame:\n{format_result_for_user(extracted_data)}\n"
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
                text_val = str(response.text)
                # Se la risposta del modello non contiene dati reali, mostra direttamente i risultati estratti
                if "Risultati estratti dal DataFrame" in final_text or not text_val.strip():
                    return str(format_result_for_user(extracted_data))
                return text_val.strip()
            else:
                return str(format_result_for_user(extracted_data))
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