# Auto-DS-Agents

**Auto-DS-Agents** is a modular, agent-based framework for automating end-to-end data science workflows.
It orchestrates specialized agents that handle different stages of the ML lifecycle—data cleaning, feature engineering, model selection, evaluation, and business action translation—making it easier to prototype and deploy automated data-driven solutions.

---

## 🚀 Features

* **Agent-Oriented Design**: Each task (e.g., cleaning, feature engineering, model selection) is handled by a dedicated agent.
* **Configurable Prompts**: YAML-based prompt files make it easy to customize agent behavior.
* **Data Pipeline Ready**: Built-in structure for raw and processed datasets.
* **Evaluation Support**: Automated evaluation to measure model performance.
* **Business Integration**: Converts results into business-oriented actions through a translator agent.
* **Test Coverage**: Includes unit tests for reliability.

---

## ⚙️ Installation

Follow these steps to set up the project:

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/auto-ds-agents.git
cd auto-ds-agents
```

### 2. Create a Conda Environment

```bash
conda create -n auto-ds-agents python=3.11 -y
conda activate auto-ds-agents
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Add your **OpenAI API Key** into the `.env` file:

```
OPENAI_API_KEY=your_api_key_here
```

---

## ▶️ Usage

1. **Set up environment variables** in `.env` (e.g., API keys if using LLMs).
2. **Prepare data** inside the `data/raw/` directory.
3. **Run the orchestrator**:

```bash
python src/auto_ds_agents/app.py
```

4. **Processed outputs** will be saved in `data/processed/`.

---

## 🧪 Testing

Run tests with:

```bash
pytest tests/
```

---

## 🔧 Customization

* Modify YAML prompt files in `prompts/` to adjust agent behaviors.
* Extend agents by adding new modules under `agents/`.
* Integrate with external tools by updating `utils/`.

---

## 🤝 Contributing

Contributions are welcome! Please fork the repo, create a branch, and open a pull request

### Contributors
- Monika Shakya  
- Van Thang Doan
- Yamuna G C  
- Linh Chi Tong  
- Szu-Yu Lin
- Duy Tung Nguyen

---

## 📜 License

This project is licensed under the MIT License.



