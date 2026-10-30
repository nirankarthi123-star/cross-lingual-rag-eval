# PREFLIGHT_REPORT.md
# Production Experiment Preflight Safety & Gate Report

**Date:** October 27, 2026  
**Target Database:** `data/research_study.db`  
**Overall Preflight Status:** `BLOCKED — PREFLIGHT FAILED CLOSED`  

---

## 1. Summary of Gate Checks

| Gate / Check Item | Status | Result / Findings |
|---|---|---|
| Database Isolation | ✅ PASS | Isolated research database validated at 'data/research_study.db' (legacy pilot protected). |
| Corpus Release Verification | ✅ PASS | Corpus release manifest verified (SHA-256: cabea5f015fb3904...). |
| Vector Store & Chunk Integrity | ✅ PASS | All 180 chunks and vectors verified (0 empty chunks, 0 orphan IDs). |
| Benchmark Integrity | ✅ PASS | All 50 information needs have verified target document IDs in the index. |
| Human Bilingual Review Gate | ⛔ BLOCKED | Research blocker active (HUMAN_REVIEW_BLOCKERS.md). 100 code-mixed queries pending dual human review. |
| Run Accounting (300-Run Design) | ✅ PASS | Matrix configuration validated: 50 base needs × 3 language variants × 2 conditions = exactly 300 runs. |

---

## 2. Gate Decision & Research Integrity Enforcement

> **VERDICT:** `EXECUTION FORBIDDEN BY SAFETY GATE`  

Under scientific integrity rules, production execution into the live Groq API cannot be launched until:
1. All 100 code-mixed queries are independently evaluated by two bilingual speakers in `research/HUMAN_QUERY_REVIEW_SHEET.csv`.
2. The lead researcher adjudicates any discrepancies and runs `python scripts/apply_human_review.py`.
3. This preflight report exits with `[PASS]` on all gates.

---

## 3. Resume Command (Post-Unblocking)

Once the human review blockers are cleared and preflight reports `PASS`:
```powershell
.\venv\Scripts\python.exe scripts/run_experiment.py --all --production --db data/research_study.db
```
