# DEVIATIONS_AND_LIMITATIONS.md
# Cross-Lingual RAG Faithfulness Evaluation under Code-Mixing
## Formal Register of Provenance, Methodological Constraints, & Study Limitations

**Project:** Cross-Lingual RAG Faithfulness Evaluation under Code-Mixing  
**Date:** October 27, 2026  
**Institution:** VIT Chennai  
**Standard of Compliance:** Research Ethics & Scientific Reproducibility Guidelines  

---

## 1. Corpus Provenance & Intellectual Property Status

### 1.1 Synthetic Ingestion Fixtures
Four documents in the corpus were synthetically generated during early pipeline development (2026-09-09) to test ingestion loaders and edge-case chunking:
1. `data/documents/banking_faq.json` (JSON FAQ loader test)
2. `data/documents/telecom_customer_support.csv` (Tabular CSV loader test)
3. `data/documents/campus_library_guide.pdf` (Multi-page PDF extraction test)
4. `data/documents/university_policies.txt` (Unstructured plain-text test)

- **Authenticity Statement:** These four documents are author-created synthetic evaluation fixtures. They were not scraped or copied from any commercial bank, telecom provider, or university website.
- **Privacy & Sensitivity Audit:** Certified 100% free of Personally Identifiable Information (PII), proprietary customer records, or confidential student records.
- **Academic Limitation:** These documents serve solely as synthetic benchmark targets. They do not represent real-world enterprise manuals.

### 1.2 Official Enterprise & Public Documents (State Bank of India)
Four documents are extracts or official publications originating from State Bank of India (SBI):
1. `data/documents/code_of_ethics.txt` (Text extract of SBI Code of Ethics)
2. `data/documents/digital_and_transaction_banking_products.txt` (Product catalog extract)
3. `data/documents/ee9a3135_Impact Reporting of Green Bond of USD 250 Million.pdf` (Official SBI Green Bond Impact Report PDF)
4. `data/documents/microfinance_loans_policy.txt` (Policy excerpt)

- **Redistribution Rights:** Publicly accessible official institutional documents; redistribution rights are not assumed. Local retention is strictly limited to non-commercial academic research under fair-use evaluation principles.
- **Corpus Freeze Decision:** Under researcher freeze Option A (ratified October 27, 2026 in `research/PROVENANCE_CONFIRMATION_FORM.md`), `code_of_ethics.txt` is retained for corpus v1 consistency. Material differences against SBI Code of Ethics v3.0 PDF are documented in `research/CODE_OF_ETHICS_VERSION_COMPARISON.md`.

---

## 2. Benchmark Review & Human-in-the-Loop Gate Limitation

### 2.1 Current Pending Human Review
- The benchmark consists of 50 base information needs expanded into 150 query instances (50 English, 50 Tamil-English, 50 Hindi-English).
- The 100 code-mixed queries were synthesized during dataset construction.
- Under top-tier NLP venue standards (ACL/EMNLP), synthetic code-mixed test benchmarks must be validated by **two independent qualified native speakers**.
- **Current State:** As of October 27, 2026, dual human review is pending in `research/HUMAN_QUERY_REVIEW_SHEET.csv`.
- **Integrity Enforcement:** The production experiment is held in `BLOCKED` status. The autonomous agent has refused to fabricate human review scores or bypass the gate.

---

## 3. Methodological & Technical Limitations

### 3.1 Dense Embedding Cross-Lingual Gap
- The retrieval index utilizes `sentence-transformers/all-MiniLM-L6-v2`.
- While MiniLM is highly effective for monolingual English semantic search, it was not pre-trained extensively on Romanized Dravidian or Devanagari transliterations.
- *Methodological note:* This creates an intentional, ecologically valid stress test for RAG retrieval under code-mixing, reflecting real-world customer deployment challenges where specialized multilingual re-rankers are absent.

### 3.2 LLM-as-a-Judge Evaluation Bias
- Generation faithfulness is evaluated using an automated LLM judge (`llama-3.3-70b-versatile` via Groq) based on the RAGAS / MT-Bench framework.
- Automated judges may exhibit subtle position bias, length bias, or self-enhancement bias. To mitigate this, temperature is set to `0.0`, structured JSON reasoning is enforced, and all claims must cite verbatim chunk IDs.

### 3.3 Domain & Dialect Scope
- The benchmark covers three enterprise domains: Banking, Telecom, and Higher Education. Generalizability to healthcare, criminal justice, or creative domains cannot be inferred.
- Code-mixing is restricted to Romanized colloquial Tamil-English (Tanglish) and Hindi-English (Hinglish). Other Indic language families (e.g., Telugu-English, Malayalam-English, Bengali-English) or native script code-switching (e.g., Devanagari/Tamil script mixed with English words) are outside the current study scope.

---

## 4. Protocol Deviations

1. **Database Partitioning:** Historical exploratory runs (168 runs) were originally recorded in `data/rag_eval.db`. To guarantee zero contamination of the frozen 300-run production experiment, the protocol deviated from single-database storage by establishing an isolated target at `data/research_study.db`.
2. **Corpus Versioning:** The active corpus was frozen and mirrored into `research/releases/corpus_v_final/` with an immutable SHA-256 hash manifest, superseding ad-hoc root document modifications.
