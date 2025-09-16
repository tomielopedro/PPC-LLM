import streamlit as st

st.set_page_config(page_title="Data Manager", page_icon=":material/edit:", layout="wide")


def login_screen():
    st.header("This app is private.")
    st.subheader("Please log in.")
    st.button("Log in with Google", on_click=st.login)


if not st.user.is_logged_in:
    login_screen()
else:
    user_data = st.user.to_dict()

    # Inicializa o estado de sessão
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("OPENAI_API_KEY", "")
    st.session_state.setdefault(
        "custom_prompt",
        "Explain the technical response in a simple, clear, and user-friendly way."
    )
    st.session_state.setdefault("agent", None)
    st.session_state.setdefault("df", None)
    st.session_state.setdefault("uploaded_file_data", None)

    if st.secrets.get("LLM"):
        st.session_state.OPENAI_API_KEY = st.secrets.get("LLM")['api_key']

    # Topo da sidebar: foto redonda, nome, email e botão de logout
    st.sidebar.markdown(
        f"""
        <div style="text-align:center; padding:10px 0; border-bottom:1px solid #ddd; margin-bottom:10px;">
            <img src="{user_data['picture']}" width="100" style="border-radius:50%; display:block; margin:0 auto;">
            <p style="font-weight:bold; text-align:center; margin:5px 0 0 0;">Hello, {user_data['given_name']}!</p>
            <p style="text-align:center; margin:0;">{user_data['email']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.sidebar.button("Log out", on_click=st.logout)

    # Configura as páginas do aplicativo (abaixo do topo da sidebar)
    chat_page = st.Page("app_pages/AgentChat.py", title="Chat with agent", icon=":material/robot_2:")
    settings_page = st.Page("app_pages/Settings.py", title="Settings", icon=":material/settings:")

    pg = st.navigation([chat_page, settings_page])
    pg.run()
