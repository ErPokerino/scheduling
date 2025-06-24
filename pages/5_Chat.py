import streamlit as st
import os
from google import genai
from dotenv import load_dotenv

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

SYSTEM_PROMPT = (
    "You are an AI assistant integrated in a Streamlit app that helps users with "
    "resource planning and scheduling. The app has these sections:\n"
    "• Scheduling – an interactive table where users filter and view monthly allocation data loaded from an Excel file.\n"
    "• Projects – metadata management for each project.\n"
    "• Analytics – visual insights on workload and capacity.\n"
    "Data columns that represent months are prefixed by Italian abbreviations (gen, feb, mar, …) and numeric values are expressed in person-days.\n"
    "When asked questions, explain how to perform operations in the app, manipulate DataFrames, or interpret scheduling data.\n"
    "If calculations are requested, reason step-by-step. Use markdown in the answer when appropriate."
)

def generate_llm_response(user_input: str) -> str:
    """Interroga Gemini Flash 2.5 e restituisce la risposta."""
    if client is None:
        return "⚠️ API key mancante. Impossibile contattare il modello."

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[SYSTEM_PROMPT, user_input],
        )
        return response.text.strip()
    except Exception as e:
        return f"❌ Errore durante la chiamata al modello: {e}"

# Render previous messages
# (loop spostato in fondo per evitare duplicazioni)
# for message in st.session_state.messages:
#     st.chat_message(message['role']).write(message['content'])

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