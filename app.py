import streamlit as st

st.set_page_config(page_title="Scheduling", page_icon="📅", layout="wide")

st.title("Scheduling – Resource Planning")

with st.sidebar:
    st.header("Navigazione")
    st.markdown(
        """
        • **Projects** – add or edit project metadata.  
        • **Schedule** – manage allocations month by month.  
        • **Analytics** – deeper analysis of resource load.
        """
    )
    st.divider()
    st.header("💬 Chat Assistant")
    st.caption("LLM integration to ask natural‑language questions about your schedules.")
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    for message in st.session_state.messages:
        st.chat_message(message['role']).write(message['content'])
    prompt = st.chat_input("Ask me anything...", key="sidebar_chat")
    if prompt:
        st.session_state.messages.append({'role':'user','content':prompt})
        st.chat_message('assistant').write("⚙️ I'm a placeholder. LLM integration to be added.")

st.info("Use the sidebar to navigate sections and chat with the assistant.", icon="ℹ️")
