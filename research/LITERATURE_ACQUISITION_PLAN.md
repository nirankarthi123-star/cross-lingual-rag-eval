# LITERATURE_ACQUISITION_PLAN.md
# Targeted Literature Acquisition Plan for Cross-Lingual RAG Faithfulness Research

**Project:** Cross-Lingual RAG Faithfulness Evaluation under Code-Mixing (English, Tamil-English, Hindi-English)  
**Status:** Approved Specification — Ready for Researcher Manual Intake  
**Protocol Compliance:** Strict anti-fabrication rules; no automatic web scraping or hallucinated metadata.

---

## 1. Executive Summary & Objective

To transition this research from an exploratory prototype to a rigorous, peer-reviewed scientific paper, the study requires a verified, authoritative literature foundation spanning six distinct technical pillars. 

Existing literature in `research/literature/` currently covers:
* Foundational RAG architecture (Lewis et al., 2020)
* Dense sentence embeddings (Reimers & Gurevych, 2019)
* Vector search indexing (Johnson et al., 2019)
* LLM-as-a-judge benchmark methodologies (Zheng et al., 2023)
* RAG faithfulness evaluation foundations (Wang et al., 2023)

This acquisition plan establishes the exact criteria, required research areas, and verification procedures for the researcher to manually acquire the remaining high-impact papers.

---

## 2. Inclusion & Exclusion Criteria (Applied to All Categories)

Every paper submitted for inclusion must satisfy the following verifiable criteria:

### 2.1 Mandatory Inclusion Criteria
1. **Publication Venue:** Must be published in a recognized, peer-reviewed conference/journal (e.g., ACL, EMNLP, NAACL, EACL, LREC-COLING, SIGIR, CIKM, KDD, NeurIPS, ICLR, AAAI, IEEE/ACM Transactions) OR a verifiable preprint on arXiv with a stable identifier and timestamp.
2. **Persistent Identifier:** Must have a resolvable DOI, official ACL Anthology URL, arXiv URL, or official publisher landing page.
3. **Primary Text Availability:** Complete PDF must be locally inspectable and extractable.
4. **Verifiable Authorship:** Author names, institutional affiliations, publication year, and volume/pages must be verifiable from the PDF itself.
5. **Direct Methodological Relevance:** Must directly inform one of the six research questions or methodologies of this study.

### 2.2 Mandatory Exclusion Criteria
1. Papers from predatory or unindexed journals.
2. Blog posts, slide decks, social media posts, or unverified secondary summaries.
3. Papers whose citation metadata cannot be verified against official publisher repositories.
4. Automatically scraped or paywalled materials acquired without proper institutional license.

---

## 3. The Six Target Research Pillars

### Pillar 1: Code-Mixed South Asian NLP (Tamil-English & Hindi-English)
* **Rationale:** Establishes the linguistic and computational reality of code-mixing (intra-sentential switching, borrowed lexical items, morphological inflection) in Dravidian (Tamil) and Indo-Aryan (Hindi) language contact with English.
* **Specific Focus Areas:**
  - Code-mixed text classification and sentiment analysis in Indian languages (e.g., DravidianLangTech, FIRE, ICON shared tasks).
  - Benchmark datasets representing natural code-switching (e.g., GLUECoS, LinCE).
* **Key Venues to Target:** ACL, EMNLP, LREC-COLING, Forum for Information Retrieval Evaluation (FIRE), DravidianLangTech Workshops.
* **Priority:** `P0 (Critical for Paper Framing)`

---

### Pillar 2: Romanized Code-Mix Detection & Query Normalization
* **Rationale:** Directly justifies the experimental design's *Mitigation Condition* (`normalised`), which translates and standardizes Romanized Hinglish/Tanglish queries into canonical English before vector search.
* **Specific Focus Areas:**
  - Back-transliteration (phonetic mapping from Roman script to Indic Devanagari/Tamil script).
  - Code-mixed machine translation and cross-lingual normalization for search.
  - Zero-shot LLM translation versus dedicated phonetic transliteration engines (IndicTrans2, Google Transliterate).
* **Key Venues to Target:** EMNLP, NAACL, WMT (Conference on Machine Translation), SIGIR.
* **Priority:** `P0 (Critical for Mitigation Defense)`

---

### Pillar 3: Multilingual & Cross-Lingual Information Retrieval (CLIR)
* **Rationale:** Grounding for our vector retrieval pipeline where queries are code-mixed but the target corpus is predominantly English.
* **Specific Focus Areas:**
  - Cross-lingual dense retrieval using multilingual sentence encoders (e.g., multilingual-e5, BGE-M3, LaBSE, mContriever).
  - Lexical vs. semantic mismatch under phonetic Romanization in dense vector spaces.
  - Performance degradation in cross-lingual retrieval when query script deviates from corpus script.
* **Key Venues to Target:** SIGIR, CIKM, ECIR, ACL (IR track).
* **Priority:** `P0 (Critical for Retrieval Evaluation)`

---

### Pillar 4: RAG Faithfulness Evaluation & Hallucination Metrics
* **Rationale:** Forms the conceptual basis for evaluating whether generated answers adhere strictly to retrieved context.
* **Specific Focus Areas:**
  - Granular hallucination taxonomies (intrinsic vs. extrinsic hallucinations).
  - Established RAG evaluation frameworks (e.g., Ragas, TruLens, ARES).
  - Cross-lingual hallucination dynamics (how non-English inputs induce English hallucinations or unfaithful claims).
* **Key Venues to Target:** EMNLP, ACL, NeurIPS, ICLR.
* **Priority:** `P0 (Core Dependent Variable)`

---

### Pillar 5: LLM-as-a-Judge Reliability & Bias Mitigation
* **Rationale:** Methodological justification and boundary conditions for using `llama-3.3-70b-versatile` / `llama3-70b-8192` as the automated evaluation judge.
* **Specific Focus Areas:**
  - Inter-annotator agreement between LLM judges and human raters (Cohen’s kappa, Krippendorff’s alpha).
  - Systematic biases in LLM judges: position bias, verbosity bias, self-enhancement bias.
  - Prompt engineering for strict JSON schema conformance and chain-of-thought faithfulness scoring.
* **Key Venues to Target:** EMNLP, ACL, NeurIPS, ICML.
* **Priority:** `P1 (Methodological Rigor)`

---

### Pillar 6: Paired Statistical Evaluation in NLP & IR
* **Rationale:** Ensures valid hypothesis testing across the 300 runs (Baseline vs. Mitigation across English, Tamil-English, and Hindi-English).
* **Specific Focus Areas:**
  - Paired non-parametric testing for bounded/skewed NLP metrics (Wilcoxon signed-rank test).
  - Multiple testing corrections (Holm-Bonferroni, Benjamini-Hochberg FDR) across multiple language strata.
  - Effect size quantification (Rank-biserial correlation, Cohen's d for paired differences).
* **Key Reference Literature:** Dror et al. (ACL 2018), "The Hitchhiker's Guide to Testing Statistical Significance in Natural Language Processing"; Demšar (JMLR 2006).
* **Priority:** `P1 (Statistical Analysis Validation)`

---

## 4. Intake & Verification Workflow for Researcher

When you acquire a new paper:

1. **Save PDF:** Place the PDF in `research/literature/` using the standard naming convention:  
   `[first_author]_[year]_[short_title].pdf` (e.g., `khanuja_2020_gluecos.pdf`).
2. **Local Verification:** Run the local verification script (or provide file for hashing):
   - Calculate SHA-256 checksum.
   - Extract page 1 to verify exact title, author names, venue, and year.
3. **Record Metadata:** Add an entry into `research/literature/literature_matrix.csv` with:
   - `paper_id` (e.g., `LIT-11`, `LIT-12`)
   - `title`, `authors`, `year`, `venue`, `doi_or_url`
   - `category` (one of the 6 pillars above)
   - `project_role` (`background`, `methodology`, `baseline`, or `benchmark`)
4. **No Automated Scraping:** To prevent corrupted or unverifiable entries, no automated scrapers or web search bots will download PDFs or generate citations.

---

## 5. Minimum Literature Target for Paper Submission

To be submission-ready for a top-tier NLP/IR venue (ACL/EMNLP/SIGIR):
* **Current verified papers:** 5
* **Target total verified papers:** 15–20 papers
* **Immediate high-priority intake required:**
  - 2 papers on Indian language code-mixing (Tamil/Hindi)
  - 2 papers on Romanized code-mixed IR or transliteration
  - 2 papers on LLM judge reliability & paired statistical testing
