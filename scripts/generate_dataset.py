import json
import logging
import os
import sys
import re
from pathlib import Path

# Ensure project root is in python path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.config.logging import setup_logging
from backend.llm.groq_provider import GroqProvider

setup_logging()
logger = logging.getLogger("generate_dataset")

def extract_json(text):
    try:
        # Try finding markdown code block
        match = re.search(r"```(?:json)?(.*?)```", text, re.DOTALL)
        if match:
            return json.loads(match.group(1).strip())
        return json.loads(text.strip())
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON: {e}\nText was:\n{text}")
        return []

def main():
    docs_path = Path("data/processed/documents.jsonl")
    queries_path = Path("data/queries/sample_queries.json")
    
    if not docs_path.exists():
        logger.error("documents.jsonl not found. Run ingestion first.")
        return

    # Load documents
    banking_docs = []
    with open(docs_path, "r", encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            # Filter for the 3 new banking documents
            if doc["filename"] in [
                "digital_and_transaction_banking_products.txt",
                "microfinance_loans_policy.txt",
                "code_of_ethics.txt"
            ]:
                banking_docs.append(doc)

    logger.info(f"Found {len(banking_docs)} logical documents from the 3 new banking files.")

    llm = GroqProvider()
    
    generated_queries = []
    q_id_counter = 4  # Start from 4 since DEV-Q01 to DEV-Q03 exist

    # Group documents by filename
    from collections import defaultdict
    docs_by_file = defaultdict(list)
    for doc in banking_docs:
        docs_by_file[doc["filename"]].append(doc)

    system_prompt = """You are an expert dataset generator for a Cross-Lingual RAG evaluation framework.
You will be given a banking document text and its document ID.
Your task is to generate realistic, high-quality information needs (queries) based ONLY on the provided document text.

Requirements for each query:
1. "english": A natural English query.
2. "tamil_english": A natural Romanized Tamil-English (Tanglish) code-mixed query. Use informal, conversational phrasing (e.g. "foreign currency transfer panna enna documents venum?").
3. "hindi_english": A natural Romanized Hindi-English (Hinglish) code-mixed query. (e.g. "foreign currency transfer karne ke liye kaunse documents chahiye?").
4. "difficulty": Choose from "Easy", "Medium", "Hard".
   - Easy: direct fact retrieval.
   - Medium: paraphrased or requires semantic matching.
   - Hard: indirect, noisy, abbreviated, or heavily code-mixed.
5. "ground_truth": A short description of what the query expects.
6. "category": A short category name.

Output ONLY a JSON array of objects.
[
  {
    "english": "...",
    "tamil_english": "...",
    "hindi_english": "...",
    "difficulty": "Easy",
    "ground_truth": "...",
    "category": "..."
  }
]
"""

    for filename, docs in docs_by_file.items():
        logger.info(f"Processing {filename}...")
        
        # We want to generate ~15-16 questions per document file to reach ~47 total
        # We can pass the whole text of the document file, or chunk it.
        # Since groq has large context, we'll combine the text of all logical documents for this file.
        # But we need to assign exact expected_document_ids!
        # So it's better to pass one logical document at a time and ask for 2-3 questions.
        
        for doc in docs:
            prompt = f"Document ID: {doc['document_id']}\nText:\n{doc['text']}\n\nGenerate 4 diverse questions (mix of Easy, Medium, Hard) based on this text."
            
            try:
                response = llm.generate(prompt=prompt, system_prompt=system_prompt, temperature=0.7)
                parsed = extract_json(response)
                
                for item in parsed:
                    item["question_id"] = f"BANK-Q{q_id_counter:02d}"
                    item["domain"] = "Banking"
                    item["script_type"] = "Romanized"
                    item["expected_document_ids"] = [doc["document_id"]]
                    item["source"] = filename
                    generated_queries.append(item)
                    q_id_counter += 1
            except Exception as e:
                logger.error(f"Error generating for doc {doc['document_id']}: {e}")

    logger.info(f"Generated {len(generated_queries)} total queries.")

    # Load existing
    existing = []
    if queries_path.exists():
        with open(queries_path, "r", encoding="utf-8") as f:
            existing = json.load(f)

    # Combine
    combined = existing + generated_queries
    logger.info(f"Saving {len(combined)} total queries to {queries_path}")

    with open(queries_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
