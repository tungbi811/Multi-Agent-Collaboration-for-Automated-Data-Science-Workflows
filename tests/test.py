from crewai import Agent, Task, Crew, Process
from crewai_tools import CodeInterpreterTool
from crewai_tools import FileWriterTool
from langchain.tools import tool
import os
import subprocess
import sys
from dotenv import load_dotenv 


##############
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Tools
code_tool = CodeInterpreterTool()
write_tool = FileWriterTool()

# Agent definition
agent = Agent(
    role="Python Code Execution Specialist",
    goal=(
        "Explore a dataset from a given path and produce summary insights with simple charts."
    ),
    backstory=(
        "An expert in data exploration, statistics, and visualization."
    ),
    tools=[code_tool, write_tool],
    allow_code_execution=True,
    code_execution_mode="safe",
    verbose=True,
    allow_delegation=False,
)

# Task definition
task = Task(
    description=(
        "Provided data path:\n\n"
        "{question}\n\n"
        "Can you write for me code to analyse this data and save it to ./generated_code folder using FileWriter tool"
        "And then analyse what you found"
    ),
    expected_output=("The actual code used to get the answer to the file."),
    agent=agent,
)

# Crew orchestration
crew = Crew(
    agents=[agent],
    tasks=[task],
    process=Process.sequential,
    verbose=True
)

# Kickoff
question = "../data/data_science_salaries/data_science_salaries.csv"
result = crew.kickoff(inputs={"question": question})
print(result)