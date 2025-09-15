from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
import pandas as pd
import streamlit as st




def create_technical_agent(df: pd.DataFrame, custom_prompt: str = ""):
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0,
        api_key=st.session_state.get("OPENAI_API_KEY")
    )

    strict_prefix = f"""
    You are a data analysis assistant. IMPORTANT RULES:
    1) Do not invent or guess values. Only answer using the exact outputs produced by executed Python code.
    2) When you call the python tool, wait for the tool output and base the final answer strictly on that output.
    3) When asked to list items, return the FULL list exactly as produced by Python (JSON array or bulleted list). Do not summarize or omit elements.
    4) If the python output is empty, say exactly: "No rows found" and show the python output.
    5) Alwais execute this python command at end **df.to_csv('teste.csv')**
    {custom_prompt}
    """

    agent = create_pandas_dataframe_agent(
        llm,
        df,
        verbose=True,
        prefix=strict_prefix,
        agent_executor_kwargs={"handle_parsing_errors": True},
        allow_dangerous_code=True,
        agent_type='openai-tools'
    )
    return agent