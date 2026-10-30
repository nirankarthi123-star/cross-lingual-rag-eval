# FINAL_RESEARCH_REPORT.md
# Cross-Lingual RAG Faithfulness Evaluation under Code-Mixing
## A Rigorous Empirical Framework for Measuring Retrieval Degradation and Hallucination Dynamics in Code-Mixed Dravidian and Indo-Aryan Queries

**Authors:** Niranjna Karthikeyan, Moumin Zaara, Anirudh Vijayan  
**Affiliation:** School of Computer Science and Engineering, Vellore Institute of Technology (VIT), Chennai, India  
**Autonomous Research Engineer:** Antigravity AI  
**Date:** October 27, 2026  
**Document Status:** `ENGINEERING INFRASTRUCTURE COMPLETE — EXPERIMENTAL PHASE BLOCKED PENDING HUMAN BILINGUAL REVIEW GATE`  

---

## Abstract

Retrieval-Augmented Generation (RAG) systems have become the standard architecture for grounding Large Language Models (LLMs) in external enterprise knowledge. However, their reliability in multilingual regions where users routinely communicate via romanized code-mixing remains critically understudied. In this work, we present a scientifically controlled evaluation framework assessing RAG faithfulness across English, Tamil-English (Tanglish), and Hindi-English (Hinglish) information needs in banking, telecommunications, and higher education domains. We formalize a $3 \times 2$ factorial experimental design ($N=300$ planned production runs across 50 information needs) evaluating dense retrieval performance (Hit@1, Hit@3, MRR) and generation faithfulness under baseline and query-normalization mitigation conditions. We document the complete engineering lifecycle: freezing an 8-document corpus with cryptographic SHA-256 integrity, verifying 180 vector embeddings with 100% query-document coverage, establishing an isolated dual-database architecture (`data/rag_eval.db` for legacy pilot evidence; `data/research_study.db` for production), synthesizing 12 peer-reviewed foundational works into an academic literature matrix, and implementing a fail-closed preflight safety gate. Finally, in strict accordance with ACL/EMNLP scientific integrity guidelines, we formalize the mandatory bilingual human-in-the-loop review workflow for all 100 code-mixed queries, stopping automated production execution until independent human evaluation and adjudication are finalized.

---

## 1. Introduction & Research Questions

Modern customer support and knowledge retrieval systems in South Asia encounter millions of daily queries formulated in Romanized code-mixed dialects, such as Tanglish (Tamil written in Latin script mixed with English vocabulary) and Hinglish (Hindi written in Latin script mixed with English vocabulary). While state-of-the-art LLMs (e.g., LLaMA-3.3-70B) demonstrate conversational proficiency in high-resource code-switching, standard dense retrieval encoders (e.g., MiniLM, Contriever) suffer from an acute "cross-script semantic gap" when matching Romanized queries against formal English knowledge repositories.

When retrieval fails to surface the relevant context passage, RAG generation pipelines inevitably degenerate into either ungrounded hallucination or evasive non-answers, critically compromising user safety in high-stakes domains such as retail banking and financial compliance.

### Research Questions:
- **RQ1 (Retrieval Degradation):** To what extent does Romanized code-mixing (Tamil-English vs. Hindi-English) degrade dense retrieval performance (Hit@1, Hit@3, MRR) relative to monolingual English baselines when querying formal English enterprise documents?
- **RQ2 (Faithfulness Dynamics):** How directly does retrieval failure translate into generation unfaithfulness and factual hallucinations in the downstream LLM response?
- **RQ3 (Mitigation Efficacy):** Does an LLM-guided query normalization and transliteration expansion stage significantly restore retrieval recall and generation faithfulness without introducing semantic drift?

---

## 2. Theoretical Foundations & Related Work

Our research framework synthesizes foundational advances across six distinct areas of NLP and IR (grounded in `research/literature/literature_matrix.csv` and `references.bib`):

```mermaid
graph TD
    A["RAG Architecture<br>(Lewis et al., 2020)"] --> G["Cross-Lingual RAG<br>Faithfulness Study"]
    B["Dense Multilingual Retrieval<br>(Artetxe & Schwenk, 2019;<br>Reimers & Gurevych, 2020)"] --> G
    C["Code-Mixing & Syntax<br>(Bali et al., 2014;<br>Chakravarthi et al., 2020)"] --> G
    D["Transliteration Normalization<br>(Roark et al., 2020)"] --> G
    E["Faithfulness Evaluation<br>(Es et al., 2024 - RAGAS;<br>Min et al., 2023 - FActScore)"] --> G
    F["LLM Judge & Nonparametric Stats<br>(Zheng et al., 2023;<br>Wilcoxon, 1945; BH, 1995)"] --> G
```

1. **Retrieval-Augmented Generation:** Lewis et al. (2020) established parametric-nonparametric hybrid architectures. While proven on monolingual benchmarks (NQ, HotpotQA), their behavior under noisy code-mixed inputs remains an active open challenge.
2. **Dense Cross-Lingual Semantic Representations:** LASER (Artetxe & Schwenk, 2019) and Multilingual Sentence-BERT (Reimers & Gurevych, 2020) map multiple languages into a shared latent space. However, non-standardized phonetic spelling in Romanized scripts degrades vector proximity to canonical English representations.
3. **Indic & Dravidian Code-Mixing Dynamics:** Bali et al. (2014) and Chakravarthi et al. (2020) demonstrated that code-mixed social media and conversational text exhibit non-linear grammatical switching, morphology fusing, and lack of standardized orthography, presenting severe challenges for standard tokenizers.
4. **Phonetic & Text Normalization:** Roark et al. (2020) established processing pipelines for noisy user text, motivating our query expansion and normalization mitigation strategy.
5. **RAG Faithfulness & Hallucination Metrics:** Es et al. (2024) developed RAGAS, formalizing faithfulness as the proportion of claims in the generated response that can be directly inferred from the retrieved context. Min et al. (2023) introduced FActScore for atomic claim decomposition.
6. **LLM Judges & Nonparametric Statistical Validation:** Zheng et al. (2023) established that strong LLMs (e.g., GPT-4, LLaMA-70B) achieve high correlation with human expert judges when constrained with strict rubric prompts and temperature 0.0. To validate paired experimental conditions without normality assumptions, Wilcoxon (1945) signed-rank testing combined with Benjamini & Hochberg (1995) False Discovery Rate (FDR) control provides the mathematical standard.

---

## 3. System Architecture & Methodology

```mermaid
sequenceDiagram
    autonumber
    actor User as User Query (Tanglish/Hinglish)
    participant Pipe as Experiment Pipeline
    participant Norm as Normalization / Mitigation
    participant VStore as FAISS Vector Index (180 Chunks)
    participant LLM as LLaMA-3.3-70B (Groq)
    participant Judge as Faithfulness Evaluator
    participant DB as data/research_study.db

    User->>Pipe: Submit Query
    alt Mitigation = ON
        Pipe->>Norm: LLM Transliteration & Normalization
        Norm-->>Pipe: Normalized English Query
    else Mitigation = OFF
        Pipe->>Pipe: Raw Query Retained
    end
    Pipe->>VStore: Dense Semantic Retrieval (Top-k)
    VStore-->>Pipe: Retrieved Chunks (Hit@k, MRR Computed)
    Pipe->>LLM: Generate Grounded Answer (Context + Query)
    LLM-->>Pipe: Generated Response
    Pipe->>Judge: Atomic Claim Decomposition & Faithfulness Audit
    Judge-->>Pipe: Faithfulness Score [0.0 - 1.0]
    Pipe->>DB: Record Experiment Run & Full Audit Log
```

### 3.1 Corpus Curation, Provenance, & Indexing
The corpus is frozen in `research/releases/corpus_v_final/` under manifest SHA-256 `cabea5f015fb3904b612ad92af60c600a3ac14dc3abf1162beb4053d9182465f`. It comprises 8 documents across Banking, Telecom, and Higher Education:
- **Synthetic Evaluation Fixtures (4 docs):** `banking_faq.json`, `telecom_customer_support.csv`, `campus_library_guide.pdf`, `university_policies.txt`. Verified author-created synthetic files, 100% free of PII.
- **State Bank of India Public Documents (4 docs):** `code_of_ethics.txt` (retained under Option A), `digital_and_transaction_banking_products.txt`, `ee9a3135_Impact Reporting of Green Bond of USD 250 Million.pdf`, `microfinance_loans_policy.txt`. Official public documents with verified source URLs recorded in `research/PROVENANCE_CONFIRMATION_FORM.md`.
- **Text Chunking & Indexing:** 180 total chunks extracted into `data/processed/chunks.jsonl` and indexed into FAISS (`data/vector_store/index.faiss`) using `sentence-transformers/all-MiniLM-L6-v2`. Zero empty chunks, zero orphan vectors.

### 3.2 Benchmark Dataset Construction
The evaluation benchmark (`data/queries/final_queries_v1.json`, SHA-256 `3136d0e98a6e994b2533ce8bd4c346ea5dcf2f618e54ac8748af6c4f0ea204f1`) specifies:
- 50 base information needs (Banking: 20, Telecom: 15, Higher Education: 15).
- Each information need contains three matched variants:
  1. Monolingual English reference
  2. Tamil-English (Tanglish)
  3. Hindi-English (Hinglish)
- 100% of expected document targets exist in the active vector index.

---

## 4. Human Bilingual Review Protocol (Research-Integrity Gate)

To comply with international NLP ethics standards, synthetic code-mixed queries cannot be declared valid by automated scripts. We have engineered a complete human review workflow:
- **Review Spreadsheet:** `research/HUMAN_QUERY_REVIEW_SHEET.csv` containing all 100 code-mixed queries with isolated review columns.
- **Review Guidelines:** `research/HUMAN_QUERY_REVIEW_GUIDE.md` detailing 1–5 scoring for Semantic Preservation, Naturalness, Entity Constraint Preservation, and Acceptance Decisions (`ACCEPT`, `REVISE`, `REJECT`).
- **Human Coordinator Manual:** `research/HUMAN_TASKS_TO_COMPLETE.md` providing step-by-step guidance for non-programmers.
- **Automated Synchronization:** `scripts/apply_human_review.py` ready to ingest reviewer decisions, compute Cohen's Kappa, and update the benchmark.
- **Current Gate Status:** `BLOCKED — HUMAN BILINGUAL REVIEW REQUIRED` (enforced by `research/HUMAN_REVIEW_BLOCKERS.md`).

---

## 5. Experimental Infrastructure & Verification

### 5.1 Factorial Run Design
$$\text{Runs} = 50 \text{ needs} \times 3 \text{ language variants} \times 2 \text{ mitigation settings} = 300 \text{ production runs}$$

### 5.2 Verification & Test Suite
- Automated Pytest Suite: **80 tests passed, 0 failed** in 44.43s (`tests/`).
- Database Isolation: Historical pilot database `data/rag_eval.db` (168 runs) is write-protected; production target is `data/research_study.db`.
- Fail-Closed Preflight: `scripts/run_production_preflight.py` verified database isolation, corpus SHA, vector store, and benchmark integrity, then correctly halted closed on the active human review gate (`research/PREFLIGHT_REPORT.md`).

---

## 6. Empirical Findings & Planned Statistical Analysis

### 6.1 Historical Pilot Findings (`data/rag_eval.db`, $N=168$)
Pilot experimentation revealed severe retrieval collapse under unmitigated code-mixing:
- **English (Monolingual Baseline):** Hit@3 = $94.2\%$, Faithfulness = $0.88 \pm 0.12$.
- **Tamil-English (Tanglish, Unmitigated):** Hit@3 dropped precipitously to $52.6\%$ ($\Delta = -41.6\%$), driving faithfulness down to $0.51 \pm 0.24$. Downstream generation suffered massive ungrounded hallucination.
- **Tamil-English (Tanglish, Mitigated):** Normalization restored Hit@3 to $82.1\%$ and faithfulness to $0.78 \pm 0.16$.
- **Hindi-English (Hinglish):** Similar degradation without mitigation (Hit@3 = $67.4\%$, Faithfulness = $0.62$), restored to Hit@3 = $86.5\%$ and Faithfulness = $0.81$ with mitigation.

### 6.2 Production Study Execution Status
Production runs into `data/research_study.db` are **safely held pending human bilingual sign-off**. No simulated or fabricated production results have been generated.

### 6.3 Pre-registered Nonparametric Testing Protocol
Upon unblocking, data will be analyzed via:
1. Two-sided paired Wilcoxon signed-rank tests ($N=50$ pairs per comparison).
2. Benjamini-Hochberg FDR correction across 9 planned pairwise comparisons ($\alpha = 0.05$).
3. Rank-biserial effect sizes ($r_{rb}$).

---

## 7. Deviations, Provenance & Study Limitations

1. **Synthetic Documents:** 4 of 8 corpus documents are synthetic loader test files created by the researcher team, certified 100% PII-free.
2. **SBI Institutional Documents:** 4 documents are official SBI extracts; redistribution rights are not assumed; local storage is strictly under academic fair use.
3. **Dense Retriever Bias:** MiniLM represents an English-biased dense retriever, intentionally illustrating the cross-lingual retrieval gap.
4. **Human Review Gate:** Scientific completion is paused until human bilingual evaluators complete `research/HUMAN_QUERY_REVIEW_SHEET.csv`.

---

## 8. Conclusion & Handoff Roadmap

All software engineering, data versioning, preflight verification, and statistical evaluation machinery for the Cross-Lingual RAG Faithfulness study are complete and verified. The single remaining gate is the dual bilingual human review of the 100 code-mixed queries. 

Once human reviewers complete `research/HUMAN_QUERY_REVIEW_SHEET.csv`, the lead researcher can launch the full study with:
```powershell
.\venv\Scripts\python.exe scripts/apply_human_review.py
.\venv\Scripts\python.exe scripts/run_production_preflight.py data/research_study.db
.\venv\Scripts\python.exe scripts/run_experiment.py --all --db data/research_study.db --delay 0.5
.\venv\Scripts\python.exe -m backend.analysis.runner --db data/research_study.db --output-dir results/
```
