import streamlit as st
import pandas as pd
from agent import create_technical_agent

def main():
    st.header("🤖️ Chat with agent")

    if not st.session_state["OPENAI_API_KEY"]:
        st.warning("⚠️ Please configure your OpenAI API key in the Settings page before using the app.")
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
        with st.expander('Data Preview'):
            st.dataframe(st.session_state.df, height=200, use_container_width=True)

        # Cria identificador único (arquivo + sheet)
        file_identifier = f"{uploaded_file.name}_{uploaded_file.size}_{sheet_name or 'csv'}"

        if st.session_state.agent is None or st.session_state.get("file_id") != file_identifier:
            with st.spinner("Initializing the AI agent..."):
                st.session_state.agent = create_technical_agent(st.session_state.df)
                st.session_state.file_id = file_identifier
                st.session_state.messages = []
    # Display chat messages
    with st.container(height=500, border=False):
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
            response = st.session_state.agent.invoke(prompt)['output']
            # raw_response, friendly_response = query_agent(st.session_state.agent, prompt)
            # assistant_response = f"**Technical response:**\n```\n{raw_response}\n```\n\n**User-friendly explanation:**\n{friendly_response}"
            st.session_state.messages.append({"role": "assistant", "content": response})

        st.rerun()

    # Clear chat and data
    if st.sidebar.button("Clear Chat and Data"):
        for key in ["messages", "agent", "df", "uploaded_file_data", "file_id"]:
            st.session_state.pop(key, None)
        st.rerun()

if __name__=='__main__':
    main()