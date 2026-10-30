"""
Synchronizes adjudicated human reviews from research/HUMAN_QUERY_REVIEW_SHEET.csv
into data/queries/final_queries_v1.json.
Enforces that every row is fully evaluated and adjudicated before unblocking.
"""
import csv
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
REVIEW_SHEET = BASE_DIR / "research" / "HUMAN_QUERY_REVIEW_SHEET.csv"
BENCHMARK_JSON = BASE_DIR / "data" / "queries" / "final_queries_v1.json"
BLOCKERS_FILE = BASE_DIR / "research" / "HUMAN_REVIEW_BLOCKERS.md"

def main():
    if not REVIEW_SHEET.exists():
        print(f"ERROR: Review sheet not found at {REVIEW_SHEET}")
        sys.exit(1)

    with open(REVIEW_SHEET, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        print("ERROR: Review sheet is empty.")
        sys.exit(1)

    # Validate completeness
    incomplete_rows = []
    agreement_matches = 0
    total_reviewed = 0

    for i, r in enumerate(rows, start=2):
        qid = r["question_id"]
        lang = r["language_variant"]
        r1_dec = r.get("reviewer_1_decision", "").strip().upper()
        r2_dec = r.get("reviewer_2_decision", "").strip().upper()
        adj_dec = r.get("adjudication_decision", "").strip().upper()
        final_text = r.get("final_approved_query_text", "").strip()

        # Check if reviewers completed their tasks
        if not r1_dec or r1_dec == "PENDING" or not r2_dec or r2_dec == "PENDING":
            incomplete_rows.append(f"Row {i} [{qid} - {lang}]: Reviewer decisions pending (R1='{r1_dec}', R2='{r2_dec}')")
            continue

        total_reviewed += 1
        if r1_dec == r2_dec:
            agreement_matches += 1

        # Check adjudication
        if not adj_dec or adj_dec == "PENDING":
            incomplete_rows.append(f"Row {i} [{qid} - {lang}]: Adjudication decision pending")
        elif not final_text:
            incomplete_rows.append(f"Row {i} [{qid} - {lang}]: Missing final_approved_query_text")

    if incomplete_rows:
        print(f"\n{'='*70}")
        print(f"[BLOCKED] Cannot synchronize benchmark: {len(incomplete_rows)} items incomplete!")
        print(f"{'='*70}")
        for err in incomplete_rows[:15]:
            print(f"  - {err}")
        if len(incomplete_rows) > 15:
            print(f"  ... and {len(incomplete_rows) - 15} more.")
        print("\nPlease have both bilingual reviewers and the adjudicator complete all fields.")
        sys.exit(1)

    # If all complete, update benchmark JSON
    with open(BENCHMARK_JSON, "r", encoding="utf-8") as f:
        benchmark = json.load(f)

    bench_by_id = {item["question_id"]: item for item in benchmark}

    for r in rows:
        qid = r["question_id"]
        lang = r["language_variant"]
        final_text = r["final_approved_query_text"].strip()
        item = bench_by_id[qid]

        if "Tamil" in lang:
            target = item["tamil_english"]
        else:
            target = item["hindi_english"]

        target["query"] = final_text
        target["status"] = "VERIFIED_GOLD"
        target["reviewer_1"] = {
            "id": r.get("reviewer_1_id"),
            "decision": r.get("reviewer_1_decision"),
            "semantic_score": r.get("reviewer_1_semantic_preservation_1to5"),
            "naturalness_score": r.get("reviewer_1_naturalness_1to5"),
            "notes": r.get("reviewer_1_comments")
        }
        target["reviewer_2"] = {
            "id": r.get("reviewer_2_id"),
            "decision": r.get("reviewer_2_decision"),
            "semantic_score": r.get("reviewer_2_semantic_preservation_1to5"),
            "naturalness_score": r.get("reviewer_2_naturalness_1to5"),
            "notes": r.get("reviewer_2_comments")
        }
        target["adjudication"] = {
            "status": "APPROVED",
            "decision": r.get("adjudication_decision"),
            "adjudicator": r.get("adjudicator_id"),
            "notes": r.get("adjudication_notes")
        }

    with open(BENCHMARK_JSON, "w", encoding="utf-8") as f:
        json.dump(benchmark, f, indent=2, ensure_ascii=False)

    # Remove blockers file
    if BLOCKERS_FILE.exists():
        BLOCKERS_FILE.unlink()

    pct_agreement = (agreement_matches / total_reviewed) * 100 if total_reviewed else 0.0
    print(f"\n[SUCCESS] Successfully synchronized 100 bilingual review items into {BENCHMARK_JSON}!")
    print(f"  Reviewer 1 vs Reviewer 2 Raw Agreement: {agreement_matches}/{total_reviewed} ({pct_agreement:.1f}%)")
    print(f"  All queries updated to status: VERIFIED_GOLD")
    print(f"  Blocker file removed: {BLOCKERS_FILE}")
    print("\nNext step: Run 'python scripts/run_production_preflight.py' to verify production readiness.")

if __name__ == "__main__":
    main()
