from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List


@CrewBase
class CrispDMCrew:
    """ CRISP-DM crew for business action recommendation """
    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def business_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['business_analyst'], # type: ignore[index]
            verbose=True
        )
    
    @agent
    def data_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['data_analyst'], # type: ignore[index]
            verbose=True
        )
    
    @agent
    def data_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['data_engineer'], # type: ignore[index]
            verbose=True
        )
    
    @agent
    def data_scientist(self) -> Agent:
        return Agent(
            config=self.agents_config['data_scientist'], # type: ignore[index]
            verbose=True
        ) 
    
    @task
    def business_analyst_task(self) -> Task:
        return Task(
            config=self.tasks_config['business_analyst_task'], # type: ignore[index]
        )
    
    @task
    def data_analyst_task(self) -> Task:
        return Task(
            config=self.tasks_config['data_analyst_task'], # type: ignore[index]
            #get output from business analyst task as context
            context = [self.business_analyst_task()]
        )
    
    @task
    def data_engineer_task(self) -> Task:
        return Task(
            config=self.tasks_config['data_engineer_task'], # type: ignore[index]
            context = [self.data_analyst_task()]
        )
    
    @task
    def data_scientist_task(self) -> Task:
        return Task(
            config=self.tasks_config['data_scientist_task'], # type: ignore[index]
            context = [self.business_analyst_task(), self.data_analyst_task(), self.data_engineer_task()]
        )
    @crew
    def crew(self) -> Crew:
        """Creates the CrispDMCrew"""
        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
    