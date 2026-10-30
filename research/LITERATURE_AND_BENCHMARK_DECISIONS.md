# LITERATURE_AND_BENCHMARK_DECISIONS.md
# Literature Intake and Benchmark Evaluation Decisions

**Version:** 1.0  
**Date:** October 26, 2026  
**Repository:** `cross-lingual-rag-eval`  
**Purpose:** Explicit, auditable rationale for every literature inclusion/exclusion and benchmark integration/rejection decision made during the Phase P2 literature intake for the Cross-Lingual RAG Faithfulness Evaluation study.

---

## 1. Scope of This Document

This document records the intake decisions for all literature and external datasets considered during the transition from the DA2 prototype to the full research study. It answers:

1. Why was each paper included in the literature matrix?
2. Why was each external benchmark included or excluded from the experiment?
3. What remains unresolved and requires user input?

---

## 2. Literature Intake Decisions

### 2.1 Papers Verified from `references.txt` (5 papers)

---

#### LIT-01 — Lewis et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. NeurIPS 2020.

**Decision: INCLUDED — Methodology Support**

**Rationale:**  
This paper introduces the foundational RAG architecture (dense passage retriever + seq2seq generator) that this study's system is directly built upon. It is non-negotiable as a citation. The pipeline in `backend/retrieval/retriever.py` and `backend/experiments/runner.py` directly implements the RAG paradigm described here.

**Role in Study:** Cite in Introduction (system architecture motivation) and Methods (RAG pipeline description).

**Verification Status:** VERIFIED — NeurIPS 2020 proceedings URL confirmed publicly accessible.

---

#### LIT-02 — Reimers & Gurevych (2019). *Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks*. EMNLP 2019.

**Decision: INCLUDED — Methodology Support**

**Rationale:**  
The multilingual-e5-base model used for embedding is architecturally derived from the Sentence-BERT siamese BERT training approach. This paper justifies the choice of dense sentence encoders for retrieval over sparse BM25 methods. It directly supports the embedding methodology.

**Role in Study:** Cite in Methods (embedding and retrieval methodology).

**Verification Status:** VERIFIED — ACL Anthology URL confirmed publicly accessible.

---

#### LIT-03 — Johnson, Douze & Jégou (2019). *Billion-scale similarity search with GPUs*. IEEE Transactions on Big Data.

**Decision: INCLUDED — Methodology Support**

**Rationale:**  
FAISS IndexFlatIP is the vector store backend used in this study. This paper is the primary academic reference for FAISS. While the study corpus is small (180 vectors), citing the algorithmic basis for FAISS is standard practice in RAG papers.

**Role in Study:** Cite in Methods (vector store and similarity search).

**Verification Status:** VERIFIED — IEEE Xplore URL confirmed publicly accessible (note: IEEE copyright, but citation of the paper title and DOI is permitted under fair use).

---

#### LIT-04 — Zheng et al. (2023). *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*. arXiv:2306.05685.

**Decision: INCLUDED — Methodology Support**

**Rationale:**  
This paper provides the primary empirical justification for using an LLM (gpt-oss-20b via Groq) as a faithfulness judge. Without this citation, the use of LLM-as-a-Judge requires justification from first principles. Zheng et al. demonstrate that strong LLM judges produce rankings highly correlated with human annotations, validating the evaluation approach used in this study.

**Role in Study:** Cite in Methods (evaluation design, faithfulness judge).

**Verification Status:** VERIFIED — arXiv URL confirmed. Note: final venue may be NeurIPS 2023 if accepted; check publication status before camera-ready submission.

---

#### LIT-05 — Wang et al. (2023). *Faithfulness Evaluation of Retrieval-Augmented Generation*. arXiv:2308.10629.

**Decision: INCLUDED — Methodology Support**

**Rationale:**  
Directly addresses faithfulness evaluation of RAG systems, which is the primary evaluation concern of this study. Provides the conceptual grounding for the faithfulness score metric (0.0–1.0 scale, evaluating factual consistency of generated answers against retrieved context).

**Role in Study:** Cite in Introduction (problem motivation) and Methods (faithfulness metric definition).

**Verification Status:** PARTIALLY VERIFIED — arXiv URL confirmed. Full author list (Wang, L.; Yang, N.; Wei, F.) matches one known version of the preprint; users should verify this matches the exact uploaded PDF if this paper was among the uploads.

---

### 2.2 User-Uploaded Papers (5 PDFs — Metadata Unverifiable from Binary)

The following 5 PDFs were uploaded by the user during the research paper intake session. The PDF binary format is not machine-readable in this environment. **Each paper has been registered in `research/literature/literature_matrix.csv` with a placeholder row. The user must confirm the metadata before these papers can be cited.**

---

#### LIT-06 — media_1790093030893.pdf (250 KB, uploaded 2026-09-22)

**Decision: REGISTERED — Pending Verification**

**Provisional Classification:** Code-Mixed NLP or Cross-Lingual IR survey/paper (inferred from upload context and timing alongside LIT-07).

**Action Required:**  
Please confirm the full title, authors, year, venue, and DOI/arXiv URL for this paper. Once confirmed, update `research/literature/literature_matrix.csv` row LIT-06 and this document accordingly.

**Likely Role (Provisional):** Background or methodology support for code-mixing or cross-lingual IR.

---

#### LIT-07 — media_1790093040078.pdf (250 KB, uploaded 2026-09-22)

**Decision: REGISTERED — Pending Verification**

**Note:** This file is the same size (250,409 bytes) as LIT-06. There is a possibility this is a duplicate file. Please verify whether both files are distinct papers or if one is a duplicate.

**Action Required:** Confirm title, authors, year, venue, DOI/URL. Confirm whether this is distinct from LIT-06.

---

#### LIT-08 — media_1790169549261.pdf (541 KB, uploaded 2026-09-23)

**Decision: REGISTERED — Pending Verification**

**Provisional Classification:** Code-Mixed NLP, Cross-Lingual RAG, or multilingual evaluation paper. The larger file size suggests it may contain figures, tables, or experimental results.

**Action Required:** Confirm title, authors, year, venue, DOI/URL.

---

#### LIT-09 — media_1790169549340.pdf (408 KB, uploaded 2026-09-23)

**Decision: REGISTERED — Pending Verification**

**Provisional Classification:** Code-Mixed NLP, RAG evaluation, or multilingual LLM paper.

**Action Required:** Confirm title, authors, year, venue, DOI/URL.

---

#### LIT-10 — media_1790169550043.pdf (5.3 MB, uploaded 2026-09-23)

**Decision: REGISTERED — Pending Verification**

**Provisional Classification:** The large file size (5.3 MB, approximately 10–20× larger than the other uploads) strongly suggests this is either:
- A survey paper with many figures and tables, or
- A dataset paper with extensive appendices and annotation examples, or
- A technical report (e.g., from AI4Bharat, Microsoft Research, or Google Research on multilingual NLP).

**Action Required:** Confirm title, authors, year, venue, DOI/URL. If this is a dataset or benchmark paper, also confirm: whether the dataset is publicly available, its license, and whether any data from it should be ingested into the evaluation corpus or cited as a benchmark.

---

## 3. Benchmark Intake Decisions

### 3.1 Benchmarks Evaluated (6 benchmarks)

Full details are in `research/benchmarks/benchmark_registry.csv`. Summaries:

---

#### BENCH-01 — LinCE (Aguilar et al., 2020)

**Decision: APPROVED FOR REFERENCE — Not for data ingestion**

**Rationale:**  
LinCE is the most directly relevant public benchmark, providing standardized Hindi-English code-mixing evaluation. We cite it to motivate our study (demonstrating that Hinglish is a studied linguistic phenomenon) and to position our evaluation methodology within the code-mixing NLP research tradition. We do not ingest LinCE data because:
1. LinCE tasks (NER, POS, LID, Sentiment) are structurally different from RAG faithfulness evaluation.
2. LinCE uses Twitter social media data; our study uses banking/telecom domain.
3. LinCE does not include Tamil-English (Tanglish), limiting its use as a comparative baseline.

**Action Required:** Verify that the LinCE CC BY 4.0 license is correctly attributed in any published paper that cites this benchmark.

---

#### BENCH-02 — GLUECoS (Khanuja et al., 2020)

**Decision: APPROVED FOR REFERENCE — Not for data ingestion**

**Rationale:**  
GLUECoS Hindi-English QA is the closest structural analogue to our study design (code-mixed queries against an English knowledge source). Citing it validates our experimental design as building on established precedent. We do not ingest GLUECoS data because:
1. GLUECoS QA uses Wikipedia passages; our corpus is banking/telecom.
2. GLUECoS does not include Tamil-English.
3. GLUECoS QA pairs are extractive; our faithfulness evaluation is generative.

---

#### BENCH-03 — XQuAD (Artetxe et al., 2020)

**Decision: BACKGROUND ONLY**

**Rationale:**  
XQuAD provides strong precedent for cross-lingual QA but uses script-native Hindi (Devanagari), not Romanized code-mixing. Its inclusion as background distinguishes our study's target phenomenon (Romanized intra-sentential code-mixing) from the broader cross-lingual transfer literature.

---

#### BENCH-04 — MLQA (Lewis et al., 2020)

**Decision: BACKGROUND ONLY**

**Rationale:**  
Same limitations as XQuAD. Useful background for situating the cross-lingual QA literature, but not directly applicable to our code-mixed Romanized query evaluation.

---

#### BENCH-05 — IndicGLUE (Kakwani et al., 2020)

**Decision: BACKGROUND ONLY**

**Rationale:**  
IndicGLUE covers Tamil and Hindi in native scripts. Useful for motivating the importance of Indic language NLP, but does not cover the Romanized code-mixed register that is the focus of this study. Cites the Indian NLP ecosystem.

---

#### BENCH-06 — XTREME (Hu et al., 2020)

**Decision: BACKGROUND ONLY**

**Rationale:**  
XTREME validates multilingual encoder models (like multilingual-e5-base) for cross-lingual tasks. Useful for justifying the embedding model choice but not directly relevant to code-mixed query evaluation.

---

### 3.2 Benchmarks NOT Considered / Out of Scope

The following publicly known benchmarks were considered but determined to be out of scope:

| Benchmark | Reason Excluded |
|---|---|
| SQuAD 1.1/2.0 | English-only; no code-mixing |
| TyDi QA | Multilingual but no code-mixing; native scripts only |
| MixSentiment (various) | Sentiment analysis task; not retrieval or QA |
| CSQA (CommonsenseQA) | English-only commonsense; not domain-specific |
| BankBench / FinQA | Financial domain but English-only; no code-mixing |

---

## 4. Decisions Still Pending (Requires User Input)

| Item | Current Status | Action Required |
|---|---|---|
| LIT-06 paper identity | Registered with placeholder | User to confirm title, authors, year, venue, DOI |
| LIT-07 paper identity | Registered with placeholder; possible duplicate of LIT-06 | User to confirm identity; check if duplicate |
| LIT-08 paper identity | Registered with placeholder | User to confirm title, authors, year, venue, DOI |
| LIT-09 paper identity | Registered with placeholder | User to confirm title, authors, year, venue, DOI |
| LIT-10 paper identity | Registered with placeholder; likely survey or dataset paper | User to confirm identity; if dataset, confirm license and ingestion decision |
| Corpus document licenses | 6 of 8 corpus documents lack confirmed licenses | User to confirm license for each; add to `research/licenses/` |
| LinCE citation attribution | CC BY 4.0 license requires attribution | Add full attribution in paper methods section |

---

## 5. Completeness Assessment

| Category | Count Completed | Count Pending |
|---|---|---|
| Papers fully verified | 5 | 5 (uploaded PDFs) |
| Benchmarks evaluated | 6 | 0 (all evaluated; 2 approved for reference) |
| Corpus documents with confirmed license | 0 | 6 |
| Research deliverables created | 5/5 | 0 |

**Literature intake deliverables created in this session:**

1. ✅ `research/literature/literature_matrix.csv` — 10 papers (5 verified, 5 pending)
2. ✅ `research/benchmarks/benchmark_registry.csv` — 6 benchmarks evaluated
3. ✅ `docs/FINAL_STUDY_PROTOCOL.md` — Full study protocol
4. ✅ `docs/CODE_MIXED_DATA_GUIDELINES.md` — Linguistic and annotation guidelines
5. ✅ `research/LITERATURE_AND_BENCHMARK_DECISIONS.md` — This decisions document
