
import streamlit as st

st.title("💬 Chat Assistant (coming soon)")

st.info("LLM integration to ask natural‑language questions about your schedules.")

if 'messages' not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    st.chat_message(message['role']).write(message['content'])

prompt = st.chat_input("Ask me anything...")
if prompt:
    st.session_state.messages.append({'role':'user','content':prompt})
    st.chat_message('assistant').write("⚙️ I'm a placeholder. LLM integration to be added.")
