import json
#!/usr/bin/env python
import os, argparse
from typing import Optional
from pydantic import BaseModel, Field
from crewai.flow.flow import Flow, listen, start
from datetime import datetime
from dotenv import load_dotenv; load_dotenv()
# from src.utils.notebook_builder import build_notebook_from_jsonl

# Import crew defined in Crew.py
from src.auto_ds_agents.crew import CrispDMCrew 

# ====== State cho Flow ======
class CrispDMState(BaseModel):
    topic: str = ""
    user_request: str = ""
    dataset: str = ""
    run_ts: str = ""

    # Path for artifact files
    ba_path: str = "artifacts/ba_report.md"
    da_path: str = "artifacts/da_report.md"
    de_path: str = "artifacts/pipeline_design.md"
    ds_path: str = "artifacts/ds_report.md"

    # Artifacts content
    ba_report: Optional[str] = None
    da_report: Optional[str] = None
    de_report: Optional[str] = None
    ds_report: Optional[str] = None

    # Log/preview kickoff result
    kickoff_preview: Optional[str] = None


class CrispDMFlow(Flow[CrispDMState]):
    """Flow orchestration for CRIPS-DM with CrewAI"""

    @start()
    def get_user_input(self):
        """Read input from CLI flags instead of input() to avoid stdin being swallowed by Flow UI."""
        parser = argparse.ArgumentParser(description="CRISP-DM Flow (non-interactive)")
        parser.add_argument("--topic", required=True, help="Bind to {topic} in agents.yaml")
        parser.add_argument("--user_request", required=True, help="Business requirements/problems")
        parser.add_argument("--dataset", required=True, help="CSV dataset path")
        args, unknown = parser.parse_known_args()

        self.state.topic = args.topic.strip()
        self.state.user_request = args.user_request.strip()
        self.state.dataset = args.dataset.strip()
        self.state.run_ts = datetime.now().isoformat(timespec="seconds")

        # Check dataset file exists
        if not os.path.isfile(self.state.dataset):
            raise FileNotFoundError(f"Dataset not found: {os.path.abspath(self.state.dataset)}")

        # Prepare directories
        os.makedirs("artifacts", exist_ok=True)
        os.makedirs("output", exist_ok=True)

        print(
            f"\nStarting CRISP-DM run\n"
            f" • Topic       : {self.state.topic}\n"
            f" • UserRequest : {self.state.user_request}\n"
            f" • Dataset     : {os.path.abspath(self.state.dataset)}\n"
        )
        return self.state
    
    @listen("get_user_input") ## Run afer get_user_input
    def run_crispdm_crew(self, state: CrispDMState):
        """ Call crew.kickoff (Process.sequential + context chaining)"""
        print("Running CRISP-DM Crew...")

        inputs = {
            "topic": state.topic,
            "user_request": state.user_request,
            "dataset": state.dataset,
            "run_ts": state.run_ts
        }

        crew = CrispDMCrew().crew()
        result = crew.kickoff(inputs=inputs)

        # Save Preview
        try:
            s = str(result)
            state.kickoff_preview = s[:2000]
        except Exception:
            state.kickoff_preview = None
        print("Crew run completed.")
        return state
    
    @listen("run_crispdm_crew") ## Run afer run_crispdm_crew
    def collect_artifacts(self, state: CrispDMState):
        """ Collect artifacts from files """
        print("Collecting artifacts...")

        def read_file(path: str) -> Optional[str]:
            if os.path.isfile(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        return f.read()
                except Exception as e:
                    print(f"Error reading {path}: {e}")
                    return None
            else:
                print(f"Artifact not found: {path}")
                return None

        state.ba_report = read_file(state.ba_path)
        state.da_report = read_file(state.da_path)
        state.de_report = read_file(state.de_path)
        state.ds_report = read_file(state.ds_path)

        print("Artifacts collection completed.")
        return state
    
    @listen("collect_artifacts") ## Run afer collect_artifacts
    def complie_final_report(self, state: CrispDMState):
        """ Compile final report from collected artifacts """
        print("Compiling final report...")

        final_report_path = "artifacts/final_crispdm_report.md"
        with open(final_report_path, "w", encoding="utf-8") as f:
            f.write(f"# CRISP-DM Report\n")
            f.write(f"**Topic:** {state.topic}\n\n")
            f.write(f"**User Request:** {state.user_request}\n\n")
            f.write(f"**Dataset:** {os.path.abspath(state.dataset)}\n\n")
            f.write(f"**Run Timestamp:** {state.run_ts}\n\n")
            
            if state.ba_report: # If report is available in state.ba_report, write it, else write placeholder
                f.write("## Business Analysis Report\n")
                f.write(state.ba_report + "\n\n")
            else:
                f.write("## Business Analysis Report\n")
                f.write("_No report available._\n\n")

            if state.da_report:
                f.write("## Data Analysis Report\n")
                f.write(state.da_report + "\n\n")
            else:
                f.write("## Data Analysis Report\n")
                f.write("_No report available._\n\n")

            if state.de_report:
                f.write("## Data Engineering Pipeline Design\n")
                f.write(state.de_report + "\n\n")
            else:
                f.write("## Data Engineering Pipeline Design\n")
                f.write("_No report available._\n\n")

            if state.ds_report:
                f.write("## Data Science Report\n")
                f.write(state.ds_report + "\n\n")
            else:
                f.write("## Data Science Report\n")
                f.write("_No report available._\n\n")

        # print(f"Final report compiled: {final_report_path}")
        # try:
        #     nb_path = build_notebook_from_jsonl(
        #         log_path="artifacts/code_run_log.jsonl",
        #         out_path="artifacts/run_notebook.ipynb"
        #     )
        #     print(f"📓 Notebook created: {os.path.abspath(nb_path)}")
        # except Exception as e:
        #     print(f"[WARN] Could not build notebook: {e}")

        return state

# ====== Entrypoint ======
def kickoff():
    """Run the CRISP-DM flow"""
    CrispDMFlow().kickoff()
    print("\n=== Flow Complete ===")
    print("Your consolidated report is in the output directory.")
    print("Open output/final_report.md to view it.")

def plot():
    """Generate a visualization of the flow"""
    flow = CrispDMFlow()
    flow.plot("crispdm_flow")
    print("Flow visualization saved to crispdm_flow.html")

if __name__ == "__main__":
    kickoff()