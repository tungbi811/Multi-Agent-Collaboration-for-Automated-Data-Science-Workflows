from crewai import Agent, Task, Crew, Process

# Path to your dataset (input here)
data_path = "./data/house_prices_train.csv"

# Data Analyst Agent
data_analyst = Agent(
    role="Data Analyst",
    goal="Analyze datasets and extract meaningful insights",
    backstory="Expert in statistical analysis and data interpretation with Python skills.",
    allow_code_execution=True,
    verbose=True
)

# Machine Learning Engineer
ml_engineer = Agent(
    role="ML Engineer", 
    goal="Build and optimize machine learning models",
    backstory="Experienced in developing ML pipelines and model deployment.",
    allow_code_execution=True,
    verbose=True
)

# Data Scientist
data_scientist = Agent(
    role="Data Scientist",
    goal="Lead data science projects and provide strategic insights",
    backstory="Senior data scientist with expertise in predictive modeling and business intelligence.",
    allow_code_execution=True,
    verbose=True
)

# Tasks (injecting the dataset path)
data_exploration_task = Task(
    description=f"Explore the dataset located at `{data_path}`, identify patterns, and generate summary statistics.",
    expected_output="Data exploration report with key findings and visualizations.",
    agent=data_analyst
)

model_building_task = Task(
    description=f"Using the dataset at `{data_path}`, build a machine learning model based on the analyzed data.",
    expected_output="Trained ML model with performance metrics.",
    agent=ml_engineer
)

insights_task = Task(
    description="Interpret the model results and provide business recommendations based on the dataset analysis and model performance.",
    expected_output="Strategic insights and actionable recommendations.",
    agent=data_scientist
)

# Create the data science crew
data_science_crew = Crew(
    agents=[data_analyst, ml_engineer, data_scientist],
    tasks=[data_exploration_task, model_building_task, insights_task],
    process=Process.sequential,
    verbose=True
)

# Execute the crew
result = data_science_crew.kickoff()
print(result)
