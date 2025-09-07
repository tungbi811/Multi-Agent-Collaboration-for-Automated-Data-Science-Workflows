# configs/crew.py
from typing import List
from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, task, crew
from crewai_tools import CodeInterpreterTool

# One shared Python executor for agents that need to run code.
# It executes Python in a sandbox (Docker if available) and returns stdout/stderr,
# letting agents save any files under ./artifacts.
code_exec = CodeInterpreterTool()


@CrewBase
class CRISPDMCrew:
    """
    Multi-agent CRISP-DM workflow implemented with CrewAI.
    Agents:
      - Business Analyst
      - Data Explorer
      - Data Engineer
      - Model Builder
      - Evaluator
      - Business Translator
      - (Optional) Code Executor - generic runtime to execute an arbitrary code snippet

    Run with:
        from configs.crew import CRISPDMCrew
        CRISPDMCrew().crew().kickoff(inputs={"dataset_path": "./data/house_prices/house_prices_train.csv"})
    """

    agents: List[Agent]
    tasks: List[Task]

    # ============== AGENTS ==============

    @agent
    def business_analyst(self) -> Agent:
        return Agent(
            role="Business Analyst",
            goal=(
                "Intake the user's request, validate it against the dataset schema, "
                "and determine the most suitable ML task type(s) with clear business alignment."
            ),
            backstory=(
                "An experienced BA who translates business goals into precise data science specifications, "
                "KPIs, assumptions, risks, and acceptance criteria."
            ),
            verbose=True,
        )

    @agent
    def data_explorer(self) -> Agent:
        return Agent(
            role="Data Explorer",
            goal=(
                "Perform lightweight EDA, summarize schema and distributions, "
                "identify data quality issues, and produce handoff notes for data preparation."
            ),
            backstory="A swift analyst focused on quick, surgical EDA without mutating data.",
            tools=[code_exec],
            verbose=True,
        )

    @agent
    def data_engineer(self) -> Agent:
        return Agent(
            role="Data Engineer",
            goal=(
                "Prepare training-ready data: clean/transform, feature engineer, "
                "and create train/validation/test splits. Save outputs to ./artifacts."
            ),
            backstory="Builds robust, reproducible pipelines with strong leakage prevention.",
            tools=[code_exec],
            verbose=True,
        )

    @agent
    def model_builder(self) -> Agent:
        return Agent(
            role="Model Builder",
            goal=(
                "Train and tune multiple candidate models, compare metrics, "
                "persist the best model and preprocessing artifacts to ./artifacts."
            ),
            backstory="A meticulous practitioner who documents experiments and avoids leakage.",
            tools=[code_exec],
            verbose=True,
        )

    @agent
    def evaluator(self) -> Agent:
        return Agent(
            role="Evaluator",
            goal=(
                "Recompute metrics on the test set, perform error/segment analysis, "
                "check robustness/fairness/operational constraints, and issue a verdict."
            ),
            backstory="Connects model performance back to KPIs and business constraints.",
            tools=[code_exec],
            verbose=True,
        )

    @agent
    def business_translator(self) -> Agent:
        return Agent(
            role="Business Translator",
            goal=(
                "Translate technical results into clear business language, "
                "highlight strengths/risks/trade-offs, and propose deployment & monitoring."
            ),
            backstory="Bridges data science outputs to non-technical stakeholders.",
            verbose=True,
        )

    # Optional agent mirroring your Autogen CodeExecutor (generic runtime).
    @agent
    def code_executor(self) -> Agent:
        return Agent(
            role="Code Executor",
            goal=(
                "Execute provided Python code safely. Ensure artifacts are saved to ./artifacts "
                "and return stdout/stderr plus any generated file paths."
            ),
            backstory="A neutral operator that runs code snippets on demand for the crew.",
            tools=[code_exec],
            allow_delegation=False,
            verbose=True,
        )

    # ============== TASKS ==============

    @task
    def t_ba(self) -> Task:
        return Task(
            description=(
                "Read the user's goal and the dataset path: {dataset_path}. "
                "Skim the dataset schema (columns, dtypes, NA%) to validate alignment with objectives. "
                "Identify the likely ML task type(s) (e.g., classification, regression, time series). "
                "Produce a concise JSON spec capturing: objective, KPIs, target_candidate, task_type, "
                "assumptions, risks, acceptance_criteria, and explicit handoff items for EDA."
            ),
            expected_output="JSON spec + alignment notes for EDA (concise, structured).",
            agent=self.business_analyst(),
        )

    @task
    def t_eda(self) -> Task:
        return Task(
            description=(
                "Perform lightweight EDA on {dataset_path}: shape, schema, %missing, distributions, "
                "and simple correlations. Identify data quality issues (missing/outliers/duplicates). "
                "Persist any figures/reports/tables under ./artifacts and output their paths. "
                "Summarize key findings and provide explicit handoff items for data engineering."
            ),
            expected_output="EDA summary + data quality report + artifact paths for downstream use.",
            agent=self.data_explorer(),
            context=[self.t_ba()],
        )

    @task
    def t_prep(self) -> Task:
        return Task(
            description=(
                "Prepare training-ready data based on EDA findings: clean/transform, feature engineering, "
                "and create train/validation/test splits (stratify if required). "
                "Save all outputs (prepared datasets, encoders/scalers, feature list) to ./artifacts. "
                "Return the paths to these artifacts and a concise description of the final feature set."
            ),
            expected_output="Paths to prepared datasets + feature list + notes (all under ./artifacts).",
            agent=self.data_engineer(),
            context=[self.t_eda()],
        )

    @task
    def t_model(self) -> Task:
        return Task(
            description=(
                "Train and tune multiple candidate models using the prepared datasets. "
                "Compare models on validation metrics, select the best, and persist the model and "
                "preprocessing pipeline to ./artifacts. Provide a comparison table and selection rationale."
            ),
            expected_output="Model comparison table + best model path + selection rationale.",
            agent=self.model_builder(),
            context=[self.t_prep()],
        )

    @task
    def t_eval(self) -> Task:
        return Task(
            description=(
                "Load the best model and recompute metrics on the test set. "
                "Perform error and segment analysis; run basic robustness/fairness checks; "
                "and issue an ACCEPT/ITERATE verdict versus acceptance criteria."
            ),
            expected_output="Test metrics + analysis + ACCEPT/ITERATE verdict with justification.",
            agent=self.evaluator(),
            context=[self.t_model(), self.t_ba()],
        )

    @task
    def t_translate(self) -> Task:
        return Task(
            description=(
                "Translate the evaluated results into business language tied to KPIs. "
                "Highlight strengths, risks, and trade-offs, and propose a deployment & monitoring plan "
                "(including data drift checks and retraining cadence)."
            ),
            expected_output="Business-facing summary/report, ready to share with stakeholders.",
            agent=self.business_translator(),
            context=[self.t_eval(), self.t_ba()],
        )

    # Optional generic execution task (send a custom code snippet via inputs={'code': '...'}).
    @task
    def t_execute_code(self) -> Task:
        return Task(
            description=(
                "Execute the following Python code snippet. Ensure any files created are saved under ./artifacts. "
                "Return stdout, stderr, and list any generated file paths.\n\n"
                "```python\n{code}\n```"
            ),
            expected_output="JSON with returncode, stdout, stderr, and artifact paths if any.",
            agent=self.code_executor(),
        )

    # ============== CREW ==============

    @crew
    def crew(self) -> Crew:
        base_tasks = [
            self.t_ba(),
            self.t_eda(),
            self.t_prep(),
            self.t_model(),
            self.t_eval(),
            self.t_translate(),
        ]
        return Crew(
            agents=self.agents,
            tasks=base_tasks,          # <-- KHÔNG đưa self.t_execute_code() vào đây
            process=Process.hierarchical,
            manager_llm="gpt-4o",
            verbose=True,
        )