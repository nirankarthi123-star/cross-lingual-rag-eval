# CODE_MIXED_DATA_GUIDELINES.md
# Guidelines for Code-Mixed Data in the Cross-Lingual RAG Faithfulness Study

**Version:** 1.0  
**Date:** October 26, 2026  
**Repository:** `cross-lingual-rag-eval`  
**Status:** Approved for use in Phase P2 full study

---

## 1. Purpose

This document defines the precise linguistic conventions, annotation standards, and quality criteria governing how code-mixed query variants (Tanglish and Hinglish) are constructed, validated, and used in the evaluation dataset. It ensures that all 50 base information needs and their 100 code-mixed variants are linguistically consistent, reproducible, and grounded in real user register.

---

## 2. Defining "Code-Mixed" in This Study

### 2.1 Linguistic Definition

**Intra-sentential code-mixing** (the register targeted in this study) is the alternation between two languages *within a single sentence*, where the matrix language provides the syntactic frame and the embedded language contributes lexical items, noun phrases, or content words.

This study specifically targets **Romanized intra-sentential code-mixing** — code-mixed speech produced in the Roman (Latin) script, as commonly used in informal digital communication (SMS, WhatsApp, social media) by South Asian users.

**Two varieties are studied:**

| Variety | Label | Matrix Language | Embedded Language | Example |
|---|---|---|---|---|
| Tanglish | `tamil_english` | Tamil | English | *"Ennoda bank account-la daily UPI limit evvalavu?"* |
| Hinglish | `hindi_english` | Hindi | English | *"Mere bank account mein UPI ka daily limit kitna hai?"* |

### 2.2 What This Study Does NOT Include

- **Script-native multilingual queries**: Queries written in Tamil script (தமிழ்) or Devanagari (हिन्दी) are **out of scope**. The study targets Romanized transliteration exclusively.
- **Transliterated monolingual text**: A query that is entirely Tamil transliterated into Roman script without English code-switching (e.g., *"Thinanthorum UPI alavilanai enna?"*) is **not** the target phenomenon.
- **Machine translation**: Queries produced by Google Translate or any other MT system are **not acceptable** as Tanglish/Hinglish variants.

---

## 3. Construction Rules for Code-Mixed Query Variants

### 3.1 Tanglish (`tamil_english`) Conventions

1. **Matrix Language is Tamil.** The base syntactic structure follows Tamil SOV word order.
2. **English domain terms are preserved.** Technical banking and telecom terms that have no widely used Tamil equivalents are kept in English: e.g., "UPI", "NEFT", "debit card", "SHG", "microfinance", "eSIM", "roaming".
3. **Tamil function words are Romanized in standard form.** Common Tamil function words and postpositions must be consistently spelled:

| Tamil Word | Standard Romanization Used in Dataset |
|---|---|
| என்ன (what) | enna |
| எவ்வளவு (how much) | evvalavu |
| எப்படி (how) | eppadi |
| என்னோட / எனது (my) | ennoda / enodaya |
| இல்ல / இல்ல (in/at suffix) | -la |
| க்கு (to/for suffix) | -kku |
| பண்ண (to do) | panna |
| செய்ய (to do formal) | seyya |

4. **No diacritics or special characters.** All Tamil Romanization uses plain ASCII (a-z, 0-9, hyphen). No macrons, dots, or IPA symbols.
5. **Colloquial contractions are permitted.** The dataset reflects informal spoken register (e.g., *"thevai"* for தேவை, *"irukku"* for இருக்கு).

### 3.2 Hinglish (`hindi_english`) Conventions

1. **Matrix Language is Hindi.** The base syntactic structure follows Hindi SOV word order.
2. **English domain terms are preserved.** Same rule as Tanglish.
3. **Hindi function words are Romanized in standard form:**

| Hindi Word | Standard Romanization Used in Dataset |
|---|---|
| क्या (what/is it) | kya |
| कैसे (how) | kaise |
| कितना (how much) | kitna |
| कौनसे (which) | kaunse |
| मेरे / मेरा (my) | mere / mera |
| में (in/at) | mein |
| के लिए (for) | ke liye |
| होता है (happens/is) | hota hai |
| करना है (need to do) | karna hai |
| है (is) | hai |

4. **No Devanagari script.** All Hinglish is written exclusively in Roman script.
5. **No diacritics.** Plain ASCII only.

---

## 4. Quality Criteria for Code-Mixed Queries

Every code-mixed query in the dataset must satisfy ALL of the following:

### 4.1 Naturalness
- The query must read as something a real South Asian user would plausibly type in a messaging application or search box.
- Avoid overly formal or stiff constructions that read like direct translations.

### 4.2 Semantic Equivalence
- The code-mixed query must convey the **exact same information need** as its English counterpart.
- No paraphrasing that changes scope, adds constraints, or removes qualifiers present in the English query.

### 4.3 Domain Term Preservation
- All domain-specific English terms (banking, telecom) must appear **verbatim** in the code-mixed variant, exactly as they appear in the corpus.
- The retrieval system's BM25/dense retriever operates on English embeddings. Preserving English technical terms ensures that the code-mixed query still contains vocabulary that can match corpus chunks, making the retrieval challenge tractable and measurable.

### 4.4 Single Language Alternate
- Each query has exactly **one** Tanglish variant and **one** Hinglish variant.
- There must be no additional language variants, no mixed-script variants, and no dialect variants.

### 4.5 Grounding in Document
- The correct answer to the query **must exist** verbatim or paraphrastically in one or more indexed chunks.
- `expected_document_ids` must resolve to document IDs present in `data/vector_store/metadata_map.json`.

---

## 5. Code-Mix Detector Behaviour

The project uses a **two-pass heuristic Code-Mix Detector** (`backend/retrieval/normalizer.py`) to classify incoming queries before deciding whether to apply LLM normalization.

### 5.1 Detection Logic

**Pass 1 — Unicode Script Analysis:**  
Detects non-ASCII characters (Tamil Unicode block, Devanagari Unicode block). A query containing native-script characters is immediately classified as `native_script_multilingual`.

**Pass 2 — Romanized Lexicon Match:**  
Checks the query against a curated list of Romanized Tamil and Hindi function words. A query matching ≥ 1 lexicon entry AND containing ≥ 1 English content word is classified as `romanized_code_mixed`.

**Fallback:**  
A query that passes neither filter is classified as `english_only`.

### 5.2 Implications for Dataset Quality

All 100 code-mixed query variants (50 Tanglish + 50 Hinglish) were designed to trigger the **Romanized Lexicon Match** pass. This is a dataset construction invariant: queries that fail to trigger the detector do not test the normalization mitigation and must be revised.

### 5.3 Detector Limitations (Documented)

- The Romanized lexicon is finite and may miss novel code-mixed constructions.
- The detector does not distinguish Tanglish from Hinglish; it detects the presence of code-mixing but not the source language.
- Queries with only English text but borrowings of Indian English (e.g., "lakh", "crore") will **not** be flagged as code-mixed.

These limitations are intentional design constraints for this study and are documented here for reproducibility.

---

## 6. Relationship to External Benchmarks

| Benchmark | Overlap with This Study | Key Difference |
|---|---|---|
| LinCE | Hindi-English code-mixing (social media) | LinCE uses Twitter data; NER/LID tasks; not QA or faithfulness |
| GLUECoS | Hindi-English QA task | GLUECoS queries are Wikipedia-domain; not banking/telecom |
| IndicGLUE | Tamil and Hindi NLP tasks | IndicGLUE uses native scripts; not Romanized code-mixed |
| XQuAD | Cross-lingual Hindi QA | XQuAD uses Devanagari Hindi; Wikipedia domain |

**Conclusion:** No existing public benchmark covers the intersection of (i) Romanized intra-sentential code-mixing in Tamil-English and Hindi-English, (ii) domain-specific knowledge (banking/telecom), and (iii) faithfulness evaluation of RAG-generated answers. This study fills that gap.

---

## 7. Annotation Provenance Statement

All 150 query variants (50 English + 50 Tanglish + 50 Hinglish) in `data/queries/sample_queries.json` were constructed with the following provenance:

1. **English queries**: Derived directly from factual claims present in the indexed corpus documents. No facts were invented.
2. **Tanglish and Hinglish variants**: Constructed by applying the conventions in Section 3 to each English query. Variants were not produced by machine translation.
3. **Expected document IDs**: Mapped to active FAISS index entries in `data/vector_store/metadata_map.json` at the time of dataset creation (September 23, 2026). The corpus manifest hash at that time is recorded in `data/corpus_manifest.json`.

> [!IMPORTANT]
> **Reproducibility Requirement**: If the corpus is re-ingested (e.g., after adding new documents), `expected_document_ids` must be re-verified against the updated `metadata_map.json`. The preflight validator in `backend/experiments/preflight.py` automates this check.

---

## 8. Prohibition on Data Fabrication

The following are **explicitly prohibited** in this dataset and any future expansions:

- Adding queries whose answers do not appear in any indexed chunk.
- Inventing code-mixed constructions by mechanical replacement of English words without linguistic grounding.
- Inferring expected document IDs from document filenames without verifying against the FAISS index metadata.
- Representing machine-translated outputs as natural code-mixed user queries.
- Mixing script-native text with Romanized text in the same query variant.
