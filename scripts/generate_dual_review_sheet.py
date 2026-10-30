"""
Generates the comprehensive dual-reviewer human query review sheet
research/HUMAN_QUERY_REVIEW_SHEET.csv with complete independent columns for
Reviewer 1, Reviewer 2, proposed revisions, and final adjudication.
"""
import json
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
QUERIES_FILE = BASE_DIR / "data" / "queries" / "sample_queries.json"
CHUNKS_FILE = BASE_DIR / "data" / "processed" / "chunks.jsonl"
REVIEW_SHEET = BASE_DIR / "research" / "HUMAN_QUERY_REVIEW_SHEET.csv"
BENCHMARK_JSON = BASE_DIR / "data" / "queries" / "final_queries_v1.json"

def load_chunks():
    chunks_by_doc = {}
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            c = json.loads(line)
            doc_id = c["document_id"]
            if doc_id not in chunks_by_doc:
                chunks_by_doc[doc_id] = []
            chunks_by_doc[doc_id].append(c["chunk_text"])
    return chunks_by_doc

def main():
    chunks_by_doc = load_chunks()
    with open(QUERIES_FILE, "r", encoding="utf-8") as f:
        queries = json.load(f)

    headers = [
        "question_id",
        "language_variant",
        "code_mixed_query",
        "english_reference_query",
        "domain",
        "category",
        "expected_document_ids",
        "gold_evidence_snippet",
        # Reviewer 1
        "reviewer_1_id",
        "reviewer_1_semantic_preservation_1to5",
        "reviewer_1_naturalness_1to5",
        "reviewer_1_entity_constraint_preservation",
        "reviewer_1_decision",
        "reviewer_1_proposed_revision",
        "reviewer_1_comments",
        # Reviewer 2
        "reviewer_2_id",
        "reviewer_2_semantic_preservation_1to5",
        "reviewer_2_naturalness_1to5",
        "reviewer_2_entity_constraint_preservation",
        "reviewer_2_decision",
        "reviewer_2_proposed_revision",
        "reviewer_2_comments",
        # Adjudication
        "adjudicator_id",
        "adjudication_decision",
        "final_approved_query_text",
        "adjudication_notes"
    ]

    rows = [headers]
    benchmark_records = []

    for q in queries:
        qid = q["question_id"]
        doc_ids = q.get("expected_document_ids", [])
        snippets = []
        for did in doc_ids:
            if did in chunks_by_doc and chunks_by_doc[did]:
                snippets.append(chunks_by_doc[did][0][:160].replace("\n", " ").strip())
        gold_snippet = " | ".join(snippets) if snippets else "Refer to target chunks"

        # Record for JSON benchmark
        benchmark_records.append({
            "question_id": qid,
            "domain": q.get("domain", "General"),
            "category": q.get("category", "General"),
            "difficulty": q.get("difficulty", "Medium"),
            "expected_document_ids": doc_ids,
            "gold_supporting_evidence": gold_snippet,
            "english": {
                "query": q["english"],
                "status": "CANONICAL_ENGLISH_REFERENCE"
            },
            "tamil_english": {
                "query": q["tamil_english"],
                "script_type": "Romanized",
                "status": "PENDING_HUMAN_BILINGUAL_REVIEW",
                "reviewer_1": {"decision": None, "id": None, "score": None, "notes": None},
                "reviewer_2": {"decision": None, "id": None, "score": None, "notes": None},
                "adjudication": {"status": "PENDING", "final_query": None, "adjudicator": None}
            },
            "hindi_english": {
                "query": q["hindi_english"],
                "script_type": "Romanized",
                "status": "PENDING_HUMAN_BILINGUAL_REVIEW",
                "reviewer_1": {"decision": None, "id": None, "score": None, "notes": None},
                "reviewer_2": {"decision": None, "id": None, "score": None, "notes": None},
                "adjudication": {"status": "PENDING", "final_query": None, "adjudicator": None}
            }
        })

        # Row for Tamil-English
        rows.append([
            qid,
            "Tamil-English (Tanglish)",
            q["tamil_english"],
            q["english"],
            q.get("domain", ""),
            q.get("category", ""),
            ";".join(doc_ids),
            gold_snippet,
            "", "", "", "", "PENDING", "", "",  # Reviewer 1 blank
            "", "", "", "", "PENDING", "", "",  # Reviewer 2 blank
            "", "PENDING", "", ""               # Adjudication blank
        ])

        # Row for Hindi-English
        rows.append([
            qid,
            "Hindi-English (Hinglish)",
            q["hindi_english"],
            q["english"],
            q.get("domain", ""),
            q.get("category", ""),
            ";".join(doc_ids),
            gold_snippet,
            "", "", "", "", "PENDING", "", "",  # Reviewer 1 blank
            "", "", "", "", "PENDING", "", "",  # Reviewer 2 blank
            "", "PENDING", "", ""               # Adjudication blank
        ])

    with open(REVIEW_SHEET, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    with open(BENCHMARK_JSON, "w", encoding="utf-8") as f:
        json.dump(benchmark_records, f, indent=2, ensure_ascii=False)

    print(f"Generated {len(rows)-1} review items in {REVIEW_SHEET}")
    print(f"Generated structured benchmark in {BENCHMARK_JSON}")

if __name__ == "__main__":
    main()
