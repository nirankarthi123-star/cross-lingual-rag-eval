# REPRODUCIBILITY_GUIDE.md
# Cross-Lingual RAG Faithfulness Evaluation under Code-Mixing
## Complete Reproduction Protocol, Environment Setup, & Execution Guide

**Project:** Cross-Lingual RAG Faithfulness Evaluation under Code-Mixing  
**Date:** October 27, 2026  
**Target Platform:** Windows 10/11 / POSIX-compatible environments  
**Python Runtime:** Python 3.11+ (Validated on Python 3.14)  

---

## 1. System Requirements & Environment Setup

### 1.1 Prerequisites
- Python 3.11 or later installed.
- Git installed.
- Valid Groq Cloud API key with access to `llama-3.3-70b-versatile`.

### 1.2 Virtual Environment Initialization
In PowerShell or terminal from the repository root:
```powershell
# Create virtual environment (if not already existing)
python -m venv venv

# Activate virtual environment
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On POSIX / Linux / macOS:
# source venv/bin/activate

# Upgrade pip and install pinned dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 1.3 Environment Variables
Configure your `.env` file in the repository root (do NOT commit this file):
```dotenv
GROQ_API_KEY=gsk_your_actual_groq_api_key_here
EMBEDDING_PROVIDER=sentence_transformers
DEFAULT_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
DEFAULT_GENERATION_MODEL=llama-3.3-70b-versatile
```

---

## 2. Artifact Versions & Cryptographic Hashes

To guarantee scientific immutability and provenance, verify all hashes before running:

| Artifact | Relative Path | Verified SHA-256 Checksum | Notes |
|---|---|---|---|
| **Corpus Manifest** | `research/releases/corpus_v_final/manifest.csv` | `cabea5f015fb3904b612ad92af60c600a3ac14dc3abf1162beb4053d9182465f` | Frozen 8-document corpus |
| **Corpus Hash Record** | `research/releases/corpus_v_final/manifest.sha256` | Matching manifest SHA-256 | Immutable check |
| **Benchmark Dataset** | `data/queries/final_queries_v1.json` | `3136d0e98a6e994b2533ce8bd4c346ea5dcf2f618e54ac8748af6c4f0ea204f1` | 50 base needs, 150 variants |
| **Processed Chunks** | `data/processed/chunks.jsonl` | Documented in manifest | 180 chunks |
| **Vector Index** | `data/vector_store/index.faiss` | Vector index file | 180 dense embeddings |
| **Historical Pilot DB** | `data/rag_eval.db` | Read-only pilot database | 168 rows (Protected) |
| **Production Target DB** | `data/research_study.db` | Production database | Clean target for 300 runs |

To verify hashes locally:
```powershell
.\venv\Scripts\python.exe -c "import hashlib; print(hashlib.sha256(open('research/releases/corpus_v_final/manifest.csv', 'rb').read()).hexdigest())"
```

---

## 3. Automated Test Suite

Before conducting any experimental operations, verify that all 80 unit and integration tests pass:
```powershell
.\venv\Scripts\python.exe -m pytest tests/
```
Expected output:
```text
======================= 80 passed, 3 warnings in ~40s =======================
```

---

## 4. Production Preflight Gate Check

The automated preflight script inspects all 6 critical gates (database isolation, corpus integrity, vector store, benchmark, human review, and run accounting). It runs in **fail-closed** mode.

```powershell
.\venv\Scripts\python.exe scripts/run_production_preflight.py data/research_study.db
```

### Current Preflight State:
- `Database Isolation`: **PASS**
- `Corpus Release Verification`: **PASS**
- `Vector Store & Chunk Integrity`: **PASS**
- `Benchmark Integrity`: **PASS**
- `Human Bilingual Review Gate`: **BLOCKED**
- `Run Accounting`: **PASS**

Preflight output is automatically written to `research/PREFLIGHT_REPORT.md`.

---

## 5. Human Bilingual Review Execution

Human reviewers must complete the review workflow as documented in `research/HUMAN_TASKS_TO_COMPLETE.md`:

1. **Complete Review Spreadsheet:**
   Reviewers 1 and 2 score the 100 queries in `research/HUMAN_QUERY_REVIEW_SHEET.csv`.
2. **Adjudicate Disagreements:**
   Lead researcher fills columns W–Z (`adjudication_decision`, `adjudicated_query_text`, `adjudication_notes`, `adjudicated_by`).
3. **Synchronize Benchmark:**
   Run the benchmark updater script:
   ```powershell
   .\venv\Scripts\python.exe scripts/apply_human_review.py
   ```
   This synchronizes approved queries into `data/queries/final_queries_v1.json` and outputs inter-annotator agreement statistics (Cohen's Kappa).
4. **Remove Human Review Blocker:**
   Once human review is complete, update `research/HUMAN_REVIEW_BLOCKERS.md` status to `CLEARED`.

---

## 6. Production Experiment Execution (Post-Review)

Once the human review blocker is cleared and preflight exits with `PASS`, launch the production study:

### 6.1 Dry-Run (Verification without API calls)
```powershell
.\venv\Scripts\python.exe scripts/run_experiment.py --all --dry-run --db data/research_study.db
```

### 6.2 Full 300-Run Production Execution
```powershell
.\venv\Scripts\python.exe scripts/run_experiment.py --all --db data/research_study.db --delay 0.5
```
This executes all 6 conditions:
- 50 information needs × 3 language variants (English, Tanglish, Hinglish) × 2 mitigation conditions (Off, On) = 300 runs.
- Inserts runs with full provenance, timestamps, retrieval metrics (Hit@1, Hit@3, MRR), generation outputs, and faithfulness scores into `data/research_study.db`.

---

## 7. Results Export and Statistical Analysis

### 7.1 Exporting Raw Results
```powershell
# Export all production runs to CSV
.\venv\Scripts\python.exe scripts/run_experiment.py --export-csv results/production_study_results.csv --db data/research_study.db

# Export all production runs to JSON
.\venv\Scripts\python.exe scripts/run_experiment.py --export-json results/production_study_results.json --db data/research_study.db
```

### 7.2 Running Statistical Evaluation
Run the analysis module to compute summary statistics, paired Wilcoxon signed-rank tests across language pairs and mitigation conditions, and Benjamini-Hochberg FDR adjustments:
```powershell
.\venv\Scripts\python.exe -m backend.analysis.runner --db data/research_study.db --output-dir results/
```
Outputs:
- Condition summary tables (faithfulness, Hit@1, Hit@3, MRR)
- Paired Wilcoxon test statistics and p-values
- Effect sizes (rank biserial correlation / Cliff's delta)
- Benjamini-Hochberg corrected p-values

---

## 8. Troubleshooting & Common Questions

1. **Why does preflight fail closed?**
   Preflight requires human bilingual review to be completed in `research/HUMAN_QUERY_REVIEW_SHEET.csv`. To maintain ACL/EMNLP research standards, AI agents are prohibited from inventing human review scores.
2. **Why can't I write to `data/rag_eval.db`?**
   `data/rag_eval.db` contains the 168-run historical pilot study. Overwriting it would corrupt pilot evidence. All production runs are isolated to `data/research_study.db`.
3. **What if a rate limit occurs during the 300 runs?**
   The runner features automatic exponential backoff (initial delay 0.5s, retrying up to 3 times). If stopped, the runner resumes idempotently by checking completed `run_id`s in SQLite.
