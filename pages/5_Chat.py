import streamlit as st
import os
import pandas as pd
from google import genai
from dotenv import load_dotenv
from src.data_access import load_scheduling

# Carica variabili da .env
load_dotenv()

st.set_page_config(page_title="Chat", page_icon="💬", layout="wide")

st.title("💬 Chat Assistant")

st.caption("LLM integration to ask natural-language questions about your schedules.")

# Store chat messages in session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Configura API key
API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

# Crea client Gemini
client = None
if API_KEY:
    client = genai.Client(api_key=API_KEY)
else:
    st.warning("⚠️ Imposta la variabile d'ambiente GOOGLE_API_KEY per utilizzare il chatbot.")

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

def query_scheduling_data(query_description: str) -> str:
    """Esegue query sui dati di scheduling basandosi sulla descrizione della richiesta."""
    import pandas as pd
    import re
    try:
        df = load_scheduling()
        query_lower = query_description.lower()

        def normalize(s):
            return re.sub(r'[^a-z0-9 ]', '', s.lower())

        # Query per progetti di uno o più utenti menzionati nella query
        if "user" in df.columns or "USER" in df.columns:
            user_col = "USER" if "USER" in df.columns else "user"
            users_series = pd.Series(df[user_col].dropna().astype(str))
            users_list = users_series.drop_duplicates().tolist()
            found_users = []
            # 1. Match completo
            for user in users_list:
                if user.lower() in query_lower or query_lower in user.lower():
                    found_users.append(user)
            if found_users:
                result = ""
                for found_user in found_users:
                    user_projects = df[df[user_col].astype(str).str.lower() == found_user.lower()]
                    projects = user_projects["PROJECT_DESCR"].dropna().drop_duplicates().tolist() if "PROJECT_DESCR" in user_projects.columns else []
                    n_proj = len(projects)
                    if n_proj > 0:
                        result += f"{found_user} lavora a {n_proj} progetti.\n"
                    else:
                        result += f"{found_user} non ha progetti assegnati.\n"
                return result.strip()
            # 2. Match parziale (tokenizzazione)
            query_words = set(normalize(query_description).split())
            partial_matches = []
            for user in users_list:
                user_words = set(normalize(user).split())
                if user_words & query_words:
                    partial_matches.append(user)
            if partial_matches:
                result = ""
                for found_user in partial_matches:
                    user_projects = df[df[user_col].astype(str).str.lower() == found_user.lower()]
                    projects = user_projects["PROJECT_DESCR"].dropna().drop_duplicates().tolist() if "PROJECT_DESCR" in user_projects.columns else []
                    n_proj = len(projects)
                    if n_proj > 0:
                        result += f"Forse ti riferivi a: {found_user}\n{found_user} lavora a {n_proj} progetti.\n"
                    else:
                        result += f"Forse ti riferivi a: {found_user}\n{found_user} non ha progetti assegnati.\n"
                return result.strip()
            # Se non trova, mostra elenco utenti
            if any(word in query_lower for word in ["lavora", "works", "progetti", "projects", "utente", "user"]):
                return "Utente non trovato. Utenti disponibili: " + ", ".join(users_list[:10])

        # Query per progetti specifici
        if any(word in query_lower for word in ["progetto", "project", "progetti", "projects"]):
            if "PROJECT_DESCR" in df.columns:
                projects = list(pd.Series(df["PROJECT_DESCR"]).dropna().drop_duplicates())
                return f"PROGETTI DISPONIBILI ({len(projects)}):\n" + "\n".join([f"• {p}" for p in projects[:10]])

        # Query per utenti
        if any(word in query_lower for word in ["utente", "user", "utenti", "users", "persona", "person"]):
            if "USER" in df.columns:
                users = list(pd.Series(df["USER"]).dropna().drop_duplicates())
                return f"UTENTI DISPONIBILI ({len(users)}):\n" + "\n".join([f"• {u}" for u in users[:10]])

        # Query per clienti
        if any(word in query_lower for word in ["cliente", "client", "clienti", "clients"]):
            if "CLIENT" in df.columns:
                clients = list(pd.Series(df["CLIENT"]).dropna().drop_duplicates())
                return f"CLIENTI DISPONIBILI ({len(clients)}):\n" + "\n".join([f"• {c}" for c in clients[:10]])

        # Query per status
        if any(word in query_lower for word in ["status", "stato", "stati"]):
            if "STATUS" in df.columns:
                statuses = list(pd.Series(df["STATUS"]).dropna().drop_duplicates())
                return f"STATUS DISPONIBILI ({len(statuses)}):\n" + "\n".join([f"• {s}" for s in statuses])

        # Query per FTE
        if any(word in query_lower for word in ["fte", "allocazione", "allocation", "carico", "load"]):
            if "PLANNED_FTE" in df.columns and "ACTUAL_FTE" in df.columns:
                total_planned = df["PLANNED_FTE"].sum()
                total_actual = df["ACTUAL_FTE"].sum()
                return f"FTE TOTALE:\n• PLANNED_FTE: {total_planned}\n• ACTUAL_FTE: {total_actual}"

        # Query per anno
        if any(word in query_lower for word in ["anno", "year", "anni", "years"]):
            if "YEAR" in df.columns:
                years = sorted(list(pd.Series(df["YEAR"]).dropna().drop_duplicates()))
                return f"ANNI DISPONIBILI: {', '.join(map(str, years))}"

        # Query generica per statistiche
        return f"STATISTICHE GENERALI:\n• Righe totali: {len(df)}\n• Progetti unici: {df['PROJECT_DESCR'].nunique() if 'PROJECT_DESCR' in df.columns else 'N/A'}\n• Utenti unici: {df['USER'].nunique() if 'USER' in df.columns else 'N/A'}"

    except Exception as e:
        return f"Errore nell'esecuzione della query: {e}"

def should_query_data(user_input: str) -> bool:
    """Determina se la richiesta dell'utente necessita di dati dall'Excel."""
    query_lower = user_input.lower()
    
    # Parole chiave che indicano necessità di dati
    data_keywords = [
        "quanti", "quante", "quale", "quali", "chi", "dove", "quando",
        "progetto", "progetti", "utente", "utenti", "cliente", "clienti",
        "fte", "allocazione", "status", "stato", "anno", "anni",
        "dati", "informazioni", "statistiche", "elenco", "lista",
        "show", "display", "list", "count", "find", "search",
        "lavora", "works", "who", "what", "which"
    ]
    
    return any(keyword in query_lower for keyword in data_keywords)

SYSTEM_PROMPT = (
    "You are an AI assistant integrated an app that helps users with "
    "resource planning and scheduling. The app has these sections:\n"
    "• Scheduling – an interactive table where users filter and view monthly allocation data loaded from an Excel file.\n"
    "• Projects – metadata management for each project: insert, delete or update project data.\n"
    "• Analytics – visual insights on workload and capacity.\n"
    "Data columns that represent months are prefixed by Italian abbreviations (gen, feb, mar, …) and numeric values are expressed in person-days.\n"
    "When asked questions, explain how to perform operations in the app, manipulate DataFrames, or interpret scheduling data.\n"
    "If calculations are requested, reason step-by-step. Use markdown in the answer when appropriate.\n"
    "Remember the conversation context and refer to previous questions when relevant.\n"
    "IMPORTANTE: Se l'utente chiede informazioni sui dati (progetti, utenti, FTE, etc.), usa le informazioni fornite nel contesto per rispondere in modo accurato.\n"
    "SE nel contesto sono presenti dati estratti dalla tabella Scheduling (ad esempio, elenchi di progetti, utenti, FTE, ecc.), DEVI rispondere utilizzando SOLO quei dati. "
    "Non suggerire mai di usare l'app o filtri manuali se i dati sono già forniti. Se la risposta è nei dati, elencala direttamente. Se non trovi la risposta nei dati forniti, rispondi che non è presente nei dati, senza suggerire altre azioni."
)

def generate_llm_response(user_input: str) -> str:
    """Interroga Gemini Flash 2.5 e restituisce la risposta con memoria della conversazione."""
    if client is None:
        return "⚠️ API key mancante. Impossibile contattare il modello."

    try:
        # Prepara il contenuto con la memoria della conversazione
        # Inizia con il system prompt
        conversation_content = SYSTEM_PROMPT + "\n\n"
        
        # Aggiungi la struttura della tabella
        table_structure = get_table_structure()
        conversation_content += table_structure + "\n\n"
        
        # Se la richiesta necessita di dati, aggiungi query results
        if should_query_data(user_input):
            query_results = query_scheduling_data(user_input)
            conversation_content += f"DATI CORRENTI DALLA TABELLA SCHEDULING:\n{query_results}\n\n"
        
        # Aggiungi tutti i messaggi precedenti per mantenere il contesto
        for message in st.session_state.messages:
            if message['role'] == 'user':
                conversation_content += f"User: {message['content']}\n"
            elif message['role'] == 'assistant':
                conversation_content += f"Assistant: {message['content']}\n"
        
        # Aggiungi il messaggio corrente
        conversation_content += f"User: {user_input}"
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=conversation_content,
        )
        
        # Gestisci la risposta in modo sicuro
        if response and hasattr(response, 'text') and response.text:
            return response.text.strip()
        else:
            return "❌ Risposta vuota dal modello."
            
    except Exception as e:
        return f"❌ Errore durante la chiamata al modello: {e}"

# Funzione per pulire la conversazione
def clear_conversation():
    st.session_state.messages = []

# Pulsante per pulire la conversazione
if st.button("🗑️ Clear Conversation", help="Clear all chat history"):
    clear_conversation()
    st.rerun()

# Input for new message
prompt = st.chat_input("Ask me anything...", key="chat_input")
if prompt:
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    # Ottieni risposta dal modello
    assistant_reply = generate_llm_response(prompt)
    st.session_state.messages.append({'role': 'assistant', 'content': assistant_reply})

# Render all messages (after possibly adding new ones)
for message in st.session_state.messages:
    st.chat_message(message['role']).write(message['content']) 