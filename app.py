
import streamlit as st

st.set_page_config(page_title="Scheduling", page_icon="📅", layout="wide")

st.title("Scheduling – Resource Planning")
st.markdown(
    """
    Use the sidebar to navigate through the sections:

    1. **Dashboard** – high‑level insights.
    2. **Projects** – add or edit project metadata.
    3. **Schedule** – manage allocations month by month.
    4. **Analytics** – deeper analysis of resource load.
    5. **Chat** – ask questions (LLM integration coming soon).
    """
)

st.info("This is the landing page. Choose a section from the sidebar.", icon="ℹ️")
