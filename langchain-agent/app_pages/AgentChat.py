import streamlit as st
import pandas as pd
from agent import create_technical_agent  # Assuming this is a custom module


# --- Helper Functions ---


def empty_df():
    st.session_state.df = None
def load_data(uploaded_file, sheet_name=None):
    """
    Loads data from an uploaded CSV or Excel file.
    Returns the DataFrame and the selected sheet name.
    """
    try:
        if uploaded_file.type == "text/csv":
            df = pd.read_csv(uploaded_file)
            sheet_name = "csv"
        else:
            xls = pd.ExcelFile(uploaded_file)
            sheet_names = xls.sheet_names
            # If a sheet is not specified, let the user select it
            if sheet_name is None:
                sheet_name = st.sidebar.selectbox("Select a Sheet", sheet_names)
            df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
        return df, sheet_name
    except Exception as e:
        st.sidebar.error(f"Error loading file: {e}")
        return None, None


def display_chat_messages():
    """Displays messages from the chat history."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def handle_user_input(prompt):
    """Handles user input and interacts with the AI agent."""
    if st.session_state.df is None:
        st.warning("Please upload a file first.")
        return

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("Analyzing your data..."):
        try:
            # Assuming create_technical_agent returns a Language Chain (LCEL) object
            response = st.session_state.agent.invoke(prompt)['output']
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.session_state.messages.append({"role": "assistant", "content": f"An error occurred: {e}"})
            st.error(f"Error invoking agent: {e}")

    # Rerun to update the chat UI
    st.rerun()


def clear_chat_and_data():
    """Clears all relevant session state variables."""
    for key in ["messages", "agent", "df", "file_id"]:
        st.session_state.pop(key, None)
    st.rerun()


# --- Main App Logic ---

def main():
    """Main function to run the Streamlit application."""
    st.set_page_config(page_title="Data Chat Agent", layout="wide")
    st.header("🤖️ Chat with your Data")

    # --- Sidebar for File Upload and Settings ---
    with st.sidebar:
        st.divider()
        st.header("Settings")
        allow_upload_file = st.radio('Data Type', ['Mocked Data', 'Upload File'], on_change=empty_df)
        # Mock file for demonstration if no file is uploaded
        if allow_upload_file == 'Mocked Data':
            mock_file_path = 'data/ppc_table.xlsx'
            try:
                xls = pd.ExcelFile(mock_file_path)
                sheet_names = xls.sheet_names
                sheet_name_mock = st.selectbox("Select a Mock Sheet", sheet_names, key="mock_sheet")

                st.session_state.df = pd.read_excel(mock_file_path, sheet_name=sheet_name_mock)
                st.session_state.file_id = f"mock_{mock_file_path}_{sheet_name_mock}"
            except FileNotFoundError:
                st.warning("Mock data file not found. Please upload a file.")

            st.markdown("---")
        if allow_upload_file == 'Upload File':

            uploaded_file = st.file_uploader("Or upload your CSV/Excel file", type=["csv", "xlsx"])

            if uploaded_file:
                df, sheet_name = load_data(uploaded_file)
                if df is not None:
                    st.session_state.df = df
                    st.session_state.file_id = f"{uploaded_file.name}_{uploaded_file.size}_{sheet_name}"

            st.markdown("---")
        if st.button("Clear Chat and Data"):
            clear_chat_and_data()

    # --- Main Content Area ---
    if not st.session_state.OPENAI_API_KEY:
        st.warning("⚠️ Please configure your OpenAI API key in the Settings page.")
        # Optionally, you could add a button to a settings page
        # if st.button("Go to Settings"):
        #     # Logic to navigate
        st.stop()

    # Check for API key before continuing
    if not st.session_state.get("OPENAI_API_KEY"):
        st.warning("⚠️ Please configure your OpenAI API key in the Settings page before using the app.")
        st.stop()

    # Preview of the loaded data
    if st.session_state.df is not None:
        with st.expander('Data Preview'):
            st.dataframe(st.session_state.df, height=200, use_container_width=True)

        # Agent Initialization
        if st.session_state.agent is None or st.session_state.file_id != st.session_state.get("last_file_id"):
            with st.spinner("Initializing the AI agent... This may take a moment."):
                st.session_state.agent = create_technical_agent(st.session_state.df)
                st.session_state.last_file_id = st.session_state.file_id
                st.session_state.messages = []  # Clear messages for new data

    # Chat UI
    with st.container(height=500, border=False):
        if not st.session_state.messages:
            with st.chat_message("assistant"):
                st.markdown("Hello! Upload a file and ask me questions about your data.")
        else:
            display_chat_messages()

    if prompt := st.chat_input("Ask a question about your data..."):
        handle_user_input(prompt)


if __name__ == '__main__':
    main()
