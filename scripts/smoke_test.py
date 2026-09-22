import json
import os
import sys
import sqlite3
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.dataset.schemas import QueryRecord
from backend.experiments.matrix import generate_matrix
from backend.experiments.runner import ExperimentRunner
from backend.database.sqlite_client import SQLiteClient

# 1. Create a minimal smoke-test dataset
dataset_path = "data/queries/smoke_test_queries.json"
os.makedirs("data/queries", exist_ok=True)
smoke_records = [
    {
        "question_id": "SMOKE-Q01",
        "domain": "Banking",
        "english": "What are the requirements for a loan?",
        "tamil_english": "Loan requirements enna?",
        "hindi_english": "Loan requirements kya hai?",
        "script_type": "Romanized"
    }
]
with open(dataset_path, "w") as f:
    json.dump(smoke_records, f, indent=2)

query_records = [QueryRecord(**r) for r in smoke_records]

# 2. Run the 6 experimental conditions using mocks
db_path = "data/smoke_test.db"
if os.path.exists(db_path):
    os.remove(db_path)
db = SQLiteClient(db_path)

matrix = generate_matrix(query_records, dataset_path)

print(f"Matrix size: {len(matrix)}")

# Mock GroqProvider to not make real calls
class MockGroqProvider:
    def __init__(self, *args, **kwargs):
        self.model = "mock"
    def generate(self, prompt, system_prompt=None, **kwargs):
        if system_prompt and "translate and rewrite" in system_prompt:
            return "What are the requirements for a loan?"
        if system_prompt and "Evaluate the following answer" in system_prompt:
            return json.dumps({
                "faithfulness_score": 0.95,
                "hallucination_flag": False,
                "explanation": "Mock explanation"
            })
        return "You need a good credit score."

@patch('backend.llm.groq_provider.GroqProvider', MockGroqProvider)
def run_smoke_test():
    runner = ExperimentRunner(db=db)
    
    # We also need to patch out SentenceTransformer inside runner to be fast or just let it load (it loads fast on CPU).
    # Since we didn't patch it, it will load the model, which is fine.
    
    print("Running initial experiment...")
    results = runner.run_all(matrix, delay_between_runs=0)
    print(f"Completed initial runs: {len(results)}")
    
    print("Running experiment again to test resume logic...")
    results_resume = runner.run_all(matrix, delay_between_runs=0)
    print(f"Runs executed on resume (should be 0 actual, returning empty list or skipping): {len(results_resume)}")
    
    # Check rows in DB
    rows = db.get_all_experiment_results()
    print(f"Total rows in DB: {len(rows)} (Expected: 6)")
    
    # Check exports
    csv_path = "results/smoke_output.csv"
    json_path = "results/smoke_output.json"
    db.export_to_csv(csv_path)
    db.export_to_json(json_path)
    
    # Read back to verify
    with open(json_path) as f:
        json_data = json.load(f)
    print(f"Total rows in JSON export: {len(json_data)} (Expected: 6)")

if __name__ == "__main__":
    run_smoke_test()
    print("Smoke test completed.")
