import streamlit as st
import pandas as pd
from agent import create_technical_agent, query_agent

# =============================
# Streamlit Interface
# =============================

st.set_page_config(page_title="Chat with your Table", layout="wide")
tabs = st.tabs(["Chat", "Settings"])

# --- Settings tab ---
with tabs[1]:
    st.header("⚙️ Settings")
    api_key = st.text_input("Enter your OpenAI API key", type="password")
    if api_key:
        st.session_state["OPENAI_API_KEY"] = api_key
        st.success("API key set!")

    custom_prompt = st.text_area(
        "Custom prompt for user-friendly responses",
        st.session_state.get(
            "custom_prompt",
            "Explain the technical response in a simple, clear, and user-friendly way."
        ),
        height=150
    )
    if st.button("Save Prompt"):
        st.session_state["custom_prompt"] = custom_prompt
        st.success("Prompt updated!")

# --- Chat tab ---
with tabs[0]:
    st.title("📊 Chat with your Table (CSV/Excel)")

    uploaded_file = st.sidebar.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx"])

    if uploaded_file is not None:
        file_identifier = f"{uploaded_file.name}_{uploaded_file.size}"

        if "uploaded_file_data" not in st.session_state or st.session_state.uploaded_file_data["id"] != file_identifier:
            st.session_state.uploaded_file_data = {
                "id": file_identifier,
                "name": uploaded_file.name,
                "type": uploaded_file.type,
                "file_object": uploaded_file
            }
            st.session_state.df = None
            st.session_state.messages = []
            st.session_state.agent = None
            st.session_state.sheet_names = []
            st.session_state.selected_sheet = None
            st.success("File uploaded successfully!")

        file_data = st.session_state.uploaded_file_data
        file_object = file_data["file_object"]

        # Excel case
        if file_data["type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            xls = pd.ExcelFile(file_object)
            st.session_state.sheet_names = xls.sheet_names
            if st.session_state.selected_sheet not in st.session_state.sheet_names:
                st.session_state.selected_sheet = st.session_state.sheet_names[0]

            selected_sheet = st.sidebar.selectbox("Select a Sheet", st.session_state.sheet_names, key="sheet_selector")
            st.session_state.selected_sheet = selected_sheet

            if st.session_state.df is None or st.session_state.df_source != f"{file_identifier}_{selected_sheet}":
                st.session_state.df = pd.read_excel(file_object, sheet_name=selected_sheet)
                st.session_state.df_source = f"{file_identifier}_{selected_sheet}"
                st.session_state.agent = None
                st.session_state.messages = []
                st.success(f"Sheet '{selected_sheet}' loaded successfully!")

        # CSV case
        elif file_data["type"] == "text/csv":
            st.session_state.sheet_names = []
            st.session_state.selected_sheet = None

            if st.session_state.df is None or st.session_state.df_source != file_identifier:
                st.session_state.df = pd.read_csv(file_object)
                st.session_state.df_source = file_identifier
                st.session_state.agent = None
                st.session_state.messages = []
                st.success("CSV file loaded successfully!")

        df = st.session_state.df

        st.subheader("Data Preview")
        st.dataframe(df, height=300)

        if st.session_state.agent is None:
            with st.spinner("Initializing the AI agent..."):
                st.session_state.agent = create_technical_agent(df)
            st.success("Technical agent initialized!")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask a question about your data..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Analyzing and simplifying response..."):
                    raw_response, friendly_response = query_agent(st.session_state.agent, prompt)
                    st.markdown(f"**Technical response:** {raw_response}")
                    st.markdown(f"**User-friendly explanation:** {friendly_response}")

                st.session_state.messages.append({"role": "assistant", "content": friendly_response})
    else:
        st.info("Please upload a CSV or Excel file in the sidebar to start.")

    if st.sidebar.button("Clear Chat"):
        st.session_state.messages = []
        st.session_state.agent = None
        st.session_state.df = None
        st.session_state.uploaded_file_data = None
        st.session_state.sheet_names = []
        st.session_state.selected_sheet = None
        st.rerun()
