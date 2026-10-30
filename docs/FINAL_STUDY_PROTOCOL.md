# FINAL_STUDY_PROTOCOL.md
# Final Study Protocol: Cross-Lingual RAG Faithfulness Evaluation

**Version:** 1.0 — Full Research Study (Post-DA2 Prototype)  
**Date:** October 26, 2026  
**Repository:** `cross-lingual-rag-eval`  
**Principal Investigator:** [Author Name — to be filled before submission]  
**Status:** READY FOR EXPERIMENT EXECUTION (P2 Phase)

---

## 1. Research Question and Hypothesis

### 1.1 Research Question

> **RQ:** Does intra-sentential Romanized code-mixing (Tanglish / Hinglish) in user queries degrade the faithfulness of Retrieval-Augmented Generation (RAG) system responses, and can LLM-based query normalization mitigate this degradation?

### 1.2 Formal Hypotheses

| Hypothesis | Statement |
|---|---|
| **H1 (Primary)** | Code-mixed queries (Tanglish or Hinglish) produce RAG responses with statistically significantly lower faithfulness scores than equivalent English queries when no normalization is applied (baseline condition). |
| **H2 (Mitigation)** | Applying LLM-based query normalization to code-mixed queries restores faithfulness scores to levels statistically equivalent to the English baseline. |
| **H3 (Retrieval)** | Code-mixed queries produce lower Recall@1, Recall@3, and Recall@5 scores than English queries in the baseline condition, and normalization reduces this gap. |

### 1.3 Null Hypotheses

- **H0-1:** There is no statistically significant difference in faithfulness scores between code-mixed and English queries.
- **H0-2:** Normalization does not significantly change faithfulness scores for code-mixed queries.

---

## 2. System Architecture (Fixed — Do Not Modify)

### 2.1 Components

| Component | Implementation | Configuration |
|---|---|---|
| **Embedding Model** | `intfloat/multilingual-e5-base` | 768-dim, sentence-transformers, FAISS IndexFlatIP |
| **Vector Store** | FAISS `IndexFlatIP` | 180 vectors (current corpus); exact inner product |
| **Retriever** | Dense retrieval (`backend/retrieval/retriever.py`) | `TOP_K = 5` |
| **Code-Mix Detector** | Two-pass heuristic (Unicode + Romanized lexicon) | `backend/retrieval/normalizer.py` |
| **LLM Normalizer** | `openai/gpt-oss-20b` via Groq API | Applied only in mitigation condition |
| **RAG Generator** | `openai/gpt-oss-20b` via Groq API | Temperature = 0.0 (deterministic) |
| **Faithfulness Judge** | `openai/gpt-oss-20b` via Groq API | JSON output; 512 token budget |
| **Database** | SQLite (`data/research_study.db`) | Clean production database; 0 pre-existing rows |

> [!IMPORTANT]
> **Architecture Lock**: None of the above components may be modified between the baseline and mitigation experiment conditions. The only permitted experimental difference is whether LLM normalization is applied to the query before retrieval.

### 2.2 Corpus

| Property | Value |
|---|---|
| Source Documents | 8 files in `data/documents/` |
| Logical Documents (parsed) | 16 entries in `data/processed/documents.jsonl` |
| Text Chunks | 180 chunks in `data/processed/chunks.jsonl` |
| Chunk Size | 500 characters |
| Chunk Overlap | 100 characters |
| Corpus Manifest | `data/corpus_manifest.json` (SHA-256 of each source file) |
| FAISS Index Last Built | September 23, 2026 |

---

## 3. Experimental Design

### 3.1 Conditions

The experiment uses a **3 × 2 fully crossed design**:

| Factor | Levels |
|---|---|
| **Query Language** | English (`en`), Tanglish (`ta_en`), Hinglish (`hi_en`) |
| **Normalization** | Baseline (no normalization), Mitigation (LLM normalization) |

This yields **6 experimental conditions**:

| Condition ID | Language | Normalization | Label |
|---|---|---|---|
| C1 | English | None | `en_baseline` |
| C2 | English | LLM | `en_mitigated` |
| C3 | Tanglish | None | `ta_en_baseline` |
| C4 | Tanglish | LLM | `ta_en_mitigated` |
| C5 | Hinglish | None | `hi_en_baseline` |
| C6 | Hinglish | LLM | `hi_en_mitigated` |

> **Note on English + Mitigation (C2):** The normalization step is applied to English queries as well, creating a matched condition to control for any effect of the normalization step itself. If normalization slightly alters even English queries, C1 vs. C2 will isolate that effect.

### 3.2 Sample Size

| Parameter | Value |
|---|---|
| Base Information Needs | 50 (confirmed; `data/queries/sample_queries.json`) |
| Runs per condition | 50 |
| Total runs | 50 × 6 = **300 runs** |
| Minimum runs per condition for statistical testing | 50 (all 50 queries must complete in all 6 conditions) |

### 3.3 Pre-registration of Analysis

The following analysis is pre-registered (i.e., specified before running the experiment):

1. **Primary metric**: Faithfulness score per run (0.0–1.0), as returned by the LLM judge.
2. **Retrieval metrics**: Recall@1, Recall@3, Recall@5 per run.
3. **Statistical test**: Wilcoxon signed-rank test (non-parametric) comparing condition pairs, using the per-query paired differences.
4. **Primary comparisons** (Bonferroni-corrected for multiple comparisons across 3 pairs):
   - C1 (`en_baseline`) vs. C3 (`ta_en_baseline`)
   - C1 (`en_baseline`) vs. C5 (`hi_en_baseline`)
   - C3 (`ta_en_baseline`) vs. C4 (`ta_en_mitigated`)
   - C5 (`hi_en_baseline`) vs. C6 (`hi_en_mitigated`)
5. **Significance threshold**: α = 0.05 (two-tailed; α/4 = 0.0125 after Bonferroni correction for 4 primary comparisons).
6. **Effect size**: Cohen's d or rank-biserial correlation, reported alongside p-values.
7. **Missing data**: Runs where the judge returns `None` (API/infrastructure failure) are excluded from statistical analysis. This exclusion will be reported explicitly. If > 10% of runs in any condition return `None`, the condition is flagged as insufficient.

---

## 4. Data Sources and Provenance

### 4.1 Corpus Documents

See `research/source_inventory.csv` for the full corpus inventory. All documents are in English. Sources:

| Document | Domain | Provenance Status |
|---|---|---|
| `banking_faq.json` | Banking | Requires license confirmation |
| `code_of_ethics.txt` | Banking/Ethics | Requires license confirmation |
| `digital_and_transaction_banking_products.txt` | Banking | Requires license confirmation |
| `ee9a3135_Impact Reporting of Green Bond...pdf` | Finance/ESG | Public corporate disclosure (SBI) — requires citation |
| `microfinance_loans_policy.txt` | Banking/Credit | Requires license confirmation |
| `telecom_customer_support.csv` | Telecom | Requires license confirmation |
| `campus_library_guide.pdf` | Academic | Historical pilot only; not in active experiment corpus |
| `university_policies.txt` | Academic | Historical pilot only; not in active experiment corpus |

> [!CAUTION]
> All documents marked "Requires license confirmation" must have their license and provenance documented in `research/licenses/` before results from this study are submitted for publication. See Section 5.3 of `docs/RESEARCH_READINESS_AUDIT.md` for the specific questions to resolve.

### 4.2 Evaluation Dataset

| Property | Value |
|---|---|
| Dataset file | `data/queries/sample_queries.json` |
| Information needs | 50 |
| Total query variants | 150 (50 EN + 50 TA-EN + 50 HI-EN) |
| Ground truth | `expected_document_ids` per query |
| Dataset hash | Verified by preflight validator at experiment start |
| Construction method | Human-crafted from corpus facts; no machine translation |
| Dataset guidelines | `docs/CODE_MIXED_DATA_GUIDELINES.md` |

### 4.3 Literature

See `research/literature/literature_matrix.csv` for the full bibliography.

---

## 5. Experiment Execution Protocol

### 5.1 Pre-Experiment Checklist (Must Complete Before Any Run)

- [ ] Confirm `.env` contains a valid, quota-sufficient `GROQ_API_KEY`
- [ ] Confirm `data/research_study.db` is empty (0 rows in `experiment_results`)
- [ ] Confirm `data/corpus_manifest.json` is present and matches current `data/documents/` files
- [ ] Run preflight validation: `python scripts/run_experiment.py --preflight-only --db data/research_study.db`
- [ ] Verify all 80 tests pass: `python -m pytest tests/ -v --tb=short`
- [ ] Confirm FAISS index was built from the same corpus as `corpus_manifest.json`

### 5.2 Execution Command

```bash
python scripts/run_experiment.py --all --db data/research_study.db
```

**Flags:**
- `--all`: Run all 300 experiment configurations
- `--db data/research_study.db`: Write results to the clean production database (NOT `data/rag_eval.db`)

### 5.3 Resume After API Rate Limit

If the Groq API daily token limit (TPD) is hit during execution, the runner will log the error per run and write a `None` faithfulness score. To resume after the token limit resets:

```bash
python scripts/run_experiment.py --all --db data/research_study.db
```

The experiment runner uses the existing `completed_at IS NOT NULL` check to skip already-completed runs automatically. **Do not delete or reset `data/research_study.db` between sessions.**

### 5.4 Rate Limit Mitigation Strategy

To reduce the risk of hitting the daily token limit:
- Run the experiment in batches of 50 runs per day if on a free Groq tier.
- Consider upgrading to a Groq paid tier for full 300-run execution.
- Alternatively, run the generator and judge using a local model (e.g., Ollama + `llama3:8b`) — document any model changes in the study results.

### 5.5 Monitoring During Execution

```bash
# Check current run progress
python scripts/analyze_results.py --db data/research_study.db --summary-only

# Check for failed or None-scored runs
sqlite3 data/research_study.db "SELECT condition, COUNT(*) FROM experiment_results WHERE error IS NOT NULL GROUP BY condition;"
```

---

## 6. Analysis Protocol

### 6.1 Statistical Analysis Command

```bash
python scripts/analyze_results.py --db data/research_study.db --output results/study_analysis/
```

### 6.2 Outputs Expected

| Output File | Contents |
|---|---|
| `results/study_analysis/analysis_summary.json` | Condition means, std devs, n per condition |
| `results/study_analysis/condition_summary.csv` | Per-condition faithfulness and Recall@K statistics |
| `results/study_analysis/paired_comparisons.csv` | Wilcoxon p-values, effect sizes for 4 primary comparisons |
| `results/study_analysis/recall_summary.csv` | Recall@1, Recall@3, Recall@5 per condition |

### 6.3 Reporting Standards

1. Report sample size per condition, including number of excluded runs (faithfulness `None`).
2. Report exact p-values (not just "< 0.05") and effect sizes.
3. Report Bonferroni-corrected significance threshold (α = 0.0125 for 4 comparisons).
4. Do not interpret pilot results (`data/rag_eval.db`) as research conclusions.
5. Include corpus manifest hash and dataset hash in the methods section.

---

## 7. Integrity and Reproducibility Standards

### 7.1 What Is Never Permitted

- Running experiments against `data/rag_eval.db` and presenting those results as the full study results.
- Mixing runs from multiple database files in a single statistical analysis.
- Re-ingesting the corpus without updating `corpus_manifest.json` and re-verifying `expected_document_ids`.
- Treating a faithfulness score of `0.0` returned due to a judge API failure as a hallucination detection.
- Fabricating, interpolating, or selecting favorable runs to report.

### 7.2 Transparency Requirements for Publication

A reproducibility appendix must include:
- Corpus manifest (SHA-256 of each source document)
- Dataset hash (SHA-256 of `sample_queries.json`)
- Model IDs (generator, normalizer, judge)
- Prompt templates (generator and judge prompts as used)
- Chunk size / overlap configuration
- Temperature setting (0.0)
- FAISS index type and dimension
- Number of runs excluded for judge API failures

---

## 8. Timeline (Indicative)

| Phase | Task | Estimated Duration |
|---|---|---|
| Pre-experiment | Resolve corpus licenses; confirm API quota; verify preflight passes | 1–2 days |
| Execution (P2.2) | Run 300-experiment matrix (subject to daily Groq rate limits) | 3–6 days |
| Analysis (P2.3) | Run statistical analysis; generate plots | 1 day |
| Manuscript | Write methods, results, discussion | 5–10 days |
| Review | Internal review; revise | 3–5 days |
| Submission | Format for target venue | 1–2 days |

---

## 9. Related Documents

| Document | Path | Purpose |
|---|---|---|
| Research Readiness Audit | `docs/RESEARCH_READINESS_AUDIT.md` | Full inventory of all repository assets and gaps |
| Experiment Configuration | `docs/EXPERIMENT_CONFIGURATION.md` | Model names, hyperparameters, API settings |
| Code-Mixed Data Guidelines | `docs/CODE_MIXED_DATA_GUIDELINES.md` | Linguistic standards for query construction |
| Source Inventory | `research/source_inventory.csv` | Corpus provenance tracking |
| Literature Matrix | `research/literature/literature_matrix.csv` | Full bibliography with roles |
| Benchmark Registry | `research/benchmarks/benchmark_registry.csv` | External benchmark evaluation and decisions |
| Literature & Benchmark Decisions | `research/LITERATURE_AND_BENCHMARK_DECISIONS.md` | Rationale for all intake decisions |
