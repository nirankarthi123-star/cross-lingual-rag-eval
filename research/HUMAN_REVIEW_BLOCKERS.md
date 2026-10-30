# HUMAN_REVIEW_BLOCKERS.md
# Human Bilingual Review Blockers

**Last Machine Audit:** October 27, 2026 22:31 IST  
**Status:** `BLOCKED — HUMAN BILINGUAL REVIEW REQUIRED BEFORE PRODUCTION EXPERIMENT`  
**Protocol Requirement:** Under Phase C (Item 6) and Phase E (Item 1) of the study protocol, LLM-generated code-mixed queries cannot be used in the final production study without documented human bilingual verification.

---

## 1. Summary of Blocked Queries (Machine-Verified)

| Metric | Count |
|---|---|
| Total rows in HUMAN_QUERY_REVIEW_SHEET.csv | 100 |
| Reviewer 1 decisions filled | **0 / 100** |
| Reviewer 2 decisions filled | **0 / 100** |
| Adjudications filled | **0 / 100** |
| Unique Reviewer 1 IDs seen | **None** |
| Unique Reviewer 2 IDs seen | **None** |

Every row contains the literal placeholder `PENDING` — no human reviewer has entered any scores, IDs, decisions, or comments yet.

* **Total Code-Mixed Queries Requiring Review:** 100
  - Romanized Tamil-English: 50
  - Romanized Hindi-English: 50
* **Pending Question IDs:** ALL (`DEV-Q01` through `DEV-Q03`, `BANK-Q04` through `BANK-Q50`)

---

## 2. Review Instructions for Researchers

1. Open `research/HUMAN_QUERY_REVIEW_SHEET.csv` in Excel, LibreOffice Calc, or Google Sheets.
2. Two bilingual reviewers must evaluate each row **independently** according to `research/HUMAN_QUERY_REVIEW_GUIDE.md`.
3. Reviewer 1 fills columns **I through O**:
   - `reviewer_1_id` (e.g., REV-01)
   - `reviewer_1_semantic_preservation_1to5` (1–5)
   - `reviewer_1_naturalness_1to5` (1–5)
   - `reviewer_1_entity_constraint_preservation` (YES / NO)
   - `reviewer_1_decision` (ACCEPT / REVISE / REJECT)
   - `reviewer_1_proposed_revision` (only if REVISE)
   - `reviewer_1_comments`
4. Reviewer 2 fills columns **P through V** independently.
5. Lead researcher adjudicates any disagreements in columns **W through Z**:
   - `adjudicator_id`, `adjudication_decision`, `final_approved_query_text`, `adjudication_notes`
6. Once all 100 rows have decisions from both reviewers plus adjudication where needed, run:
   ```powershell
   .\venv\Scripts\python.exe scripts/apply_human_review.py
   ```
7. Update `data/queries/final_queries_v1.json` status to `VERIFIED_GOLD`.
8. Remove or update this blocker file to unlock Phase E (Production Experiment Execution).
