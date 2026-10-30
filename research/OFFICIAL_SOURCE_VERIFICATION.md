# OFFICIAL_SOURCE_VERIFICATION.md
# Official Source Verification Report: State Bank of India Documents

**Date:** October 26, 2026  
**Auditor:** Automated Agentic Pair-Programmer (Local Audit & Official Domain Verification)  
**Verification Scope:** Only official State Bank of India domains (`https://sbi.bank.in/`, `https://bank.sbi/`, `https://sbi.co.in/`) and exact publisher portals.  
**Constraint Compliance:** No unofficial reposts, blogs, social media, file-sharing repositories, or third-party snippet aggregators were used. No corpus or database modifications were made.

---

## 1. Executive Summary

| Document | Title in Corpus | Official Status | Official Source URL | Verification Verdict |
|---|---|---|---|---|
| `microfinance_loans_policy.txt` | Policy on ‘Microfinance Loans’ | State Bank of India Official Policy Circular | `https://sbi.bank.in/documents/14463/22577/20012023_Mircorfinance+Loan+Policy+for+Publication.pdf` | **VERIFIED OFFICIAL SOURCE** |
| `code_of_ethics.txt` | SBI Code of Ethics (DO/DON'T Summary) | Researcher-curated abridged extract | UNVERIFIED (Internal/intranet circular) | **BLOCKED PENDING USER CONFIRMATION** |
| `digital_and_transaction_banking_products.txt` | Booklet on Digital & Transaction Banking Products | SBI Marketing / Product Brochure | UNVERIFIED (No static public URL for full text) | **BLOCKED PENDING USER CONFIRMATION** |
| `ee9a3135_Impact Reporting of Green Bond of USD 250 Million.pdf` | Impact Reporting of Green Bond of USD 250 Million | Official Investor Relations / CAAPL Report | UNVERIFIED (Dynamic portal routing; direct URL unresolved) | **BLOCKED PENDING USER CONFIRMATION** |

---

## 2. Detailed Document Verifications

### 2.1 `microfinance_loans_policy.txt`
* **Local File:** `data/documents/microfinance_loans_policy.txt` (20,270 bytes, 37 FAISS chunks)
* **Official Source URL:** `https://sbi.bank.in/documents/14463/22577/20012023_Mircorfinance+Loan+Policy+for+Publication.pdf`
* **Publisher / Entity:** State Bank of India, NBFC Alliances Department, ABU & GSS, Corporate Centre, Mumbai
* **Document Version:** Version 1.0 (Incorporating instructions issued up to 18.10.2022)
* **Access Date:** 2026-10-26
* **Verification Evidence:**
  - Official PDF downloaded and inspected directly from `https://sbi.bank.in/`.
  - Substantive content matches across all major sections:
    - §1: Introduction citing RBI Circular `RBI/DOR/2021-22/89 - DoR.FIN.REC.95/03.10.038/2021-22`.
    - §2: Definition of Microfinance Loan (collateral-free, annual household income up to ₹3,00,000, max tenure 36 months, 2-month moratorium).
    - §3: Assessment of Household Income and mandatory reporting to Credit Information Companies (CICs).
    - §4: Limit on loan repayment obligations capped at 50% of monthly household income.
    - §5: Pricing of loans, factsheet disclosure, and prohibition of prepayment penalties.
    - §6: Guidelines on conduct, staff training, Fair Practices Code, and standard loan cards.
* **Mismatches / Variations:**
  - The local text file (`microfinance_loans_policy.txt`) is an exact text extraction of Sections 1 through 6.3 of the official 25-page publication PDF. Later sections of the PDF (§7 to §12: Product Parameters, NPA provisioning, and Annexures I–V) were omitted from the text corpus.
* **Licensing / Terms:** Publicly accessible official document; redistribution rights not assumed.
* **Status:** **VERIFIED OFFICIAL SOURCE**

---

### 2.2 `code_of_ethics.txt`
* **Local File:** `data/documents/code_of_ethics.txt` (10,968 bytes, 35 FAISS chunks)
* **Accurate Characterization:** Researcher-curated abridged extract derived from the official SBI Code of Ethics source (DO/DON'T guidance summary).
* **Official Publisher:** State Bank of India, Ethics & Business Conduct Department, Corporate Centre, Mumbai.
* **Official Source Status:**
  - The official SBI Code of Ethics exists in two forms:
    1. Abridged Version 3.0 PDF (effective 01.04.2026, 49 pages, verified in `research/CODE_OF_ETHICS_VERSION_COMPARISON.md`).
    2. Internal employee circulars distributed via the SBI HRMS / Intranet portal.
  - No permanent, open static URL for the exact DO/DON'T bullet text was found on the public domain without intranet access.
* **Verification Evidence & Mismatches:**
  - Local text is 10,968 characters vs. 60,226 characters in the official v3.0 booklet.
  - As established in [CODE_OF_ETHICS_VERSION_COMPARISON.md](file:///C:/Users/NIRANJNA/.gemini/antigravity-ide/scratch/cross-lingual-rag-eval/research/CODE_OF_ETHICS_VERSION_COMPARISON.md), `code_of_ethics.txt` is an abridged, curated DO/DON'T summary representing a strict subset of the official guidance.
  - All 12 study queries targeting the Code of Ethics rely on rules present identically in both texts (e.g., gift acceptance limits of Rs. 7,500 / 15,000 / 25,000, STEPS values).
* **Action Required:** The researcher must provide the original intranet circular URL or institutional origin link.
* **Status:** **BLOCKED PENDING USER CONFIRMATION** (Source URL: UNVERIFIED)

---

### 2.3 `digital_and_transaction_banking_products.txt`
* **Local File:** `data/documents/digital_and_transaction_banking_products.txt` (4,720 bytes, 16 FAISS chunks)
* **Title:** Booklet on Digital & Transaction Banking Products
* **Publisher / Entity:** State Bank of India, Digital & Transaction Banking – Marketing Department / Transaction Banking Unit (TBU), Corporate Centre
* **Official Source Status:**
  - All described products are verified official SBI commercial offerings hosted across `https://sbi.bank.in/`:
    - **Power Jyoti PUL (Pre-Upload / TBU):** Specialized centralized pooling current account for institutions and NBFCs with pre-uploaded validation data.
    - **Easy Collect:** Premium collection facility across 22,000+ branches.
    - **Mandate-Based Collection & E-Mandate:** NACH/Direct Debit centralized collection workflows.
    - **Collection (VAN):** Virtual Account Numbers for automated reconciliation.
    - **Digi Dealer:** Mobile application linked with YONO Business for merchant/dealer cash and cheque deposition.
    - **E-Payments:** RTGS/NEFT/Direct Credit bulk corporate payout file processing.
* **Verification Evidence & Mismatches:**
  - While individual products are actively documented across SBI's corporate banking website, the consolidated 81-line marketing booklet text itself appears to have been compiled from an internal marketing brochure or client hand-out. A single static public URL hosting this exact text could not be confirmed on `sbi.bank.in`.
* **Action Required:** The researcher must confirm the original source URL or internal brochure source.
* **Status:** **BLOCKED PENDING USER CONFIRMATION** (Source URL: UNVERIFIED)

---

### 2.4 `ee9a3135_Impact Reporting of Green Bond of USD 250 Million.pdf`
* **Local File:** `data/documents/ee9a3135_Impact Reporting of Green Bond of USD 250 Million.pdf` (676,583 bytes, 8 pages, 69 FAISS chunks)
* **Issuer / Entity:** State Bank of India (London Branch) / CareEdge Advisory (CARE Analytics and Advisory Private Limited - CAAPL)
* **Key Instrument Parameters Verified:**
  - Instrument: Senior Unsecured Green Floating Rate Notes ("The Green Notes", USD 250 Million).
  - Issuance Date: December 29, 2023 | Maturity Date: December 29, 2028.
  - Benchmark: SOFR + 1.20% | Medium-Term Note Program: USD 10 Billion | Exchange: India INX.
  - Impact Metric: 4.38 million metric tons CO2 equivalent reduction annually across 6,027 million kWh generated; 137 jobs created.
* **Official Source Status:**
  - SBI's official Investor Relations portal on `sbi.bank.in` explicitly references and lists this document under its ESG Financing and Green Bond Post-Issuance disclosures.
  - However, direct URL links on the portal use dynamic session tokens / Liferay CMS endpoints, preventing resolution of an unauthenticated permanent static URL.
* **Action Required:** The researcher must provide the direct investor relations URL or confirm academic fair use.
* **Status:** **BLOCKED PENDING USER CONFIRMATION** (Source URL: UNVERIFIED)

---

## 3. Remaining Unresolved Documents & Required User Actions

To advance the corpus to `READY TO FREEZE`, the user must provide the following:

1. **`code_of_ethics.txt`:** Provide the specific internal SBI circular link or official source URL where the DO/DON'T guidance was extracted.
2. **`digital_and_transaction_banking_products.txt`:** Provide the specific SBI marketing portal URL or brochure origin.
3. **`ee9a3135_Impact Reporting of Green Bond of USD 250 Million.pdf`:** Provide the permanent SBI Investor Relations download URL.
4. **Researcher Sign-Off in `research/PROVENANCE_CONFIRMATION_FORM.md`:**
   - Complete Section 6.2 (PII confirmation, researcher name, affiliation, date, and final freeze approval).
