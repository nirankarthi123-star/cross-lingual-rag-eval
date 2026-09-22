from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: str


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def get_health() -> HealthResponse:
    """
    Health check endpoint to verify backend service availability.
    """
    return HealthResponse(status="ok")


class DatasetStatsResponse(BaseModel):
    num_documents: int
    num_chunks: int
    empty_documents: int
    empty_chunks: int
    avg_chunk_length: float
    min_chunk_length: int
    max_chunk_length: int
    document_types: dict


@router.get("/api/documents/stats", response_model=DatasetStatsResponse, tags=["Documents"])
async def get_document_stats() -> DatasetStatsResponse:
    """
    Return statistics on processed documents and chunks in the active corpus.
    """
    from pathlib import Path
    from backend.config.settings import get_settings
    from backend.retrieval.validator import validate_dataset

    settings = get_settings()
    processed_path = Path(settings.PROCESSED_DIR)
    stats = validate_dataset(processed_dir=processed_path)

    return DatasetStatsResponse(
        num_documents=stats.num_documents,
        num_chunks=stats.num_chunks,
        empty_documents=stats.empty_documents,
        empty_chunks=stats.empty_chunks,
        avg_chunk_length=stats.avg_chunk_length,
        min_chunk_length=stats.min_chunk_length,
        max_chunk_length=stats.max_chunk_length,
        document_types=stats.document_types,
    )


# --- RAG Endpoint ---

import logging
from fastapi import HTTPException
from backend.api.schemas import RAGQueryRequest, RAGQueryResponse
from backend.rag.service import RAGService

logger = logging.getLogger(__name__)

# Global service instance cache
_rag_service = None

def get_rag_service() -> RAGService:
    global _rag_service
    if _rag_service is None:
        try:
            from backend.retrieval.indexer import FAISSIndexer
            from backend.retrieval.searcher import VectorSearcher
            
            # Re-initialize indexer
            indexer = FAISSIndexer()
            indexer.load()
            
            # Re-initialize embedding provider
            from backend.embeddings.sentence_transformer import SentenceTransformerProvider
            embed_provider = SentenceTransformerProvider()
            
            # Re-initialize searcher
            searcher = VectorSearcher(embed_provider, indexer)
            
            # Initialize LLM Provider
            from backend.llm.groq_provider import GroqProvider
            llm_provider = GroqProvider()
            
            # Initialize Detector and Normalizer
            from backend.detection.heuristic_detector import HeuristicRegexDetector
            from backend.normalization.llm_normalizer import LLMNormalizer
            
            detector = HeuristicRegexDetector()
            normalizer = LLMNormalizer(llm_provider)
            
            # Initialize Faithfulness Judge and DB
            from backend.evaluation.llm_judge import LLMFaithfulnessJudge
            from backend.database.sqlite_client import SQLiteClient
            from backend.config.settings import get_settings
            
            judge_settings = get_settings()
            # The judge uses its own configured model — passed per-call in generate()
            from backend.llm.groq_provider import GroqProvider as JudgeProvider
            judge_llm = JudgeProvider()  # same API key; model is specified at generate() time
            judge = LLMFaithfulnessJudge(llm=judge_llm)
            db = SQLiteClient()
            
            _rag_service = RAGService(searcher, llm_provider, detector, normalizer, judge, db)
            logger.info("RAGService initialized with detection, normalization, and faithfulness judge layers.")
        except Exception as e:
            logger.error(f"Failed to initialize RAGService: {e}")
            raise RuntimeError(f"Failed to initialize RAGService: {e}")
            
    return _rag_service


@router.post("/api/rag/query", response_model=RAGQueryResponse, tags=["RAG"])
async def query_rag(request: RAGQueryRequest) -> RAGQueryResponse:
    """
    Submit a query to the RAG pipeline.
    The pipeline will retrieve context from the FAISS index and generate an answer.
    If mitigation_enabled is true, it will attempt code-mix normalization first.
    """
    try:
        service = get_rag_service()
        response = service.answer_query(
            request.query,
            request.mitigation_enabled,
            request.evaluate_faithfulness,
        )
        return response
    except Exception as e:
        # Avoid exposing raw api keys or sensitive internal errors directly if possible,
        # but for this dev setup we will return a 500 with the error string
        raise HTTPException(status_code=500, detail=str(e))


# --- Detection Endpoint ---

from backend.api.schemas import DetectionRequest
from backend.detection.models import DetectionResult

_detector_service = None

def get_detector():
    global _detector_service
    if _detector_service is None:
        from backend.detection.heuristic_detector import HeuristicRegexDetector
        _detector_service = HeuristicRegexDetector()
    return _detector_service


@router.post("/api/detection", response_model=DetectionResult, tags=["Detection"])
async def detect_query(request: DetectionRequest) -> DetectionResult:
    """
    Detect code-mixing within a given query.
    Returns structured language spans and confidence.
    """
    try:
        detector = get_detector()
        return detector.detect(request.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Dashboard Endpoints ---

from typing import Optional, List, Dict, Any
from backend.database.sqlite_client import SQLiteClient
from backend.evaluation.analysis import (
    load_and_validate_data,
    compute_descriptive_stats,
    evaluate_success_criterion
)

@router.get("/api/dashboard/summary", tags=["Dashboard"])
async def get_dashboard_summary():
    """
    Returns high-level statistics for the dashboard overview.
    """
    try:
        db = SQLiteClient()
        raw_records = db.get_all_experiment_results()
        
        if not raw_records:
            return {"status": "empty", "message": "No experimental results available."}
            
        valid_records, excluded_records = load_and_validate_data(raw_records)
        stats = compute_descriptive_stats(valid_records)
        success_criterion = evaluate_success_criterion(stats)
        
        # Calculate overall averages for overview
        total_queries = len(valid_records)
        total_faithfulness = sum(r["faithfulness_score"] for r in valid_records)
        total_hallucinations = sum(1 for r in valid_records if r["hallucination_flag"])
        
        avg_faithfulness = (total_faithfulness / total_queries) if total_queries > 0 else 0
        overall_hallucination_rate = (total_hallucinations / total_queries) if total_queries > 0 else 0
        
        return {
            "status": "success",
            "overview": {
                "total_queries_evaluated": len(set(r["question_id"] for r in valid_records)),
                "total_experiments": total_queries,
                "average_faithfulness": round(avg_faithfulness, 4),
                "overall_hallucination_rate": round(overall_hallucination_rate, 4)
            },
            "condition_summaries": stats,
            "success_criterion": success_criterion
        }
    except Exception as e:
        logger.error(f"Failed to load dashboard summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/dashboard/results", tags=["Dashboard"])
async def get_dashboard_results(
    language: Optional[str] = None,
    mitigation: Optional[bool] = None,
    hallucination: Optional[bool] = None
):
    """
    Returns individual query results, optionally filtered.
    """
    try:
        db = SQLiteClient()
        raw_records = db.get_all_experiment_results()
        valid_records, _ = load_and_validate_data(raw_records)
        
        filtered = valid_records
        if language is not None:
            filtered = [r for r in filtered if r["language"] == language]
        if mitigation is not None:
            filtered = [r for r in filtered if r["mitigation_enabled"] == mitigation]
        if hallucination is not None:
            filtered = [r for r in filtered if r["hallucination_flag"] == hallucination]
            
        return {"status": "success", "results": filtered}
    except Exception as e:
        logger.error(f"Failed to load dashboard results: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Interactive Chat Endpoint ---

import time as _time
from pydantic import Field as _Field

class ChatRequest(BaseModel):
    query: str = _Field(..., min_length=1, description="The user's question.")
    mitigation_enabled: bool = _Field(True, description="Whether to apply code-mix normalization.")
    top_k: Optional[int] = _Field(None, ge=1, le=20, description="Number of retrieval results.")

class ChatRetrievedDoc(BaseModel):
    document_id: str
    chunk_id: str
    score: float
    text: str

class ChatResponse(BaseModel):
    answer: str
    original_query: str
    normalized_query: Optional[str] = None
    code_mix_detected: bool = False
    detected_languages: list = []
    mitigation_enabled: bool = False
    mitigation_applied: bool = False
    retrieved_documents: list = []
    generator_model: str = ""
    judge_model: str = ""
    faithfulness_score: Optional[float] = None
    hallucination_flag: Optional[bool] = None
    faithfulness_explanation: Optional[str] = None
    latency: Optional[float] = None
    error: Optional[str] = None


@router.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
async def interactive_chat(request: ChatRequest) -> ChatResponse:
    """
    Interactive RAG chatbot endpoint.
    Performs retrieval, optional mitigation, generation, and faithfulness evaluation.
    Results are NOT stored in the experiment-results table.
    """
    t0 = _time.time()
    from backend.config.settings import get_settings

    try:
        service = get_rag_service()
    except Exception as e:
        return ChatResponse(
            answer="",
            original_query=request.query,
            error=f"Service initialization failed: {e}",
        )

    settings = get_settings()

    # --- Detection ---
    det_result = None
    code_mix_detected = False
    detected_languages = []
    try:
        if service.detector:
            det_result = service.detector.detect(request.query)
            code_mix_detected = det_result.is_code_mixed
            detected_languages = det_result.languages
    except Exception as e:
        logger.warning(f"Detection failed: {e}")

    # --- Normalization ---
    search_query = request.query
    normalized_query_str = None
    mitigation_applied = False
    if request.mitigation_enabled and code_mix_detected and service.normalizer and det_result:
        try:
            norm_result = service.normalizer.normalize(request.query, det_result)
            if norm_result.normalization_applied and not norm_result.error_fallback:
                search_query = norm_result.normalized_query
                normalized_query_str = norm_result.normalized_query
                mitigation_applied = True
        except Exception as e:
            logger.warning(f"Normalization failed, falling back to raw query: {e}")

    # --- Retrieval ---
    top_k = request.top_k or settings.RAG_TOP_K
    try:
        chunks = service.searcher.retrieve(search_query, k=top_k)
    except Exception as e:
        return ChatResponse(
            answer="",
            original_query=request.query,
            code_mix_detected=code_mix_detected,
            detected_languages=detected_languages,
            mitigation_enabled=request.mitigation_enabled,
            error=f"Retrieval failed: {e}",
        )

    from backend.rag.prompt import SYSTEM_PROMPT, build_rag_prompt
    context_str = service._construct_context(chunks)
    user_prompt = build_rag_prompt(search_query, context_str)

    # --- Generation ---
    try:
        answer = service.llm.generate(prompt=user_prompt, system_prompt=SYSTEM_PROMPT)
    except Exception as e:
        return ChatResponse(
            answer="",
            original_query=request.query,
            code_mix_detected=code_mix_detected,
            detected_languages=detected_languages,
            mitigation_enabled=request.mitigation_enabled,
            mitigation_applied=mitigation_applied,
            normalized_query=normalized_query_str,
            retrieved_documents=[
                ChatRetrievedDoc(
                    document_id=c.get("document_id", ""),
                    chunk_id=c.get("chunk_id", ""),
                    score=c.get("score", 0.0),
                    text=c.get("text", ""),
                ) for c in chunks
            ],
            generator_model=settings.LLM_MODEL,
            error=f"Generation failed: {e}",
        )

    # --- Faithfulness Evaluation ---
    faithfulness_score = None
    hallucination_flag = None
    faithfulness_explanation = None
    judge_model = ""
    if service.judge:
        try:
            eval_result = service.judge.evaluate(answer=answer, context=context_str)
            faithfulness_score = eval_result.faithfulness_score
            hallucination_flag = eval_result.hallucination_flag
            faithfulness_explanation = eval_result.explanation
            judge_model = eval_result.judge_model or settings.JUDGE_LLM_MODEL
        except Exception as e:
            faithfulness_explanation = f"Judge evaluation failed: {e}"
            logger.warning(faithfulness_explanation)

    latency = round(_time.time() - t0, 3)

    # NOTE: We intentionally do NOT call service.db.save_evaluation() or
    # save_experiment_result() here. Interactive chat results must remain
    # separate from Phase 10 experiment data.

    return ChatResponse(
        answer=answer,
        original_query=request.query,
        normalized_query=normalized_query_str,
        code_mix_detected=code_mix_detected,
        detected_languages=detected_languages,
        mitigation_enabled=request.mitigation_enabled,
        mitigation_applied=mitigation_applied,
        retrieved_documents=[
            ChatRetrievedDoc(
                document_id=c.get("document_id", ""),
                chunk_id=c.get("chunk_id", ""),
                score=c.get("score", 0.0),
                text=c.get("text", ""),
            ) for c in chunks
        ],
        generator_model=settings.LLM_MODEL,
        judge_model=judge_model,
        faithfulness_score=faithfulness_score,
        hallucination_flag=hallucination_flag,
        faithfulness_explanation=faithfulness_explanation,
        latency=latency,
    )


# --- Document Management Endpoints ---
import shutil
import uuid
from pathlib import Path
from fastapi import UploadFile, File, Form, BackgroundTasks
from scripts.ingest_documents import ingest
import importlib

class IngestResponse(BaseModel):
    message: str
    status: str

@router.post("/api/documents/upload", tags=["Documents"])
async def upload_document(file: UploadFile = File(...), source_url: str = Form("")):
    """
    Upload a document (PDF, TXT, CSV, JSON) safely without overwriting.
    """
    from backend.config.settings import get_settings
    settings = get_settings()
    docs_dir = Path(settings.DOCUMENTS_DIR)
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    # Validate extension
    allowed = {".pdf", ".txt", ".csv", ".json"}
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed: {allowed}")
    
    # Save file uniquely
    safe_name = f"{uuid.uuid4().hex[:8]}_{file.filename}"
    file_path = docs_dir / safe_name
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")
        
    return {"status": "success", "filename": safe_name, "message": "File uploaded successfully."}


@router.post("/api/documents/ingest", response_model=IngestResponse, tags=["Documents"])
async def ingest_documents():
    """
    Trigger the document ingestion pipeline and rebuild the FAISS index.
    """
    from backend.config.settings import get_settings
    settings = get_settings()
    try:
        # Run ingest and chunking
        docs, chunks = ingest(
            input_dir=Path(settings.DOCUMENTS_DIR),
            output_dir=Path(settings.PROCESSED_DIR),
            chunk_size=settings.DEFAULT_CHUNK_SIZE,
            chunk_overlap=settings.DEFAULT_CHUNK_OVERLAP,
            run_validation=False
        )
        
        # Build index
        from scripts.build_index import main as build_index_main
        # Re-initialize SentenceTransformer manually to build the index here or call the script logic
        from backend.embeddings.sentence_transformer import SentenceTransformerProvider
        from backend.retrieval.indexer import FAISSIndexer
        
        provider = SentenceTransformerProvider()
        embeddings = provider.embed_documents([c.chunk_text for c in chunks])
        
        indexer = FAISSIndexer()
        indexer.build_index(chunks, embeddings)
        indexer.save()
        
        # Invalidate the cached RAG service so it reloads the FAISS index
        global _rag_service
        _rag_service = None
        
        return IngestResponse(
            status="success", 
            message=f"Successfully ingested {len(docs)} documents into {len(chunks)} chunks and rebuilt index."
        )
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")
