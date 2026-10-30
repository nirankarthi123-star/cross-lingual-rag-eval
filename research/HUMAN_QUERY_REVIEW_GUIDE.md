# HUMAN_QUERY_REVIEW_GUIDE.md
# Bilingual Human Query Review Guidelines & Protocol

**Project:** Cross-Lingual RAG Faithfulness Evaluation under Code-Mixing  
**Benchmark Target:** `data/queries/final_queries_v1.json` (50 Information Needs / 100 Code-Mixed Evaluation Variants)  
**Active Review Instrument:** `research/HUMAN_QUERY_REVIEW_SHEET.csv`  
**Protocol Requirement:** Mandatory research-integrity gate. LLM-generated or uncurated code-mixed queries must NOT be used for production research experiments without documented verification by qualified human bilingual speakers.

---

## 1. Reviewer Qualifications & Roles

1. **Reviewer 1 (Tamil-English or Hindi-English Native/Bilingual Speaker):**
   - Independent evaluation of semantic fidelity and conversational code-mixing naturalness.
   - Evaluates odd-numbered query rows for their assigned language.
2. **Reviewer 2 (Second Independent Bilingual Speaker):**
   - Blind, independent secondary evaluation without seeing Reviewer 1's decisions.
3. **Adjudicator (Lead Researcher / Senior Linguist):**
   - Resolves any discrepancies between Reviewer 1 and Reviewer 2.
   - Authorizes final query wording or initiates replacement of rejected items.

---

## 2. Review Sheet Structure & Columns

Reviewers must complete their respective sections in `research/HUMAN_QUERY_REVIEW_SHEET.csv`:

| Column Name | Valid Values | Description |
|---|---|---|
| `reviewer_N_id` | e.g., `REV-TA-01`, `REV-HI-01` | Anonymized identifier of the reviewer |
| `reviewer_N_semantic_preservation_1to5` | `1`, `2`, `3`, `4`, `5` | Faithfulness to original English intent |
| `reviewer_N_naturalness_1to5` | `1`, `2`, `3`, `4`, `5` | Fluency of colloquial Romanized code-switching |
| `reviewer_N_entity_constraint_preservation` | `YES` / `NO` | Are names, numbers, limits, and technical terms preserved? |
| `reviewer_N_decision` | `ACCEPT`, `REVISE`, `REJECT` | Independent recommendation |
| `reviewer_N_proposed_revision` | Free text | Required if `REVISE` is selected |
| `reviewer_N_comments` | Free text | Observations, cultural nuances, or dialect notes |

---

## 3. Explicit Scoring Criteria & Worked Examples

### 3.1 Semantic Preservation (1–5 Scale)
* **5 — Perfect:** Expresses the exact same core information need and constraints.
  - *Example (English):* "What is the daily transaction limit for UPI transfers?"
  - *Tanglish (Score 5):* `Oru bank account-la daily UPI transaction limit evvalavu?`
* **4 — High:** Negligible phrasing variance; retrieves the exact same target chunk.
* **3 — Moderate:** Slightly generic or conversational, but intent is unambiguous.
* **2 — Low (Flawed):** Missing a key constraint or altering the question scope.
  - *Flawed Example:* `UPI transfer eppadi panrathu?` (Asks *how* to do a transfer, not *what the limit is*).
* **1 — Critical Failure:** Incomprehensible, wrong domain, or completely different question.

### 3.2 Naturalness & Code-Mixing Authenticity (1–5 Scale)
* **5 — Highly Authentic:** Colloquial code-switching reflecting real Indian smartphone and chat communication.
  - *Example (Hinglish):* `Physical SIM card ko eSIM mein convert karne ka procedure kya hai?`
* **3 — Artificial/Stiff:** Literal word-by-word translation that sounds unnatural to native speakers.
* **1 — Synthetic Nonsense:** Grammar salad or broken transliteration.

### 3.3 Entity & Constraint Preservation (YES / NO)
* **Must be marked NO** if amounts (e.g. `100,000 INR`, `50%`, `36 months`), brand names (`YONO`, `Power Jyoti PUL`, `Green Notes`), or policy thresholds (`Rs. 7,500`) are omitted, altered, or hallucinated.

---

## 4. Current Review Progress Summary (as of October 27, 2026)

| Metric | Tamil-English (Tanglish) | Hindi-English (Hinglish) | Total Benchmark |
|---|---|---|---|
| **Total Query Items** | 50 | 50 | **100** |
| **Completed Reviewer 1 Evaluations** | 0 | 0 | **0** |
| **Completed Reviewer 2 Evaluations** | 0 | 0 | **0** |
| **Agreed Acceptances** | 0 | 0 | **0** |
| **Proposals for Revision** | 0 | 0 | **0** |
| **Rejected Items** | 0 | 0 | **0** |
| **Disputed / Pending Adjudication** | 0 | 0 | **0** |
| **Total Pending Items** | 50 | 50 | **100 (100%)** |
| **Gate Status** | **BLOCKED** | **BLOCKED** | **BLOCKED — HUMAN BILINGUAL REVIEW REQUIRED** |

---

## 5. Adjudication Procedure

1. **Unanimous Agreement:**
   - If Reviewer 1 = `ACCEPT` and Reviewer 2 = `ACCEPT`, and both naturalness/semantic scores are $\ge 4$:
   - Adjudicator marks `adjudication_decision = ACCEPT_ORIGINAL` and copies `code_mixed_query` to `final_approved_query_text`.
2. **Split Decision (One ACCEPT, One REVISE):**
   - Adjudicator inspects `proposed_revision`. If the revision improves authenticity or fixes a minor spelling flaw, mark `adjudication_decision = ACCEPT_REVISION` and paste the revised text in `final_approved_query_text`.
3. **Dispute / Reject (Either Reviewer = REJECT):**
   - Adjudicator reviews the item. If the item is invalid, mark `REJECT_REPLACE`. A replacement code-mixed query must be drafted and reviewed by both reviewers.

---

## 6. Final Benchmark Release Checklist

Before `Phase E` (Production Experiment) can unlock, all items below must be verified:

- [ ] All 50 Tamil-English queries have completed evaluations from Reviewer 1 and Reviewer 2.
- [ ] All 50 Hindi-English queries have completed evaluations from Reviewer 1 and Reviewer 2.
- [ ] Inter-annotator agreement (Cohen's $\kappa$ on accept/revise/reject) is calculated and recorded.
- [ ] Every disputed or revised item is adjudicated and signed off in `research/HUMAN_QUERY_REVIEW_SHEET.csv`.
- [ ] All 100 rows have `final_approved_query_text` populated and approved.
- [ ] `data/queries/final_queries_v1.json` is updated with adjudicated queries and marked `status: VERIFIED_GOLD`.
- [ ] `research/HUMAN_REVIEW_BLOCKERS.md` is cleared.
- [ ] Preflight validation (`python scripts/run_production_preflight.py`) exits with code 0.
