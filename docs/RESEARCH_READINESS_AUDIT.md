# Research-Readiness Audit Report: Cross-Lingual RAG Evaluation

**Date of Audit:** October 26, 2026  
**Repository:** `cross-lingual-rag-eval`  
**Location:** `C:\Users\NIRANJNA\.gemini\antigravity-ide\scratch\cross-lingual-rag-eval`  
**Purpose:** Comprehensive readiness assessment for transitioning from a DA2 course prototype to a rigorous academic research study.

---

## 1. Executive Summary & Crucial Research Context

This repository is transitioning from a university prototype (DA2 submission) to a full research study investigating the faithfulness and retrieval degradation of Retrieval-Augmented Generation (RAG) systems on intra-sententially code-mixed queries (English, Tamil-English [Tanglish], and Hindi-English [Hinglish]), along with an LLM-based query normalization mitigation strategy.

### Crucial Findings:
1. **The Existing 18-Run Pilot Cannot Support Research Conclusions:**
   The historical analysis artifacts in `results/analysis/` reflect only **18 completed runs across 3 dev queries** (`DEV-Q01`, `DEV-Q02`, `DEV-Q03`) across 6 conditions ($3 \times 6 = 18$). All 18 runs returned a faithfulness score of $1.0$ with zero variance ($\sigma = 0.0$). The Wilcoxon signed-rank test in `results/analysis/paired_comparisons.csv` explicitly notes `NOT TESTABLE: All paired differences are zero`. The claim in `success_criterion.csv` that the criterion was `MET` is an artifact of identical $1.0$ scores on 3 trivial queries, not valid empirical evidence.
2. **Corpus Version Drift:**
   The historical pilot was executed on an initial 5-file corpus (producing 23 chunks). Since the pilot, the corpus has been expanded with three substantial banking policy documents, bringing the active corpus to **8 source files, 16 parsed logical documents, and 180 indexed FAISS chunks**. The pilot results do not evaluate the current corpus.
3. **Partial & Failed Experiment State in Database:**
   The active SQLite database (`data/rag_eval.db`) contains **168 total execution rows**:
   - **101 successfully completed runs**
   - **67 failed runs** (caused by historical decommissioned model errors, missing API keys, and Groq API token-per-day rate limits)
   - **85 rows missing `recall_at_1`, `recall_at_3`, and `recall_at_5`** (because they predate the Recall@K schema migration)
   - Running statistical analysis on the raw database without filtering will contaminate final research findings.
4. **Secrets and Repository Hygiene:**
   `.env` is verified as **untracked** by git and covered by `.gitignore`. No secret keys are printed or committed. However, untracked binary files (e.g., `backend.zip`) and course documents (`DA2_Project_Report.docx`, `.pdf`) remain in the workspace.

---

## 2. Complete Inventory and Classification

### 2.1 Source Documents & Active Corpora
The repository currently contains **8 source document files** in `data/documents/`:

| Source File | File Type | File Size | Domain | Language | Role / Description |
|---|---|---|---|---|---|
| `banking_faq.json` | JSON | 2,169 B | Banking | English | 5 Q&A pairs on UPI limits, debit card freezing, minimum balance, wire transfers, zero liability. |
| `campus_library_guide.pdf` | PDF | 927 B | Academic | English | Central library borrowing rules and patron guidelines. |
| `code_of_ethics.txt` | TXT | 10,968 B | Banking / Ethics | English | Comprehensive banking business conduct and ethics manual. |
| `digital_and_transaction_banking_products.txt` | TXT | 4,720 B | Banking | English | Product guide for corporate and transaction banking portals. |
| `ee9a3135_Impact Reporting of Green Bond of USD 250 Million.pdf` | PDF | 676,583 B | Finance / ESG | English | State Bank of India Green Bond allocation and impact report. |
| `microfinance_loans_policy.txt` | TXT | 20,270 B | Banking / Credit | English | Credit policy, eligibility, SHG group lending, and recovery guidelines. |
| `telecom_customer_support.csv` | CSV | 1,367 B | Telecom | English | 5 customer support entries on roaming, eSIM, rollover, 5G, termination. |
| `university_policies.txt` | TXT | 2,301 B | Academic | English | Academic regulations, attendance, grading policies. |

### 2.2 Processed Documents, Chunks, and Vector Index
- **Logical Documents:** `data/processed/documents.jsonl` contains **16 logical documents** (JSON and CSV loaders explode individual records into separate logical document entries).
- **Text Chunks:** `data/processed/chunks.jsonl` contains **180 chunks** (configured at 500 characters, 100 character overlap).
  - Chunk distribution per document ranges from 1 chunk (for atomic FAQ items) up to 69 chunks (`ee9a3135_Impact Reporting...pdf`) and 37 chunks (`microfinance_loans_policy.txt`).
- **Vector Store:**
  - `data/vector_store/index.faiss`: 553,005 bytes. FAISS `IndexFlatIP` storing 180 vectors of dimension 768.
  - `data/vector_store/metadata_map.json`: 173,922 bytes. Maps 180 chunk IDs to source text, document ID, and chunk metadata.
- **Corpus Hash / Version Status:**
  - The vector index and processed files match the current 8 source files (last rebuilt September 23, 2026).
  - **Crucial Note:** There is no automated SHA-256 corpus hash check in `scripts/run_experiment.py` or `scripts/build_index.py` to prevent running experiments against an out-of-sync FAISS index.

### 2.3 Query Datasets
1. **Primary Dataset (`data/queries/sample_queries.json`):**
   - **50 base information needs** across Banking (45 queries) and Telecom (5 queries).
   - Each entry contains 3 language variants:
     - `english` (Pure English query)
     - `tamil_english` (Tanglish - Romanized intra-sentential code-mixed)
     - `hindi_english` (Hinglish - Romanized intra-sentential code-mixed)
   - Total evaluation queries: **150 query instances**.
   - Difficulty distribution: Easy (15), Medium (25), Hard (10).
   - Ground truth: All 50 queries have explicit `expected_document_ids` mapped to corpus chunks.
2. **Smoke Test Dataset (`data/queries/smoke_test_queries.json`):**
   - 1 test query (`SMOKE-Q01`) for pipeline sanity checks.

### 2.4 Experiment Records: Pilot vs. Current vs. Failed/Mock
The database `data/rag_eval.db` contains **168 execution rows** across table `experiment_results`:

| Category | Row Count | Question IDs Involved | Failure / Status Reason |
|---|---|---|---|
| **Historical Pilot Runs** | 18 | `DEV-Q01`, `DEV-Q02`, `DEV-Q03` | Successfully completed on historical 3-question corpus. |
| **New Completed Runs** | 83 | `BANK-Q04` through `BANK-Q37` | Successfully completed on expanded 50-question corpus. |
| **Old Decommissioned Model Errors** | 18 | `DEV-Q01`..`DEV-Q03` (Rows 4–21) | Failed with HTTP 400: `llama3-8b-8192` decommissioned on Groq. |
| **Missing API Key Failures** | 3 | `DEV-Q01`..`DEV-Q03` (Rows 1–3) | Failed: `GROQ_API_KEY` was not configured during early testing. |
| **API Rate Limit Failures (429)** | 46 | `BANK-Q05`..`BANK-Q50` | Failed: Groq 429 daily token limit hit during batch experiment run. |
| **Total Completed Rows** | **101** | Across all conditions | Stored in `experiment_results` with `completed_at NOT NULL`. |
| **Total Failed Rows** | **67** | Across all conditions | Stored in `experiment_results` with `error NOT NULL`. |
| **Null Recall@K Rows** | **85** | Older runs | Rows executed before Recall@K schema migration have `NULL` values. |

*Additional Test DB:* `data/smoke_test.db` contains 6 mock/test evaluation rows used strictly for unit testing.

### 2.5 Research Papers & Literature References
Currently, citations are recorded in a plain text file `references.txt`:
1. Lewis, P., et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. NeurIPS 2020.
2. Reimers, N., & Gurevych, I. (2019). *Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks*. EMNLP 2019.
3. Johnson, J., Douze, M., & Jégou, H. (2019). *Billion-scale similarity search with GPUs*. IEEE Big Data.
4. Zheng, L., et al. (2023). *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*. arXiv:2306.05685.
5. Wang, L., et al. (2023). *Faithfulness Evaluation of Retrieval-Augmented Generation*. arXiv:2308.10629.

*Missing Literature:* See Section 5 (`REQUIRES USER INPUT`). No comprehensive survey on Code-Mixed NLP or Cross-Lingual Information Retrieval is present in the repository.

### 2.6 Current Model & Configuration Settings

| Setting Name | `settings.py` (Active Code) | `docs/EXPERIMENT_CONFIGURATION.md` | `.env.example` | Discrepancy Flag |
|---|---|---|---|---|
| `EMBEDDING_MODEL` | `intfloat/multilingual-e5-base` | `intfloat/multilingual-e5-base` | `intfloat/multilingual-e5-base` | **Consistent** |
| `LLM_PROVIDER` | `groq` | `groq` | `groq` | **Consistent** |
| `LLM_MODEL` (Generator) | `openai/gpt-oss-20b` | `llama3-8b-8192` | `openai/gpt-oss-20b` | **MISMATCH:** `llama3-8b-8192` is decommissioned! |
| `JUDGE_LLM_MODEL` | `openai/gpt-oss-20b` | `llama-3.1-8b-instant` | `openai/gpt-oss-20b` | **MISMATCH:** Settings vs Docs disagree |
| `TOP_K` | 5 | 5 | 5 | **Consistent** |
| `HALLUCINATION_THRESHOLD` | 0.8 | 0.8 | 0.8 | **Consistent** |
| `DEFAULT_CHUNK_SIZE` | 500 | 500 | 500 | **Consistent** |
| `DEFAULT_CHUNK_OVERLAP` | 100 | 100 | 100 | **Consistent** |

### 2.7 Generated Artifacts & Course Reports
- `results/output.csv`: Raw export of historical experiment runs.
- `results/analysis/`: Contains analysis summary, chart data, condition summary, paired comparisons, and `phase10_summary.md` based strictly on the 18 pilot runs.
- `results/mock_analysis/`: Analysis output based on `data/smoke_test.db`.
- `DA2_Project_Report.docx` / `DA2_Project_Report.pdf` (177 KB): Written report submitted for coursework evaluation.
- `DA2_Review_Preparation_Guide.docx` (52 KB): Study guide for academic viva/review.
- `architecture_diagram` & `architecture_diagram.md`: System architectural documentation.

---

## 3. Comprehensive Discrepancy & Mismatch Audit

The following discrepancies were uncovered across code, documentation, datasets, and configurations:

### 3.1 Corpus & Chunk Count Mismatches
- **`README.md` (Line 51):** Claims the corpus consists of *"5 sample documents ... parsed into 12 documents and 23 chunks"*.
- **Reality:** There are **8 source documents**, parsed into **16 logical documents**, yielding **180 indexed chunks**.

### 3.2 Query Dataset Count Mismatches
- **`README.md` (Line 52):** Claims the dataset consists of *"3 information needs ... (9 total variants)"*.
- **`docs/QUERY_DATASET.md` (Line 6):** Recommends *"approximately 40–50 base questions"*.
- **Reality:** `data/queries/sample_queries.json` contains **50 base questions (150 query variants)**.

### 3.3 Model ID Conflicts
- `docs/EXPERIMENT_CONFIGURATION.md` specifies `llama3-8b-8192` as the Generator model and `llama-3.1-8b-instant` as the Judge.
- In reality, `llama3-8b-8192` was **decommissioned by Groq** (generating 18 HTTP 400 errors in the database).
- `backend/config/settings.py` sets `LLM_MODEL = "openai/gpt-oss-20b"` and `JUDGE_LLM_MODEL = "openai/gpt-oss-20b"`.
- The database historical pilot runs recorded `llama3-8b-8192`, whereas recent runs recorded `openai/gpt-oss-20b`. A publication-grade study must use a single, documented, actively supported model ID across all conditions.

### 3.4 Outdated Test Counts & Broken Assertions
- **`FINAL_VALIDATION.md` (Line 13):** Claims *"51/51 tests passing locally"*.
- **`README.md` (Line 43):** Claims *"67 automated Pytest tests"*.
- **Reality:** The repository contains **74 tests**.
- **Test Execution Result:** When run via `.\venv\Scripts\python -m pytest tests/ -v --tb=short`, the actual result is:
  ```
  ================== 5 failed, 69 passed, 3 warnings in 48.96s ==================
  ```
- **Root Cause of 5 Failures:**
  The 5 failing tests are in `tests/test_evaluation.py`:
  1. `test_judge_returns_fallback_on_invalid_json`
  2. `test_judge_returns_fallback_on_api_failure`
  3. `test_judge_fallback_when_score_unrecoverable`
  4. `test_judge_handles_empty_string_response`
  5. `test_judge_handles_whitespace_only_response`
  
  *Technical Reason:* A recent safety improvement updated `llm_judge.py` to return `faithfulness_score = None` when the LLM judge fails or returns an empty response (to avoid falsely penalizing a generation as a hallucination `0.0` when the judge API simply crashed). However, the test assertions in `tests/test_evaluation.py` were still expecting `result.faithfulness_score == 0.0`.

### 3.5 Stale CLI Commands in Documentation
- **`README.md` (Line 90):** Instructs the user to run `python scripts/run_ingestion.py`.
  - *Mismatch:* No file named `scripts/run_ingestion.py` exists! The actual script is `scripts/ingest_documents.py`.
- **`docs/QUERY_DATASET.md` (Line 32-33):** Instructs saving the dataset to `data/queries/final_dataset.json` and running `python scripts/validate_queries.py data/queries/final_dataset.json`.
  - *Mismatch:* The actual file in production is `data/queries/sample_queries.json`.

### 3.6 Dependency Declarations vs. Actual Code Imports
`requirements.txt` declares 12 dependencies:
`fastapi`, `uvicorn`, `pydantic`, `pydantic-settings`, `python-dotenv`, `httpx`, `pytest`, `pypdf`, `sentence-transformers`, `faiss-cpu`, `numpy`, `groq`.

*Missing from `requirements.txt`:*
1. **`scipy`**: Heavily imported in `backend/evaluation/analysis.py` (`from scipy.stats import wilcoxon`). While installed in the local `venv`, any new user or continuous integration (CI) environment installing strictly from `requirements.txt` will fail with `ModuleNotFoundError: No module named 'scipy'`.
2. **`python-docx` (`docx`)**: Imported in `scratch/generate_report.py` and `scratch/generate_da2_guide.py`.
3. **`graphviz`**: Imported in `scratch/generate_diagram.py`.

### 3.7 Contradiction Between Pilot Results and "Pending" Claims
- `FINAL_VALIDATION.md` claims: *"Status: Experiment pending. ... the corpus of 50 base questions across the 6 conditions has not yet been executed in production"*.
- Yet `results/analysis/` contains an analysis report claiming the success criterion was *"MET"* based on the 18 pilot runs.
- Meanwhile, the database actually contains 101 completed runs from the 50-question set. Documentation must clearly distinguish between the 18-run historical pilot, the interrupted 300-run expanded experiment, and the pending full research study.

---

## 4. Repository Hygiene & Secret Safety Check

### 4.1 Secret Exposure Verification
- `.env` Status: **NOT tracked by git**.
  - Verified via `git ls-files .env` (returns exit code 0, 0 lines tracked).
  - Size: 1,591 bytes.
  - Contains active API keys (`GROQ_API_KEY`).
  - No secret keys are printed or logged in this audit.
- `.gitignore` Status:
  - Properly includes `.env`, `*.env`, `venv/`, `*.db`, `data/vector_store/*`, `data/processed/*`.

### 4.2 Files That Must Never Be Committed or Shared
The following files exist in the repository and must be kept strictly local:
1. `.env`: Contains sensitive API credentials.
2. `venv/`: Local Python virtual environment (~thousands of files, OS-specific binaries).
3. `data/rag_eval.db` & `data/smoke_test.db`: Local SQLite databases containing run history and test data.
4. `backend.zip`: 180 KB untracked zip archive in the root directory.
5. `.pytest_cache/`, `__pycache__/`, `*.pyc`: Runtime caches.
6. `data/vector_store/index.faiss` & `data/vector_store/metadata_map.json`: Local FAISS binary index.

### 4.3 Safe Cleanup Recommendations (No Files Deleted)
1. **Add to `.gitignore`:**
   Add the following patterns to `.gitignore` to prevent accidental commits of binaries and archives:
   ```gitignore
   *.zip
   *.docx
   *.pdf
   scratch/
   ```
2. **Archive Coursework Artifacts:**
   Move `DA2_Project_Report.docx`, `DA2_Project_Report.pdf`, `DA2_Review_Preparation_Guide.docx`, and `backend.zip` into an `archive/da2_submission/` folder, or exclude them from git tracking.
3. **Pin Dependencies:**
   Export pinned versions including `scipy` into a clean `requirements.txt`:
   ```
   scipy>=1.13.0
   ```

---

## 5. Explicit Section: REQUIRES USER INPUT

The following items are missing from the repository, lack formal documentation, or require domain confirmation before a full research study can be published:

### 5.1 Survey Papers & Literature Grounding
*Status: Missing from repository.*
- **REQUIRES USER INPUT:** Provide the formal survey papers on **Code-Mixed Natural Language Processing** and **Cross-Lingual Information Retrieval** (e.g., surveys covering Hinglish/Tanglish NLP, query reformulation in low-resource environments, or RAG evaluation benchmarks).
- *Action Required:* Place the PDFs or list of DOI/ArXiv identifiers in the designated folder (see Section 7.4).

### 5.2 External Benchmark Datasets
*Status: Missing from repository.*
- **REQUIRES USER INPUT:** To establish external validity and avoid single-dataset bias, provide or designate standard code-mixed benchmarks (e.g., LinCE, GLUECoS, or public multilingual QA benchmarks).
- *Action Required:* If an external benchmark is to be used, specify whether the evaluation will run on public benchmarks in addition to the proprietary banking corpus.

### 5.3 Source Document Provenance & Licenses
*Status: Needs Verification.*
- **REQUIRES USER INPUT:** Clarify the license, provenance, and data-sharing rights for:
  1. `ee9a3135_Impact Reporting of Green Bond of USD 250 Million.pdf` (State Bank of India Green Bond report — public domain / corporate disclosure?).
  2. `microfinance_loans_policy.txt` (Internal bank policy vs. public regulatory guidelines?).
  3. `code_of_ethics.txt` (Public corporate policy vs. proprietary internal training document?).
  4. `digital_and_transaction_banking_products.txt` (Marketing booklet vs. internal operational documentation?).

### 5.4 Test Assertion Alignment Confirmation
*Status: Code logic updated, test assertions pending.*
- **REQUIRES USER INPUT:** Confirm whether the LLM judge should return `None` (recommended: separates API/infrastructure errors from hallucination) or `0.0` (legacy: treats judge timeout as hallucination) when an API failure occurs, so the 5 unit test assertions in `tests/test_evaluation.py` can be officially updated.

---

## 6. Research Readiness Summary: What is Ready vs. What Blocks

### 6.1 What Is Ready for Research
1. **RAG Architecture & Pipeline:**
   - Multi-format ingestion (PDF, CSV, JSON, TXT) is functional.
   - Dense retrieval using `intfloat/multilingual-e5-base` (768-dim) with FAISS is fully operational.
   - Two-pass heuristic Code-Mix Detector (Unicode + Romanized lexicon) is implemented and tested.
   - LLM Normalizer prompt and fallback mechanisms are in place.
2. **Evaluation Query Set:**
   - 50 base questions covering Banking and Telecom with grounded `expected_document_ids` and 3 balanced linguistic variants (150 total queries).
3. **Evaluation Metrics:**
   - LLM-as-a-Judge prompt, JSON parsing, regex score recovery, and empty-response protection.
   - Recall@1, Recall@3, and Recall@5 metric computation.
   - Paired statistical comparison module (Wilcoxon signed-rank test).
4. **Interactive Interfaces:**
   - Full FastAPI backend with live Chatbot and visual Evaluation Dashboard.

### 6.2 What Blocks a Full Research Conclusion
1. **Uncompleted Experiment Matrix:**
   - Only 101 of the required 300 runs (50 queries $\times$ 6 conditions = 300 runs) are completed in the current run sequence.
   - No statistical tests can be run on incomplete conditions (Hindi baseline, Hindi mitigated, and Tamil mitigated currently have only 3 completed runs each).
2. **Corpus & Result Version Contamination:**
   - The pilot results in `results/analysis/` represent an obsolete 3-query run on an old 23-chunk corpus and cannot be cited in the research paper.
   - The database contains mixed runs: historical pilot runs without Recall@K, decommissioned model rows, and partial runs from the expanded set.
3. **API Rate Limit Bottleneck:**
   - Groq API daily token limits (TPD) interrupt batch execution around run 108. A production study requires either higher-tier API quotas, a local model (e.g., via Ollama/vLLM), or staged multi-day batching.
4. **Missing Dependency in Declarations:**
   - `scipy` is missing from `requirements.txt`.
5. **Test Suite Failures:**
   - 5 unit tests are failing due to the `None` vs `0.0` assertion discrepancy.

---

## 7. Prioritized Action Checklist

### Phase P0: Core Research Integrity & Hygiene (Must Complete Before Any Experiment)
- [ ] **P0.1 Update `requirements.txt`:** Add `scipy>=1.13.0` so any clean environment can execute analysis scripts.
- [ ] **P0.2 Align Test Assertions:** Update the 5 failing tests in `tests/test_evaluation.py` to assert `result.faithfulness_score is None` on API failures. Verify 74/74 tests pass.
- [ ] **P0.3 Consolidate Model Configuration:** Standardize generator and judge model IDs across `settings.py`, `.env.example`, and `docs/EXPERIMENT_CONFIGURATION.md` (e.g., designate `llama-3.1-8b-instant` or `openai/gpt-oss-20b`).
- [ ] **P0.4 Database Partitioning:** Create a clean database file (e.g., `data/research_study.db`) for the full 300-run study to prevent mixing old pilot runs with publication data. Preserve `data/rag_eval.db` untouched as the pilot record.

### Phase P1: Documentation & Provenance Alignment
- [ ] **P1.1 Correct Stale Documentation:** Update `README.md` (fix command to `scripts/ingest_documents.py`, update corpus counts to 16 docs / 180 chunks, update query count to 50 queries / 150 variants).
- [ ] **P1.2 Document Document Provenance:** Fill in licenses and sources in `research/source_inventory.csv` based on user input.
- [ ] **P1.3 Update `FINAL_VALIDATION.md`:** Update test count from 51 to 74 and clarify pilot vs. production study status.

### Phase P2: Full Study Execution & Publication
- [ ] **P2.1 Ingest Survey Papers & External Benchmarks:** Place literature in `research/literature/`.
- [ ] **P2.2 Execute Full 300-Run Experiment:** Run `scripts/run_experiment.py --all` against the clean study database with proper rate-limit backoff.
- [ ] **P2.3 Run Statistical Analysis:** Run `scripts/analyze_results.py` to calculate Wilcoxon p-values, Recall@1/3/5 differences, and effect sizes on the completed $n=50$ dataset.

---

## 8. Designated Folders for User Literature & Datasets

To ensure strict file organization and reproducibility, please place your survey papers, external datasets, and provenance files in the following exact locations:

| Asset Type | Target Directory | Recommended File Naming Convention | Description |
|---|---|---|---|
| **Survey Papers (PDFs)** | `research/literature/` | `survey_[author]_[year]_[short_title].pdf` (e.g., `survey_sitaram_2019_codemixing_nlp.pdf`) | Full-text survey papers and background literature. |
| **BibTeX Citations** | `research/literature/references.bib` | `references.bib` | Formal BibTeX entries for all cited papers. |
| **External Benchmark Datasets** | `research/benchmarks/` | `benchmark_[name]_[split].json` (e.g., `benchmark_lince_tanglish_test.json`) | Standardized external validation datasets. |
| **Provenance & Licensing Notes** | `research/licenses/` | `license_[document_name].txt` (e.g., `license_sbi_green_bond.txt`) | Written terms of use, fair-use statements, or license text. |

*(The `research/` directory has been created in the project root to house these assets alongside `research/source_inventory.csv`).*
