import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_experimental.agents import create_pandas_dataframe_agent
import streamlit as st


def create_technical_agent(df: pd.DataFrame):
    """Technical agent to work directly with the data."""
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        api_key=st.session_state.get("OPENAI_API_KEY")
    )
    agent = create_pandas_dataframe_agent(
        llm,
        df,
        verbose=True,
        agent_executor_kwargs={"handle_parsing_errors": True},
        allow_dangerous_code=True
    )
    return agent


def explain_answer(raw_answer: str, user_question: str) -> str:
    """Explainer agent to make the response more user-friendly."""
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7,
        api_key=st.session_state.get("OPENAI_API_KEY")
    )
    base_prompt = st.session_state.get(
        "custom_prompt",
        "Explain the technical response in a simple, clear, and user-friendly way."
    )
    prompt = f"""
    {base_prompt}

    User question: "{user_question}".
    Technical answer: "{raw_answer}".
    """
    response = llm.invoke(prompt)
    return response.content.strip()


def query_agent(agent, query: str):
    """Run a query through the technical agent and generate a friendly explanation."""
    if agent is None:
        return "Agent not initialized.", "Agent not initialized."
    try:
        raw_response = agent.invoke({"input": query}).get(
            "output",
            "Could not get a response from the agent."
        )
        friendly_response = explain_answer(raw_response, query)
        return raw_response, friendly_response
    except Exception as e:
        return f"Error: {e}", f"Error: {e}"
