from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crewai_tools import CSVSearchTool
# Criar um Tool do CrewAI que usa o LangChain Pandas Agent
from crewai.tools import BaseTool
import pandas as pd
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI


class LangchainPandasTool(BaseTool):
    name: str = "LangchainPandasTool"
    description: str = "Use this tool to analyze a pandas DataFrame"

    def _run(self, query: str) -> str:
        try:
            df = pd.read_csv("knowledge/llm_knowledge.csv")  # last dataset saved
            llm = ChatOpenAI(model="gpt-4o-mini")
            agent = create_pandas_dataframe_agent(llm, df, verbose=True, allow_dangerous_code=True, agent_type="openai-tools")
            return agent.run(query)
        except Exception as e:
            return f"Error: {e}"



@CrewBase
class MarketingLlm():
    """MarketingLlm crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def manager(self) -> Agent:
        return Agent(
            config=self.agents_config['DE'],  # type: ignore[index]
            verbose=True,

        )

    @agent
    def data_analyst(self) -> Agent:
        tool = LangchainPandasTool()

        return Agent(
            config=self.agents_config['data_analyst'],  # type: ignore[index]
            tools=[tool],
            verbose=True
        )

    @agent
    def csv_search(self) -> Agent:
        tool = CSVSearchTool(csv="knowledge/llm_knowledge.csv")

        return Agent(
            config=self.agents_config['csv_search'],  # type: ignore[index]
            tools=[tool],
            verbose=True
        )

    @agent
    def formatter(self) -> Agent:
        return Agent(
            config=self.agents_config['formatter'],  # type: ignore[index]
            verbose=True
        )

    @task
    def manager_task(self) -> Task:
        return Task(
            config=self.tasks_config['interpreter_task'],  # type: ignore[index]
        )

    @task
    def data_analyst_task(self) -> Task:
        return Task(
            config=self.tasks_config['data_analyst_task'],  # type: ignore[index]
        )

    @task
    def csv_search_task(self) -> Task:
        return Task(
            config=self.tasks_config['csv_search_task'],  # type: ignore[index]
        )

    @task
    def formatter_task(self) -> Task:
        return Task(
            config=self.tasks_config['formatter_task'],  # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.hierarchical,
            verbose=True
        )
