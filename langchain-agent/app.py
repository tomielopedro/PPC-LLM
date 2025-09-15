import streamlit as st
import pandas as pd
from agent import create_technical_agent

st.set_page_config(page_title="Home", layout="wide")

# Initialize session state
st.session_state.setdefault("messages", [])
st.session_state.setdefault("OPENAI_API_KEY", "")
st.session_state.setdefault("custom_prompt", "Explain the technical response in a simple, clear, and user-friendly way.")
st.session_state.setdefault("agent", None)
st.session_state.setdefault("df", None)
st.session_state.setdefault("uploaded_file_data", None)



chat = st.Page("app_pages/AgentChat.py", title="Chat with agent", icon=":material/robot_2:")
settings = st.Page("app_pages/Settings.py", title="Settings", icon=":material/settings:")

pg = st.navigation([chat, settings])
st.set_page_config(page_title="Data manager", page_icon=":material/edit:")
pg.run()