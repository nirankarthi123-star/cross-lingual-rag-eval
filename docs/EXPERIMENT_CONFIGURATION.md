# Experiment Configuration Documentation

This document explicitly defines the fixed variables and configurations for the cross-lingual RAG evaluation study. Any deviations from these variables compromise the integrity of the 3×2 baseline vs. mitigation analysis.

## Core Models (Production Study)
- **Embedding Model**: `intfloat/multilingual-e5-base` (Dimension: 768)
- **Generator Model**: `openai/gpt-oss-20b` (via Groq API)
- **Judge Model (LLM-as-a-judge)**: `openai/gpt-oss-20b` (via Groq API)
- **Normalizer Model**: `openai/gpt-oss-20b` (via Groq API)

### Legacy Historical Models (Preserved for Provenance)
> [!NOTE]
> - `llama3-8b-8192`: Used during early exploratory iterations and the 18-run pilot. Subsequently decommissioned by Groq (returning HTTP 400). Its historical rows remain preserved in `data/rag_eval.db` for provenance and are not deleted.
> - `llama-3.1-8b-instant`: Used in intermediate exploratory evaluation tests.

## Vector Store Parameters
- **Embedding Dimension**: 768
- **Retrieval `top_k`**: 5
- **Chunk Size**: 500 characters
- **Chunk Overlap**: 100 characters
- **Index Type**: FAISS `IndexFlatIP` (Cosine similarity via inner product on normalized embeddings)

## Judge Parameters
- **Faithfulness Scoring**: 0.0 to 1.0 (continuous support ratio)
- **Hallucination Threshold**: `< 0.8` (Any score below 0.8 is strictly flagged as a hallucination).
- **Prompt Version**: `v1`
- **Failure Semantics**: Infrastructure, rate-limit, or JSON parse errors return `None` (missing evaluation) rather than `0.0`, preventing false hallucination attribution.

## Experimental Design
- **Independent Variable 1**: Language Variant
  - English (Canonical monolingual baseline)
  - Tamil-English (Tanglish, Romanized intra-sentential code-mixed)
  - Hindi-English (Hinglish, Romanized intra-sentential code-mixed)
- **Independent Variable 2**: Mitigation Condition
  - Baseline (`OFF`: Raw query passed directly to retrieval)
  - Mitigated (`ON`: Code-mixed query normalized to English prior to retrieval)
- **Dataset**: `data/queries/sample_queries.json` (50 base information needs × 3 language variants = 150 total queries).
- **Total Experiment Matrix**: 50 queries × 6 conditions = **300 runs**.

## Database Architecture
- **Production Study DB**: `data/research_study.db` (Clean database containing strictly production runs).
- **Legacy Pilot DB**: `data/rag_eval.db` (Historical database preserved read-only containing the 18 pilot runs and partial exploratory trials).

## System Constraints & Preflight Guardrails
1. **The Mitigation Layer**: Must **never** answer the query; it must strictly normalize code-mixed text into retrieval-friendly English while preserving entities.
2. **The Code-Mix Detector**: Bypasses normalization for purely English queries to maintain a strict experimental baseline.
3. **Preflight Validator**: Refuses to launch a production experiment if:
   - Corpus manifest or SHA-256 hash is missing or out of sync with active index.
   - Query dataset SHA-256 hash is missing or unverified.
   - Duplicate question IDs or missing language variants exist.
   - `expected_document_ids` are missing or refer to documents not present in the vector index.
   - The dataset mixes mock/smoke test rows with production queries.
