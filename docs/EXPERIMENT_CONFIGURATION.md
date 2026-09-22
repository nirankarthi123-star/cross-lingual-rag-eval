# Experiment Configuration Documentation

This document explicitly defines the fixed variables and configurations for the cross-lingual RAG evaluation. Any deviations from these variables compromise the integrity of the 3x2 baseline vs. mitigation analysis.

## Core Models
- **Embedding Model**: `intfloat/multilingual-e5-base`
- **Generator Model**: `llama3-8b-8192` (via Groq)
- **Judge Model (LLM-as-a-judge)**: `llama-3.1-8b-instant` (via Groq)
- **Normalizer Model**: `llama-3.1-8b-instant` (via Groq)

## Vector Store Parameters
- **Embedding Dimension**: 768
- **Retrieval `top_k`**: 5
- **Chunk Size**: 500 characters
- **Chunk Overlap**: 100 characters

## Judge Parameters
- **Faithfulness Scoring**: 0.0 to 1.0
- **Hallucination Threshold**: `< 0.8` (Any score below 0.8 is strictly flagged as a hallucination).
- **Prompt Version**: `v1`

## Experimental Design
- **Independent Variable 1**: Language (English, Tamil-English, Hindi-English)
- **Independent Variable 2**: Mitigation Status (Baseline [OFF] vs. Mitigated [ON])
- **Dataset Version**: Phase 12 (Production)

## System Constraints
1. The Mitigation layer must **never** answer the query; it must strictly normalize code-mixed text into retrieval-friendly English.
2. The Code-Mix Detector explicitly bypasses normalization for purely English queries to maintain a strict experimental baseline.
3. If normalization fails due to invalid JSON or LLM timeouts, the system safely falls back to the original query and records the failure.
