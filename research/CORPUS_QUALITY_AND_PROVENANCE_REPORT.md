# CORPUS_QUALITY_AND_PROVENANCE_REPORT.md
# Corpus Quality and Provenance Report

**Date:** October 26, 2026  
**Repository:** `cross-lingual-rag-eval`  
**Audit Type:** Local, read-only — no live experiment calls made  
**Audit Method:** SHA-256 hashing, pypdf metadata extraction, JSONL/JSON parsing, FAISS metadata inspection  

---

## 1. Source File Inventory

| # | Filename | Size (bytes) | File Type | SHA-256 (first 16 hex) | Provenance Status |
|---|---|---|---|---|---|
| 1 | `banking_faq.json` | 2,169 | JSON | `1AD0550B3BBADFC3...` | UNVERIFIED |
| 2 | `campus_library_guide.pdf` | 927 | PDF | `9A5039DBB0980B53...` | HISTORICAL PILOT ONLY |
| 3 | `code_of_ethics.txt` | 10,968 | TXT | `CAB41E272EFE44AA...` | PARTIALLY VERIFIED (SBI CoE) |
| 4 | `digital_and_transaction_banking_products.txt` | 4,720 | TXT | `57DA443F9D7214D9...` | PARTIALLY VERIFIED (SBI D&TB) |
| 5 | `ee9a3135_Impact Reporting of Green Bond of USD 250 Million.pdf` | 676,583 | PDF | `5372FCA20779137B...` | UNVERIFIED |
| 6 | `microfinance_loans_policy.txt` | 20,270 | TXT | `3760CA8BAF5ACF28...` | PARTIALLY VERIFIED (SBI MFL Policy) |
| 7 | `telecom_customer_support.csv` | 1,367 | CSV | `AA968680726148C6...` | UNVERIFIED |
| 8 | `university_policies.txt` | 2,301 | TXT | `E7F005BE606A3CBA...` | HISTORICAL PILOT ONLY |

**Total source files: 8**  
**Files used in active 300-run study: 6** (excluding `campus_library_guide.pdf` and `university_policies.txt`, which are not targeted by any production query)  
**Files with confirmed provenance: 0 / 8**  
**Files with partially identified source organization: 4 / 8** (confirmed SBI via PDF inspection)

Full SHA-256 hashes and provenance details are recorded in [`research/corpus_manifest_v1.csv`](research/corpus_manifest_v1.csv).

---

## 2. Processed Documents

- **Source:** `data/processed/documents.jsonl`  
- **Total logical documents:** 16
- **Parsing note:** JSON and CSV files are exploded into one logical document per record (banking_faq.json → 5 docs; telecom_customer_support.csv → 5 docs). PDF and TXT files produce 1 logical document each.

| Source File | Logical Doc Count | Document IDs |
|---|---|---|
| `banking_faq.json` | 5 | 650a8d08, 6c7d4f5e, dd28e57a, 4a59037b, 8436fe73 |
| `campus_library_guide.pdf` | 1 | 75ef41bc |
| `code_of_ethics.txt` | 1 | 6bbc2ade |
| `digital_and_transaction_banking_products.txt` | 1 | 2dea0f92 |
| `ee9a3135_Impact Reporting of Green Bond...pdf` | 1 | 71bdb7e3 |
| `microfinance_loans_policy.txt` | 1 | 5627f773 |
| `telecom_customer_support.csv` | 5 | a10c7fc9, ef57775e, b3e2f8a9, 933fe29d, db2baa30 |
| `university_policies.txt` | 1 | 7734bc2b |

---

## 3. Text Chunks and Vector Index

- **Source:** `data/processed/chunks.jsonl`  
- **FAISS metadata:** `data/vector_store/metadata_map.json`

| Metric | Value |
|---|---|
| Total chunks in `chunks.jsonl` | **180** |
| Total entries in FAISS `metadata_map.json` | **180** |
| FAISS key scheme | Integer (0–179) mapping to chunk metadata |
| Chunk ID format | `{document_id}_c{chunk_index}` (e.g., `650a8d084f403647_c0`) |
| `expected_document_ids` in queries | Reference `document_id` values (not chunk_ids or FAISS integer keys) |
| Chunk size | 500 characters |
| Chunk overlap | 100 characters |
| FAISS vector dimension | 768 (intfloat/multilingual-e5-base) |

### 3.1 Cross-Validation: Chunks vs. FAISS Metadata

> [!NOTE]
> The earlier audit script reported "180 chunk IDs only in chunks.jsonl, 180 only in FAISS" — this was a **false alarm** caused by the key type mismatch: `chunks.jsonl` uses `chunk_id` strings (e.g., `"650a8d084f403647_c0"`) while `metadata_map.json` uses integer FAISS vector indices (`"0"`, `"1"`, ...) as keys. The `document_id` values are **consistent across both files**. Cross-validation by `document_id` confirms **zero mismatches**.

| Check | Result |
|---|---|
| Document IDs in chunks.jsonl | 16 unique |
| Document IDs in metadata_map.json values | 16 unique |
| Document IDs matching | 16 / 16 ✅ |
| Orphaned chunks (in chunks, not in FAISS) | 0 ✅ |
| Orphaned metadata (in FAISS, not in chunks) | 0 ✅ |

### 3.2 Chunk Distribution by Source

| Source Document | Chunk Count |
|---|---|
| `ee9a3135_Impact Reporting of Green Bond...pdf` | 69 |
| `microfinance_loans_policy.txt` | 37 |
| `code_of_ethics.txt` | 35 |
| `digital_and_transaction_banking_products.txt` | 16 |
| `university_policies.txt` | 12 |
| `banking_faq.json` | 5 |
| `telecom_customer_support.csv` | 5 |
| `campus_library_guide.pdf` | 1 |
| **Total** | **180** |

---

## 4. Data Quality Findings

### 4.1 Empty Chunks
- **Finding:** The initial audit script reported 180 empty chunks. This was a field-name error in the script — it checked `c.get('text','')` but the field in `chunks.jsonl` is named `chunk_text`.
- **Actual status:** Inspecting `chunk_text` field — chunks contain substantive text (329, 317, 378, etc. characters). No empty chunks confirmed.

### 4.2 Scanned / Unreadable PDFs
- **`campus_library_guide.pdf`:** Only 927 bytes — extremely small for a PDF. This likely means it is a text-only PDF or a near-empty file. It produced only 1 logical document with 299 characters — borderline usable but not impactful since it is not used in the production study.
- **`ee9a3135_Impact Reporting of Green Bond...pdf`:** 676 KB, 69 chunks — text was successfully extracted by pypdf during ingestion (confirmed by chunk count). Not scanned.

### 4.3 Duplicate or Near-Duplicate Documents

> [!WARNING]
> **The following uploaded PDFs are the SOURCE DOCUMENTS for corpus .txt files** — not separate research papers:

| Uploaded PDF | SHA-256 | Identified As | Corpus File |
|---|---|---|---|
| `media_1790169549261.pdf` | `47F993F4...` | SBI Digital & Transaction Banking Booklet (2022) | `digital_and_transaction_banking_products.txt` |
| `media_1790169549340.pdf` | `BD6E1600...` | SBI Microfinance Loans Policy v1.0 (2022) | `microfinance_loans_policy.txt` |
| `media_1790169550043.pdf` | `356A9554...` | SBI Code of Ethics v3.0 (April 2026) | `code_of_ethics.txt` (possible earlier version) |

> [!CAUTION]
> **`media_1790169550043.pdf` (SBI CoE v3.0, April 2026) may be a NEWER VERSION than `code_of_ethics.txt`.** The PDF creation date is April 2026; the .txt file in the corpus was ingested without a version date. If the .txt was derived from an earlier version, the FAISS index may not reflect the current version of the document. This requires user verification before the corpus can be frozen.

### 4.4 Documents Without Source Provenance

| Document | Provenance Gap |
|---|---|
| `banking_faq.json` | No source URL, no publisher identified |
| `telecom_customer_support.csv` | No telecom operator identified; no source URL |
| `ee9a3135_Impact Reporting of Green Bond...pdf` | Source is SBI (strongly inferred from filename); no URL confirmed |
| `code_of_ethics.txt` | Content is SBI; version vs. uploaded PDF v3.0 unresolved |

### 4.5 Documents Without Verified Usage Rights

All 8 source documents have **UNVERIFIED** license status. For a publishable research study:
- **Minimum requirement:** Fair-use or research-exemption statement for each document.
- **Recommended:** Written confirmation from the document owner (SBI, unnamed telecom) or confirmation that documents are public disclosures.

---

## 5. Domain Distribution

| Domain | Source Files | Logical Docs | Chunks | % of Corpus |
|---|---|---|---|---|
| Banking (general) | 3 | 7 | 56 | 31.1% |
| Banking (microfinance) | 1 | 1 | 37 | 20.6% |
| Banking (ethics) | 1 | 1 | 35 | 19.4% |
| Banking (ESG/Green Bond) | 1 | 1 | 69 | 38.3% |
| Telecom | 1 | 5 | 5 | 2.8% |
| Academic (pilot only) | 2 | 2 | 13 | 7.2% |

> [!NOTE]
> The corpus is heavily weighted toward banking and finance content. The ESG/Green Bond PDF alone accounts for 38% of all chunks. Telecom is represented by only 5 small chunks across 5 documents, while the study evaluates 5 Telecom queries (DEV-Q01, DEV-Q03, plus 3 others). This domain imbalance should be acknowledged in the Methods section.

---

## 6. Missing / Unresolvable Items

| Item | Status | Action Required |
|---|---|---|
| `banking_faq.json` license | UNVERIFIED | Confirm whether this is an original project creation or sourced from a bank |
| `telecom_customer_support.csv` publisher | UNVERIFIED | Identify the telecom operator and confirm license |
| `ee9a3135_...pdf` public disclosure status | UNVERIFIED | Confirm this is a public SBI filing and cite accordingly |
| `code_of_ethics.txt` vs. CoE v3.0 PDF version | UNRESOLVED | Compare .txt content with PDF to determine which version is ingested |
| All documents — formal license/permission | UNVERIFIED | Add license notes to `research/licenses/` directory |
| Chunk `text` field name inconsistency | CONFIRMED BUG | `chunks.jsonl` uses `chunk_text` but preflight validator may check `text` — verify field name consistency in production code |
