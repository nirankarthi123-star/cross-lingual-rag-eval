# Query Dataset Creation Guide

This document outlines the guidelines for constructing the final query dataset for the Cross-Lingual Faithfulness Evaluation of RAG Chatbots on Code-Mixed Queries.

## 1. What is a "Base Question"?
A **base question** represents a single, unique underlying information need. For our research design, we need approximately 40–50 base questions derived from our fixed knowledge base corpus (telecom/banking FAQs, policies, etc.).

Each base question MUST be accompanied by its expected document IDs (the `chunk_id` or `document_id` that contains the ground-truth answer) for future evaluation phases.

## 2. What is "Code-Mixing" in this Project?
For this project, we are focusing specifically on **intra-sentential code-mixing**.
- **Definition**: Mixing two languages seamlessly within the *same* sentence or utterance.
- **Languages**: Tamil-English and Hindi-English.
- **Script**: Romanized (Latin script) or Native script, but this must be explicitly noted in the `script_type` metadata field.

### Examples of Intra-sentential Code-mixing (Romanized)
- **English**: "How do I activate international roaming?"
- **Tamil-English**: "Ennoda mobile-la international roaming eppadi activate panrathu?"
- **Hindi-English**: "Mere mobile par international roaming kaise activate karu?"

## 3. The Strict Translation Constraint
It is **CRITICAL** that all three language variants for a single `question_id` represent the *exact same* underlying information need.

**Why?**
Because this project evaluates how the RAG pipeline's faithfulness degrades or fluctuates based on the language input. If the Hindi query actually asks for something slightly different than the English query, any failure by the RAG bot could be attributed to the altered intent rather than the language itself.

### How to generate the final 120–150 query variants
1. **Curate the Base Queries (English)**: Identify 40-50 diverse questions that can be answered by the corpus.
2. **Translate to Tamil-English**: Ensure native syntax while injecting English domain terms naturally.
3. **Translate to Hindi-English**: Ensure native syntax while injecting English domain terms naturally.
4. **Human Validation**: Do **NOT** rely on automated, uncontrolled MT pipelines (like Google Translate). The variants must be verified by a human annotator to ensure intra-sentential mixing is natural and the information need remains perfectly aligned with the base query.
5. **Ingestion**: Save the final dataset as `data/queries/final_dataset.json` or `.csv`.
6. **Validation**: Run `python scripts/validate_queries.py data/queries/final_dataset.json` to ensure there are no missing variants or accidental duplicates before running the evaluation suite.
