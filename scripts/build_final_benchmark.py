"""
Builds versioned final benchmark (data/queries/final_queries_v1.json),
the human review sheet (research/HUMAN_QUERY_REVIEW_SHEET.csv),
the reviewer guidelines (research/HUMAN_QUERY_REVIEW_GUIDE.md),
and the blocker report (research/HUMAN_REVIEW_BLOCKERS.md).
"""
import json
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
QUERIES_IN = BASE_DIR / "data" / "queries" / "sample_queries.json"
CHUNKS_FILE = BASE_DIR / "data" / "processed" / "chunks.jsonl"
BENCHMARK_OUT = BASE_DIR / "data" / "queries" / "final_queries_v1.json"
REVIEW_SHEET_OUT = BASE_DIR / "research" / "HUMAN_QUERY_REVIEW_SHEET.csv"
REVIEW_GUIDE_OUT = BASE_DIR / "research" / "HUMAN_QUERY_REVIEW_GUIDE.md"
BLOCKERS_OUT = BASE_DIR / "research" / "HUMAN_REVIEW_BLOCKERS.md"

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
    with open(QUERIES_IN, "r", encoding="utf-8") as f:
        raw_queries = json.load(f)

    final_queries = []
    review_rows = [
        [
            "question_id", "language_variant", "query_text", "english_reference",
            "domain_category", "expected_document_ids", "gold_evidence_summary",
            "semantic_equivalence_1to5", "naturalness_1to5",
            "entity_and_constraint_preservation_yes_no", "language_correctness_yes_no",
            "decision_accept_revise_reject", "reviewer_id", "review_date", "reviewer_notes"
        ]
    ]

    for q in raw_queries:
        qid = q["question_id"]
        doc_ids = q.get("expected_document_ids", [])
        evidence_snippets = []
        for did in doc_ids:
            if did in chunks_by_doc and chunks_by_doc[did]:
                snippet = chunks_by_doc[did][0][:200].replace("\n", " ").strip()
                evidence_snippets.append(snippet)
        evidence_text = " | ".join(evidence_snippets) if evidence_snippets else "Refer to target document chunks"

        entry = {
            "question_id": qid,
            "english_query": q["english"],
            "tamil_english_query": q["tamil_english"],
            "hindi_english_query": q["hindi_english"],
            "source_provenance": "Authored for study; Romanized code-mixed variants; requires human bilingual review",
            "domain": q.get("domain", "General"),
            "category": q.get("category", "General"),
            "difficulty": q.get("difficulty", "Medium"),
            "expected_document_ids": doc_ids,
            "gold_supporting_evidence": evidence_text,
            "gold_answer": "Refer to target chunk for canonical answer",
            "status": "PENDING_HUMAN_BILINGUAL_REVIEW",
            "reviewer_1_decision": None,
            "reviewer_2_decision": None,
            "adjudication_decision": None,
            "comments": ""
        }
        final_queries.append(entry)

        # Row for Tamil-English
        review_rows.append([
            qid, "Tamil-English (Tanglish)", q["tamil_english"], q["english"],
            f"{q.get('domain')}: {q.get('category')}", ";".join(doc_ids), evidence_text[:120],
            "", "", "", "", "PENDING", "", "", ""
        ])
        # Row for Hindi-English
        review_rows.append([
            qid, "Hindi-English (Hinglish)", q["hindi_english"], q["english"],
            f"{q.get('domain')}: {q.get('category')}", ";".join(doc_ids), evidence_text[:120],
            "", "", "", "", "PENDING", "", "", ""
        ])

    with open(BENCHMARK_OUT, "w", encoding="utf-8") as f:
        json.dump(final_queries, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(final_queries)} benchmark queries to {BENCHMARK_OUT}")

    with open(REVIEW_SHEET_OUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(review_rows)
    print(f"Saved review sheet with {len(review_rows)-1} query review items to {REVIEW_SHEET_OUT}")

    # Guide
    guide_content = """# HUMAN_QUERY_REVIEW_GUIDE.md
# Bilingual Human Query Review Guidelines for Code-Mixed Benchmark

**Project:** Cross-Lingual RAG Faithfulness Evaluation under Code-Mixing  
**Benchmark Target:** `data/queries/final_queries_v1.json` (50 base information needs, 150 total queries)  
**Review Sheet:** `research/HUMAN_QUERY_REVIEW_SHEET.csv`

---

## 1. Overview & Objective

To prevent bias and synthetic artifacts, research integrity standards mandate that LLM-generated or uncurated code-mixed queries cannot be published as ground-truth evaluation benchmarks without independent verification by bilingual native speakers.

Each query in `data/queries/final_queries_v1.json` has an English reference, a Romanized Tamil-English (Tanglish) query, and a Romanized Hindi-English (Hinglish) query.

Two independent bilingual reviewers must evaluate each query variant, followed by adjudication if discrepancies occur.

---

## 2. Review Criteria & Scoring Scale

Reviewers must complete the following columns in `research/HUMAN_QUERY_REVIEW_SHEET.csv`:

### 1. Semantic Equivalence (1 to 5)
* **5 (Perfect):** The code-mixed query asks for the exact same information need as the English reference with no ambiguity.
* **4 (High):** Minor phrasing differences that do not alter the expected retrieved document or answer.
* **3 (Moderate):** Slight shift in nuance or specificity, but understandable in context.
* **2 (Poor):** Missing critical constraint or altering key facts (e.g., confusing "freeze card" with "cancel account").
* **1 (Unusable):** Incoherent, completely different question, or unintelligible translation.

### 2. Naturalness of Code-Mixing (1 to 5)
* **5 (Highly Natural):** Reflects authentic everyday conversational code-switching used by bilingual speakers in India (e.g., in chat apps, tech support, forums).
* **4 (Natural):** Fluent with minor stylistic stiffness.
* **3 (Acceptable):** Understandable, but contains mechanical or literal word-for-word transliteration.
* **2 (Unnatural):** Awkward grammatical hybrid or artificial code-switch placement.
* **1 (Nonsensical):** Completely unnatural or synthetic gibberish.

### 3. Entity & Constraint Preservation (Yes / No)
* Are named entities, specific products (e.g., YONO, Power Jyoti PUL, Green Notes, UPI), numerical values (e.g., 100,000 INR, 250 Million, 15 days), and technical terms preserved accurately?

### 4. Language Correctness (Yes / No)
* Is the query genuinely written in Romanized Tamil-English or Hindi-English (without improper Devanagari/Tamil script corruption, random punctuation, or invalid characters)?

### 5. Final Decision
* **ACCEPT:** Suitable for the gold evaluation benchmark as-is.
* **REVISE:** Minor spelling/grammatical fix needed (suggest fix in `reviewer_notes`).
* **REJECT:** Fundamentally flawed; replacement query required.

---

## 3. Adjudication Protocol

* If Reviewer 1 and Reviewer 2 both mark **ACCEPT**, the query status transitions to `VERIFIED_GOLD`.
* If either reviewer marks **REVISE** or **REJECT**, the lead researcher adjudicates the final text or replaces the query.
* The final production experiment (`Phase E`) may only be executed once all 50 information needs (100 code-mixed queries) are adjudicated and marked `VERIFIED_GOLD`.
"""
    with open(REVIEW_GUIDE_OUT, "w", encoding="utf-8") as f:
        f.write(guide_content)
    print(f"Saved review guide to {REVIEW_GUIDE_OUT}")

    # Blockers file
    blockers_content = f"""# HUMAN_REVIEW_BLOCKERS.md
# Human Bilingual Review Blockers

**Date:** October 27, 2026  
**Status:** `BLOCKED — HUMAN BILINGUAL REVIEW REQUIRED BEFORE PRODUCTION EXPERIMENT`  
**Protocol Requirement:** Under Phase C (Item 6) and Phase E (Item 1) of the study protocol, LLM-generated code-mixed queries cannot be used in the final production study without documented human bilingual verification.

---

## 1. Summary of Blocked Queries

* **Total Information Needs:** 50
* **Total Code-Mixed Queries Requiring Review:** 100
  - Romanized Tamil-English: 50
  - Romanized Hindi-English: 50
* **Completed Human Reviews:** 0 / 100
* **Pending Question IDs:** ALL (`DEV-Q01` through `DEV-Q03`, `BANK-Q04` through `BANK-Q50`)

---

## 2. Review Instructions for Researchers

1. Open `research/HUMAN_QUERY_REVIEW_SHEET.csv`.
2. Two bilingual reviewers must evaluate each row according to `research/HUMAN_QUERY_REVIEW_GUIDE.md`.
3. Fill in:
   - `semantic_equivalence_1to5`
   - `naturalness_1to5`
   - `entity_and_constraint_preservation_yes_no`
   - `language_correctness_yes_no`
   - `decision_accept_revise_reject`
   - `reviewer_id`
   - `review_date`
4. Once all rows are completed and adjudicated, update `data/queries/final_queries_v1.json` status to `VERIFIED_GOLD`.
5. Remove this blocker file to unlock Phase E (Production Experiment Execution).
"""
    with open(BLOCKERS_OUT, "w", encoding="utf-8") as f:
        f.write(blockers_content)
    print(f"Saved review blockers to {BLOCKERS_OUT}")

if __name__ == "__main__":
    main()
