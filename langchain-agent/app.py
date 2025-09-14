import streamlit as st
import pandas as pd
from agent import create_technical_agent, query_agent

# =============================
# Streamlit Interface
# =============================

st.set_page_config(page_title="Chat with your Table", layout="wide")

# --- Inicialização do Estado da Sessão ---
# É uma boa prática inicializar todas as chaves do session_state no início.
if "messages" not in st.session_state:
    st.session_state.messages = []
if "OPENAI_API_KEY" not in st.session_state:
    st.session_state["OPENAI_API_KEY"] = ""
if "custom_prompt" not in st.session_state:
    st.session_state["custom_prompt"] = "Explain the technical response in a simple, clear, and user-friendly way."
if "agent" not in st.session_state:
    st.session_state.agent = None
if "df" not in st.session_state:
    st.session_state.df = None
if "uploaded_file_data" not in st.session_state:
    st.session_state.uploaded_file_data = None

# --- Abas da Interface ---
tabs = st.tabs(["Chat", "Settings"])

# --- Aba de Configurações (Settings) ---
with tabs[1]:
    st.header("⚙️ Settings")

    # Input da chave da API
    api_key = st.text_input(
        "Enter your OpenAI API key",
        type="password",
        value=st.session_state["OPENAI_API_KEY"]
    )
    if api_key != st.session_state["OPENAI_API_KEY"]:
        st.session_state["OPENAI_API_KEY"] = api_key
        st.success("API key set!")
        st.rerun()

    # Input do prompt customizado
    custom_prompt = st.text_area(
        "Custom prompt for user-friendly responses",
        st.session_state.get("custom_prompt"),
        height=150
    )
    if st.button("Save Prompt"):
        st.session_state["custom_prompt"] = custom_prompt
        st.success("Prompt updated!")

# --- Aba de Chat ---
with tabs[0]:
    st.write("## Chat with your Table (CSV/Excel)")

    # Verifica se a chave da API foi configurada
    if not st.session_state["OPENAI_API_KEY"]:
        st.warning("⚠️ Please configure your OpenAI API key in the Settings tab before using the app.")
        st.stop()

    # Uploader de arquivo na barra lateral
    uploaded_file = st.sidebar.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx"])

    if uploaded_file is not None:
        # Carrega o DataFrame a partir do arquivo
        try:
            if uploaded_file.type == "text/csv":
                df = pd.read_csv(uploaded_file)
            else:  # Para 'xlsx'
                xls = pd.ExcelFile(uploaded_file)
                sheet_names = xls.sheet_names
                selected_sheet = st.sidebar.selectbox("Select a Sheet", sheet_names)
                df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)

            st.session_state.df = df
        except Exception as e:
            st.sidebar.error(f"Error loading file: {e}")
            st.stop()

        # Exibe a pré-visualização dos dados
        st.subheader("Data Preview")
        st.dataframe(st.session_state.df, height=200, use_container_width=True)

        # Inicializa o agente se ele ainda não existir para o arquivo atual
        file_identifier = f"{uploaded_file.name}_{uploaded_file.size}"
        if st.session_state.agent is None or st.session_state.get("file_id") != file_identifier:
            with st.spinner("Initializing the AI agent..."):
                st.session_state.agent = create_technical_agent(st.session_state.df)
                st.session_state.file_id = file_identifier
                st.session_state.messages = []  # Limpa o chat para o novo arquivo

    # --- Container de Mensagens (estilo do segundo código) ---
    # Cria um container com altura fixa para exibir as mensagens.
    # Isso cria uma janela de chat rolável.
    messages_container = st.container(height=300, border=False)
    with messages_container:
        if not st.session_state.messages:
            with st.chat_message("assistant"):
                st.markdown("Olá! Faça o upload de um arquivo e me faça perguntas sobre seus dados.")
        else:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

    # --- Campo de Input do Chat ---
    if prompt := st.chat_input("Ask a question about your data..."):
        if st.session_state.df is None:
            st.warning("Please upload a file first.")
            st.stop()

        # Adiciona e exibe a mensagem do usuário
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Processa a resposta do agente
        with st.spinner("Analyzing..."):
            raw_response, friendly_response = query_agent(st.session_state.agent, prompt)

            # Formata a resposta completa do assistente
            assistant_response = f"**Technical response:**\n```\n{raw_response}\n```\n\n**User-friendly explanation:**\n{friendly_response}"
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})

        # Força o rerender para exibir a nova mensagem imediatamente
        st.rerun()

    # Botão para limpar o chat na barra lateral
    if st.sidebar.button("Clear Chat and Data"):
        # Limpa todo o estado da sessão relacionado ao arquivo e chat
        keys_to_clear = ["messages", "agent", "df", "uploaded_file_data", "file_id"]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()