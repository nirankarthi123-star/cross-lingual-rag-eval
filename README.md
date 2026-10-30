# Cross-Lingual Faithfulness Evaluation of RAG Chatbots

## Project Overview
This project evaluates the faithfulness of Retrieval-Augmented Generation (RAG) chatbots when handling code-mixed queries (e.g., Tamil-English and Hindi-English). It provides an automated evaluation framework to measure the impact of query language on retrieval quality and answer groundedness.

## Problem Statement
Real-world users in multilingual regions frequently use code-mixed language (e.g., mixing Tamil/Hindi with English). Standard English-oriented RAG systems struggle to retrieve relevant context for code-mixed queries because their embedding spaces do not align well with Romanized code-mixed text. This leads to retrieval degradation and hallucinated answers.

## Proposed Solution
The project implements a two-stage mitigation strategy:
1. Detect code-mixing using a two-pass heuristic (Unicode script + Romanized lexicons).
2. Normalize the code-mixed query to standard English using an LLM before embedding and retrieval.
The framework then compares the faithfulness of the RAG generator (scored by an LLM-as-a-Judge) across baseline (no normalization) and mitigated conditions.

## Key Features
- **Multilingual Support**: Supports English, Tamil-English (Tanglish), and Hindi-English (Hinglish).
- **Code-Mix Detection**: Two-pass heuristic detector for identifying native and Romanized code-mixing.
- **LLM-Based Query Normalization**: Preserves exact intent, names, numbers, and constraints while translating to English.
- **Automated Evaluation Pipeline**: LLM-as-a-Judge scores answer faithfulness against retrieved context.
- **Interactive Dashboard & Chatbot**: Real-time FastAPI backend serving Vanilla JS/HTML frontend.
- **Statistical Analysis**: Integrated SciPy for paired statistical testing of results.

## System Architecture
1. **Offline Indexing**: Documents are chunked (500 chars, 100 overlap) and embedded into a FAISS index.
2. **Online Retrieval**: Queries are detected, optionally normalized, embedded, and used to retrieve the Top-5 chunks.
3. **Generation**: An LLM generates an answer using only the retrieved context.
4. **Evaluation**: A judge LLM scores the answer's faithfulness (0.0 to 1.0) and flags hallucinations.

## Technologies Used
- **Backend**: Python, FastAPI, Uvicorn
- **Frontend**: Vanilla HTML, CSS, JavaScript
- **Vector Search**: FAISS (faiss-cpu)
- **Embeddings**: `intfloat/multilingual-e5-base` via `sentence-transformers`
- **LLM / Generation**: `openai/gpt-oss-20b` via Groq API
- **Evaluation**: LLM-as-a-Judge (`openai/gpt-oss-20b` via Groq API)
- **Database**: SQLite
- **Testing & Analysis**: Pytest, SciPy

## Project Structure
- `backend/`: FastAPI application, API routes, and core RAG modules (detection, normalization, retrieval, generation, evaluation).
- `frontend/`: Static HTML/JS/CSS files (`index.html` for Chatbot, `dashboard.html` for Evaluation).
- `scripts/`: CLI scripts for ingestion, experiment running, and analysis.
- `tests/`: 74 automated Pytest tests.
- `data/`:
  - `documents/`: Source corpus files (8 files: PDF, CSV, TXT, JSON).
  - `queries/`: Information needs dataset (`sample_queries.json` with 50 base questions).
  - `processed/` & `vector_store/`: Generated chunks (180 chunks), corpus manifest, and FAISS index.
- `results/`: Output analysis reports and CSVs.

## Dataset & Corpus Architecture

### Active Production Corpus vs. Historical Pilot Corpus
- **Active Expanded Corpus**:
  - **8 source documents** in `data/documents/`: Banking FAQ (JSON), Telecom Support (CSV), University Policies (TXT), Campus Library Guide (PDF), SBI Green Bond Impact Report (PDF), Digital Banking Products (TXT), Code of Ethics (TXT), and Microfinance Loans Policy (TXT).
  - Parsed into **16 logical documents** and **180 indexed chunks** (500 chars / 100 overlap).
  - Documented and hash-verified via `data/processed/corpus_manifest.json`.
- **Active Query Dataset**:
  - **50 base information needs** across Banking and Telecom.
  - 3 balanced variants per need: English, Tamil-English (Tanglish), Hindi-English (Hinglish) = **150 total queries**.
  - All 50 queries have ground-truth `expected_document_ids` for Recall@1, Recall@3, and Recall@5 calculation.
- **Historical Pilot Corpus (Archived)**:
  - Initial 5 sample documents parsed into 12 documents and 23 chunks with 3 dev queries (`DEV-Q01`..`DEV-Q03`).

## Database Partitioning

To maintain strict scientific integrity and avoid data contamination:
- **`data/research_study.db` (Clean Production Study)**:
  Dedicated database for the complete 300-run experiment (50 queries × 6 conditions). Starts empty, enforces preflight safety validation, and records comprehensive reproducibility metadata.
- **`data/rag_eval.db` (Legacy Pilot Record)**:
  Historical database preserved read-only containing the 18 pilot runs, early decommissioned model errors, and partial exploratory runs.

## Installation Requirements
```bash
# Clone the repository
git clone <your-repo-url>
cd cross-lingual-rag-eval

# Create and activate virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Mac/Linux:
# source venv/bin/activate

# Install dependencies
python -m pip install -r requirements.txt
```

## Environment Variables
Create a `.env` file in the root directory (you can copy `.env.example`):
```env
GROQ_API_KEY=your_groq_api_key_here
MITIGATION_ENABLED=true
LLM_MODEL=openai/gpt-oss-20b
NORMALIZER_LLM_MODEL=openai/gpt-oss-20b
JUDGE_LLM_MODEL=openai/gpt-oss-20b
```

## How to Run the Backend & Frontend
The frontend is served directly by the FastAPI backend.
```bash
python -m uvicorn backend.main:app --port 8000 --reload
```
Navigate to `http://127.0.0.1:8000/` in your browser to use the interactive Chatbot.  
Navigate to `http://127.0.0.1:8000/dashboard` to view the Evaluation Dashboard.

## How to Reproduce Results

1. **Ingest Documents & Build Index**:
   ```bash
   python scripts/ingest_documents.py
   python scripts/build_index.py
   ```

2. **Preflight Safety Validation**:
   ```bash
   python -m backend.experiments.preflight --dataset data/queries/sample_queries.json
   ```

3. **Run Dry-Run (Clean Production Study)**:
   ```bash
   python scripts/run_experiment.py --all --dataset data/queries/sample_queries.json --db data/research_study.db --dry-run
   ```

4. **Execute Full Production Experiment**:
   ```bash
   python scripts/run_experiment.py --all --dataset data/queries/sample_queries.json --db data/research_study.db
   ```

5. **Analyze Results**:
   ```bash
   python scripts/analyze_results.py --db data/research_study.db --output-dir results/research_study
   ```

## Example API Endpoints
- `GET /health`: Health check.
- `POST /api/chat`: Interactive chat endpoint performing detection, normalization, retrieval, generation, and faithfulness scoring in one call.
- `GET /api/dashboard/summary`: Retrieves experiment statistics from the SQLite database.

## Baseline vs Mitigation Explanation
- **Baseline**: The user's query (e.g., code-mixed Tanglish) is embedded as-is and sent directly to FAISS for similarity search.
- **Mitigation**: The system detects code-mixing and calls an LLM to translate the query into formal English before embedding. The normalized query typically retrieves much more relevant context from the English corpus.

## Historical Pilot Study Results (Exploratory Prototype)
The historical coursework pilot completed 18 evaluated runs across 6 conditions on the 3-question dev set:
- **Faithfulness Score**: All 18 runs achieved a faithfulness score of `1.0`.
- **Hallucination Rate**: `0%` across all conditions.
- **Limitations**: The pilot dataset was too small ($n=3$) and lacked variance, making formal statistical tests (Wilcoxon) non-testable. The full 300-run study resolves this by evaluating 50 diverse queries with ground-truth Recall@K tracking.
