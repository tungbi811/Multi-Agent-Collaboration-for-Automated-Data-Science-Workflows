# run_crew.py
from configs.crew import CRISPDMCrew

if __name__ == "__main__":
    inputs = {"dataset_path": "./data/house_prices/house_prices_train.csv"}
    CRISPDMCrew().crew().kickoff(inputs=inputs)
