import streamlit as st
import pandas as pd
from agent import create_technical_agent, query_agent

st.set_page_config(page_title="Chat with your Table", layout="wide")

# Initialize session state
st.session_state.setdefault("messages", [])
st.session_state.setdefault("OPENAI_API_KEY", "")
st.session_state.setdefault("custom_prompt", "Explain the technical response in a simple, clear, and user-friendly way.")
st.session_state.setdefault("agent", None)
st.session_state.setdefault("df", None)
st.session_state.setdefault("uploaded_file_data", None)

# App tabs
tabs = st.tabs(["Chat", "Settings"])

# Settings tab
with tabs[1]:
    st.header("⚙️ Settings")

    # API key input
    api_key = st.text_input(
        "Enter your OpenAI API key",
        type="password",
        value=st.session_state["OPENAI_API_KEY"]
    )

    if st.button("Save Api Key", disabled=api_key is ''):
        st.session_state["OPENAI_API_KEY"] = api_key
        st.success("API key set!")

    # Custom prompt input
    custom_prompt = st.text_area(
        "Custom prompt for user-friendly responses",
        st.session_state["custom_prompt"],
        height=150
    )
    if st.button("Save Prompt"):
        st.session_state["custom_prompt"] = custom_prompt
        st.success("Prompt updated!")

# Chat tab
with tabs[0]:
    st.write("## Chat with your Table (CSV/Excel)")

    if not st.session_state["OPENAI_API_KEY"]:
        st.warning("⚠️ Please configure your OpenAI API key in the Settings tab before using the app.")
        st.stop()

    # File uploader
    uploaded_file = st.sidebar.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx"])
    if uploaded_file:
        try:
            if uploaded_file.type == "text/csv":
                df = pd.read_csv(uploaded_file)
                sheet_name = None  # CSV não tem sheet
            else:
                xls = pd.ExcelFile(uploaded_file)
                sheet_names = xls.sheet_names
                sheet_name = st.sidebar.selectbox("Select a Sheet", sheet_names)
                df = pd.read_excel(uploaded_file, sheet_name=sheet_name)

            st.session_state.df = df
        except Exception as e:
            st.sidebar.error(f"Error loading file: {e}")
            st.stop()

        # Preview
        st.subheader("Data Preview")
        st.dataframe(st.session_state.df, height=200, use_container_width=True)

        # Cria identificador único (arquivo + sheet)
        file_identifier = f"{uploaded_file.name}_{uploaded_file.size}_{sheet_name or 'csv'}"

        if st.session_state.agent is None or st.session_state.get("file_id") != file_identifier:
            with st.spinner("Initializing the AI agent..."):
                st.session_state.agent = create_technical_agent(st.session_state.df)
                st.session_state.file_id = file_identifier
                st.session_state.messages = []
    # Display chat messages
    with st.container(height=300, border=False):
        messages_container = st.container()
        with messages_container:
            if not st.session_state.messages:
                with st.chat_message("assistant"):
                    st.markdown("Hello! Upload a file and ask me questions about your data.")
            else:
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question about your data..."):
        if st.session_state.df is None:
            st.warning("Please upload a file first.")
            st.stop()

        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("Analyzing..."):
            raw_response, friendly_response = query_agent(st.session_state.agent, prompt)
            assistant_response = f"**Technical response:**\n```\n{raw_response}\n```\n\n**User-friendly explanation:**\n{friendly_response}"
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})

        st.rerun()

    # Clear chat and data
    if st.sidebar.button("Clear Chat and Data"):
        for key in ["messages", "agent", "df", "uploaded_file_data", "file_id"]:
            st.session_state.pop(key, None)
        st.rerun()
