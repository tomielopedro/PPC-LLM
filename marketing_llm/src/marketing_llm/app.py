# app.py
import streamlit as st
from datetime import datetime
from crew import MarketingLlm
import pandas as pd


# Inicializar sessão
INITIAL_FILE = r'knowledge/teste_llm.xlsx'

sheets = pd.ExcelFile(INITIAL_FILE).sheet_names
with st.sidebar:
    selected_sheet = st.selectbox('Select a sheet', sheets)

    if selected_sheet:
        df = pd.read_excel(INITIAL_FILE, sheet_name=selected_sheet)
        df.to_csv('knowledge/llm_knowledge.csv', index=False)
        print(f'New sheet saved -> {selected_sheet}')

if "messages" not in st.session_state:
    st.session_state["messages"] = []

st.set_page_config(page_title="🤖 Chatbot with Agent", layout="wide")
st.title("🤖 Chatbot with Agent")

# Container para histórico do chat
chat_container = st.container()

with chat_container:
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Entrada do usuário
if prompt := st.chat_input("Write a message"):
    # Mostrar a mensagem do usuário
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Chamar sua LLM
    try:
        # O crew espera inputs como dicionário
        inputs = {
            "topic": prompt
        }

        response = MarketingLlm().crew().kickoff(inputs=inputs)

        # Se a resposta for objeto, converter para string
        if not isinstance(response, str):
            response = str(response)

    except Exception as e:
        response = f"⚠️ Error to process: {e}"

    # Mostrar a resposta
    st.session_state["messages"].append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
