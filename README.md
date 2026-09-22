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
- `tests/`: 67 automated Pytest tests.
- `data/`:
  - `documents/`: Source corpus files (PDF, CSV, TXT, JSON).
  - `queries/`: Information needs dataset (`sample_queries.json`).
  - `processed/` & `vector_store/`: Generated chunks and FAISS index.
- `results/`: Output analysis reports and CSVs.

## Dataset Description
- **Corpus**: 5 sample documents (Banking FAQ, Telecom Support, University Policies, Library Guide, Green Bond Report) parsed into 12 documents and 23 chunks.
- **Queries**: 3 information needs across Telecom and Banking domains. Each need has an English, Tamil-English, and Hindi-English variant (9 total variants).

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
```

## How to Run the Backend & Frontend
The frontend is served directly by the FastAPI backend.
```bash
python -m uvicorn backend.main:app --port 8000 --reload
```
Navigate to `http://127.0.0.1:8000/` in your browser to use the interactive Chatbot.
Navigate to `http://127.0.0.1:8000/dashboard` to view the Evaluation Dashboard.

## How to Reproduce Results
1. **Ingest Documents**:
   ```bash
   python scripts/run_ingestion.py
   ```
2. **Run the Evaluation Pipeline**:
   Runs all 6 conditions (Baseline + Mitigated for 3 languages) against the query dataset.
   ```bash
   python scripts/run_experiment.py --all
   ```
3. **Analyze Results**:
   Generates the statistical report in `results/`.
   ```bash
   python scripts/analyze_results.py
   ```

## Example API Endpoints
- `GET /health`: Health check.
- `POST /api/chat`: Interactive chat endpoint performing detection, normalization, retrieval, generation, and faithfulness scoring in one call.
- `GET /api/dashboard/summary`: Retrieves experiment statistics from the SQLite database.

## Baseline vs Mitigation Explanation
- **Baseline**: The user's query (e.g., code-mixed Tanglish) is embedded as-is and sent directly to FAISS for similarity search.
- **Mitigation**: The system detects code-mixing and calls an LLM to translate the query into formal English before embedding. The normalized query typically retrieves much more relevant context from the English corpus.

## Results (Pilot Study)
The pilot study completed 18 evaluated runs across 6 conditions.
- **Faithfulness Score**: All 18 runs achieved a perfect faithfulness score of `1.0`.
- **Hallucination Rate**: `0%` across all conditions.
- **Success Criterion**: The gap between English baseline mean and Code-Mixed mitigated mean was `0.00` (which is ≤ 0.10). The success criterion was met for both Tamil-English and Hindi-English.
- *Note: Due to the zero variance in scores in this small pilot, paired Wilcoxon tests were not statistically viable.*

## Limitations
- The pilot dataset is very small (3 information needs, 5 synthetic documents).
- Perfect retrieval led to zero variance in faithfulness scores, preventing formal statistical significance testing.
- `Recall@K` was not explicitly tracked in the database for the pilot.

## Future Work
- Scale the evaluation to 50+ information needs and 300+ runs using real-world noisy corpora.
- Implement formal `Recall@K` tracking and evaluation.
- Test against non-Romanized, native script code-mixing (Tamil script, Devanagari).
- Incorporate a human-in-the-loop evaluation to validate the LLM-as-a-Judge scores.
