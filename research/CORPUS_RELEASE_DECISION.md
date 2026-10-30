# CORPUS_RELEASE_DECISION.md
# Corpus Freeze and Release Decision

**Date:** October 26, 2026  
**Repository:** `cross-lingual-rag-eval`  
**Decision Version:** v1.0  
**Based On:**  
- `research/CORPUS_QUALITY_AND_PROVENANCE_REPORT.md`  
- `research/QUERY_BENCHMARK_AUDIT.md`  
- `research/literature/paper_verification_candidates.csv`  
- `research/corpus_manifest_v1.csv`  
- `docs/FINAL_STUDY_PROTOCOL.md`

---

## RELEASE STATUS

> **BLOCKED BY PROVENANCE**

The corpus is technically sound (no broken chunks, no missing document IDs, no corrupt files, no FAISS index mismatches) and the query benchmark is structurally ready. However, the corpus **cannot be frozen for a publishable research study** until the source document provenance and licensing for the 6 active production documents are confirmed by the study author.

---

## Decision Rationale

### What is Ready

| Item | Status |
|---|---|
| FAISS vector index (180 vectors, 768-dim) | ✅ READY — consistent with all 16 document IDs and all 180 chunks |
| `data/processed/chunks.jsonl` (180 chunks) | ✅ READY — no empty, corrupt, or orphaned chunks |
| `data/processed/documents.jsonl` (16 documents) | ✅ READY — consistent with 8 source files |
| `data/queries/sample_queries.json` (50 queries / 150 variants) | ✅ READY — all IDs unique, all ground-truth doc IDs resolve in FAISS, all 3 language variants present |
| Preflight validator (`backend/experiments/preflight.py`) | ✅ READY — will catch any future index drift before each experiment run |
| Test suite (80/80 tests) | ✅ READY |
| `data/research_study.db` (clean, 0 rows) | ✅ READY for production experiment |

### What Blocks the Freeze

The following 6 active corpus documents have **UNVERIFIED** license and provenance status. Publishing results of a study that uses these documents as a retrieval corpus requires at minimum: (a) confirmation that documents are public disclosures or (b) a fair-use research exemption statement for each.

---

## Documents Requiring Manual Confirmation (Priority Order)

### 🔴 CRITICAL — Requires Immediate Confirmation

#### 1. `code_of_ethics.txt` vs. SBI Code of Ethics v3.0 PDF

**Issue:** The corpus contains `code_of_ethics.txt` (10,968 bytes; ingested into FAISS as 35 chunks). One of the uploaded PDFs — `media_1790169550043.pdf` (5.3 MB, 49 pages) — has been positively identified as the **State Bank of India Code of Ethics Version 3.0, dated April 21, 2026** (confirmed from PDF `/Title` metadata field and cover page text).

**What the user must confirm:**
- Is the `code_of_ethics.txt` file derived from SBI CoE v3.0 (this PDF), or from an earlier version?
- If this is v3.0: is the .txt a complete extraction, or was it truncated/edited?
- Is this document publicly available on SBI's website, or is it an internal document?

**Why this matters:** If the .txt is from an older version of the CoE but the study cites SBI's Code of Ethics, the citation version will be inaccurate. If there are content differences between versions, queries grounded in the .txt may not match the publicly citable document.

**Action:** Compare the first 500 characters of `code_of_ethics.txt` with the first page of the PDF to determine if versions match.

---

#### 2. `microfinance_loans_policy.txt` (SBI Microfinance Loans Policy v1.0, October 2022)

**Confirmation:** The uploaded PDF `media_1790169549340.pdf` (408 KB, 25 pages) has been positively identified as the source for `microfinance_loans_policy.txt`.

**PDF metadata:**
- Author: DEVENDRA K DWEVIDI
- Created: January 17, 2023 (Word for Microsoft 365)
- Organization: NBFC Alliances Department, ABU & GSS, Corporate Centre, Mumbai (SBI)
- Instructions updated up to: October 18, 2022

**What the user must confirm:**
- Is this document publicly available on SBI's official website or regulatory filings?
- Is reproducing excerpts of this policy in a research paper permitted under fair use / public interest exemption?
- Is the `.txt` file a complete or partial extraction of the 25-page policy?

---

#### 3. `digital_and_transaction_banking_products.txt` (SBI D&TB Marketing Booklet, 2022)

**Confirmation:** The uploaded PDF `media_1790169549261.pdf` (541 KB, 5 pages) has been positively identified as the source for `digital_and_transaction_banking_products.txt`.

**PDF metadata:**
- Author: D&TB Ma (Digital & Transaction Banking — Marketing Department, SBI)
- Created: February 3, 2022 (Microsoft Word 2013)
- Title (from `/Title` metadata): "DIGITAL & TRANSACTION BANKING PRODUCTS"

**What the user must confirm:**
- Is this a publicly distributed marketing booklet (e.g., available on SBI's website for corporate clients)?
- Is it a publicly available document that can be cited and reproduced in excerpts for non-commercial research?

---

### 🟡 MODERATE — Required Before Publication

#### 4. `ee9a3135_Impact Reporting of Green Bond of USD 250 Million.pdf`

**Likely Source:** State Bank of India Green Bond Impact Report. The filename prefix `ee9a3135` appears to be an internal document reference. Green bond impact reports are typically filed with international regulators (e.g., Climate Bonds Initiative) and are public disclosures.

**What the user must confirm:**
- Is this the official SBI Green Bond USD 250M Impact Report filed publicly?
- If yes, what is the URL of the public filing? (e.g., on SBI website, SEBI portal, or CBI registry)
- Is citation and excerpt use permitted for non-commercial academic research?

---

#### 5. `banking_faq.json`

**Status:** Source entirely unknown. The content describes banking procedures (UPI limits, debit card blocking, minimum balance) in clean, structured Q&A format. It reads as a specifically constructed dataset rather than a scraped document.

**What the user must confirm:**
- Was `banking_faq.json` created by the study author for this project? → If yes: eligible for use; state as "original dataset" in the paper.
- Or was it scraped from a specific bank's public FAQ page? → If yes: identify the bank and URL; confirm fair-use or permission.

---

#### 6. `telecom_customer_support.csv`

**Status:** Telecom operator completely unidentified. Content covers 5 support topics for an unnamed Indian telecom provider.

**What the user must confirm:**
- Was `telecom_customer_support.csv` created by the study author? → If yes: eligible; state as "original dataset."
- Or was it sourced from a public support page (e.g., Airtel, Jio, Vi)? → If yes: identify the provider and URL.

---

## Literature Citations Requiring Confirmation

The 5 PDFs uploaded as "research papers" (LIT-06 through LIT-10) have been forensically verified and **are NOT research papers**. They are:

| LIT ID | File | Actual Content | Action |
|---|---|---|---|
| LIT-06 | `media_1790093030893.pdf` | Student OS project report — Railway Reservation concurrency (24BRS1202 Anirudh Vijayan et al.) | **REMOVE from bibliography** — not a research paper |
| LIT-07 | `media_1790093040078.pdf` | **Exact duplicate of LIT-06** (SHA-256 identical) — same student report uploaded twice | **REMOVE from bibliography** — duplicate student report |
| LIT-08 | `media_1790169549261.pdf` | SBI Digital & Transaction Banking Products Booklet (2022) — already a corpus document | **RECLASSIFY as corpus source document** — cite as corpus document, not a research paper |
| LIT-09 | `media_1790169549340.pdf` | SBI Microfinance Loans Policy v1.0 (October 2022) — already a corpus document | **RECLASSIFY as corpus source document** — cite as corpus document, not a research paper |
| LIT-10 | `media_1790169550043.pdf` | SBI Code of Ethics v3.0 (April 2026) — source document for `code_of_ethics.txt` | **RECLASSIFY as corpus source document** — may represent a newer version than currently indexed |

> [!CAUTION]
> **No external research papers on code-mixed NLP, cross-lingual IR, or RAG evaluation were among the uploaded files.** The 5 literature placeholders (LIT-06 through LIT-10) in `research/literature/literature_matrix.csv` should be removed and replaced with actual research papers if they are available. The study currently has only 5 verified references (LIT-01 through LIT-05).

---

## Query Benchmark Decision

| Metric | Status |
|---|---|
| 50 unique question IDs | ✅ CONFIRMED |
| All 3 language variants present | ✅ CONFIRMED |
| All expected_document_ids in FAISS | ✅ CONFIRMED |
| No exact duplicate queries | ✅ CONFIRMED |
| Grounding check (sample) | ✅ CONFIRMED |
| Dataset structurally ready | ✅ **QUERY BENCHMARK IS READY** |

The query benchmark has no blocking issues. It may be used for the 300-run production study once the corpus provenance is resolved.

---

## Exact Next Actions Required (In Priority Order)

### Required Before ANY Publication

1. **[USER ACTION — CRITICAL]** Confirm whether `code_of_ethics.txt` matches SBI CoE v3.0 (the uploaded PDF) or an earlier version. If different versions, re-ingest the v3.0 PDF and rebuild the FAISS index.

2. **[USER ACTION — CRITICAL]** Confirm the source and license for `banking_faq.json` and `telecom_customer_support.csv` — are these original project creations or sourced documents?

3. **[USER ACTION — CRITICAL]** Remove LIT-06 and LIT-07 from the literature matrix — they are a student OS project report (uploaded twice), not a published research paper.

4. **[USER ACTION — CRITICAL]** Supply actual research papers for the "missing literature" gap identified in the Research Readiness Audit — specifically, papers on Code-Mixed NLP and Cross-Lingual IR. Current bibliography has only 5 entries (LIT-01 through LIT-05), which covers foundational RAG/embedding infrastructure but lacks code-mixing literature entirely.

5. **[USER ACTION — REQUIRED]** Confirm public availability and citation rights for the three SBI documents (`microfinance_loans_policy.txt`, `digital_and_transaction_banking_products.txt`, `ee9a3135_...pdf`). Add license/provenance notes to `research/licenses/`.

### Required Before Freezing Corpus v1

6. **[USER ACTION — REQUIRED]** Decide whether to update `code_of_ethics.txt` with SBI CoE v3.0 content from the uploaded PDF. If yes: re-ingest and rebuild FAISS index before running the 300-run experiment.

7. **[AUTOMATED — BEFORE EACH EXPERIMENT RUN]** Run preflight validator: `python scripts/run_experiment.py --preflight-only --db data/research_study.db` to confirm corpus hash consistency.

### Recommended Before Submission

8. Run cosine similarity check on the 50 English queries to detect semantic near-duplicates (threshold: similarity > 0.90).

9. Populate `ground_truth` and `source` fields for the 3 DEV-* queries that are missing them.

10. Add formal license note files to `research/licenses/` for each of the 6 active corpus documents.

---

## Summary Table

| Component | Status | Blocking? |
|---|---|---|
| FAISS index | ✅ Consistent | No |
| Chunks (180) | ✅ No empty/corrupt | No |
| Documents (16) | ✅ Consistent | No |
| Query benchmark (50 queries) | ✅ Ready | No |
| `data/research_study.db` | ✅ Clean (0 rows) | No |
| Test suite (80/80) | ✅ Passing | No |
| Corpus document licenses | ❌ All UNVERIFIED | **YES — blocks publication** |
| banking_faq.json provenance | ❌ Unknown | **YES — blocks publication** |
| telecom_customer_support.csv provenance | ❌ Unknown | **YES — blocks publication** |
| code_of_ethics.txt version vs. CoE v3.0 | ❌ Unresolved | **YES — may require re-ingestion** |
| Literature — code-mixing research papers | ❌ None present | **YES — blocks literature review** |
| LIT-06/07 (student report, not a paper) | ❌ Must be removed | **YES — blocks bibliography** |
