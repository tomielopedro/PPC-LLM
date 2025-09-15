import streamlit as st
def main():
    st.header("⚙️ Settings")

    # API key input
    api_key = st.text_input(
        "Enter your OpenAI API key",
        type="password",
        value=st.session_state["OPENAI_API_KEY"]
    )

    if st.button("Save Api Key", disabled=api_key == ''):
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

if __name__=='__main__':
    main()