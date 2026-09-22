import time
import logging
from typing import Dict, Any, Optional

from backend.llm.base import LLMProvider
from backend.retrieval.searcher import VectorSearcher
from backend.rag.prompt import SYSTEM_PROMPT, build_rag_prompt
from backend.api.schemas import RAGQueryResponse, RetrievedDocument
from backend.config.settings import get_settings
from backend.detection.base import CodeMixDetector
from backend.normalization.base import QueryNormalizer
from backend.evaluation.base import FaithfulnessJudge
from backend.database.sqlite_client import SQLiteClient

logger = logging.getLogger("rag_service")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

class RAGService:
    """
    Connects vector retrieval to LLM generation.
    Optionally applies code-mix mitigation and faithfulness evaluation.
    """
    def __init__(
        self,
        searcher: VectorSearcher,
        llm: LLMProvider,
        detector: Optional[CodeMixDetector] = None,
        normalizer: Optional[QueryNormalizer] = None,
        judge: Optional[FaithfulnessJudge] = None,
        db: Optional[SQLiteClient] = None,
    ):
        self.searcher = searcher
        self.llm = llm
        self.settings = get_settings()
        self.detector = detector
        self.normalizer = normalizer
        self.judge = judge
        self.db = db

    def _construct_context(self, retrieved_chunks: list) -> str:
        if not retrieved_chunks:
            return ""
        
        # Simple concatenation. Future: Token counting/truncation based on LLM_MAX_TOKENS.
        contexts = [f"--- Document {i+1} ---\n{chunk['text']}" for i, chunk in enumerate(retrieved_chunks)]
        return "\n\n".join(contexts)

    def answer_query(
        self,
        raw_query: str,
        mitigation_enabled: Optional[bool] = None,
        evaluate_faithfulness: bool = False,
    ) -> RAGQueryResponse:
        settings = get_settings()
        
        # --- Mitigation Layer ---
        is_mitigation_on = mitigation_enabled if mitigation_enabled is not None else settings.MITIGATION_ENABLED
        
        search_query = raw_query
        normalized_query_str = None
        mitigation_applied = False

        if is_mitigation_on:
            if not self.detector or not self.normalizer:
                logger.error("Mitigation is enabled but detector or normalizer is not initialized. Falling back to raw query.")
            else:
                try:
                    logger.info(f"Mitigation ON. Running detection on: {raw_query}")
                    det_result = self.detector.detect(raw_query)
                    norm_result = self.normalizer.normalize(raw_query, det_result)
                    
                    if norm_result.normalization_applied and not norm_result.error_fallback:
                        search_query = norm_result.normalized_query
                        normalized_query_str = norm_result.normalized_query
                        mitigation_applied = True
                        logger.info(f"Query normalized: {raw_query} -> {search_query}")
                    else:
                        logger.info("Normalization bypassed or fell back. Using raw query.")
                except Exception as e:
                    logger.error(f"Mitigation pipeline failed: {e}. Falling back to raw query.")
        else:
            logger.info("Mitigation OFF. Using raw query.")
            
        start_time = time.time()
        
        # --- Retrieval ---
        try:
            chunks = self.searcher.retrieve(search_query, k=self.settings.RAG_TOP_K)
        except Exception as e:
            logger.error(f"Retrieval error: {e}")
            raise RuntimeError(f"Retrieval failed: {e}")
            
        context_str = self._construct_context(chunks)
        user_prompt = build_rag_prompt(search_query, context_str)
        
        # --- Generation ---
        answer = self.llm.generate(
            prompt=user_prompt,
            system_prompt=SYSTEM_PROMPT
        )
        
        latency = time.time() - start_time
        logger.info(f"RAG processed | Model: {settings.LLM_MODEL} | Mitigation: {mitigation_applied} | Latency: {latency:.2f}s")
        
        # --- Format retrieved docs ---
        retrieved_docs = [
            RetrievedDocument(
                chunk_id=c.get("chunk_id", "unknown"),
                document_id=c.get("document_id", "unknown"),
                text=c.get("text", ""),
                score=c.get("score", 0.0),
                metadata=c.get("metadata", {})
            )
            for c in chunks
        ]
        
        # --- Optional Faithfulness Evaluation ---
        faithfulness_score = None
        hallucination_flag = None
        faithfulness_explanation = None
        
        if evaluate_faithfulness:
            if not self.judge:
                logger.warning("evaluate_faithfulness requested but no judge configured.")
            else:
                try:
                    eval_result = self.judge.evaluate(answer=answer, context=context_str)
                    faithfulness_score = eval_result.faithfulness_score
                    hallucination_flag = eval_result.hallucination_flag
                    faithfulness_explanation = eval_result.explanation
                    logger.info(
                        f"Faithfulness: score={faithfulness_score:.2f} | "
                        f"hallucination={hallucination_flag} | model={eval_result.judge_model}"
                    )
                    # Persist to SQLite
                    if self.db:
                        self.db.save_evaluation(
                            query=raw_query,
                            answer=answer,
                            context=context_str,
                            score=faithfulness_score,
                            flag=hallucination_flag,
                            explanation=faithfulness_explanation,
                            model=eval_result.judge_model,
                            version=eval_result.judge_prompt_version,
                        )
                except Exception as e:
                    logger.error(f"Faithfulness evaluation failed: {e}")
        
        return RAGQueryResponse(
            query=raw_query,
            normalized_query=normalized_query_str,
            mitigation_applied=mitigation_applied,
            answer=answer,
            retrieved_documents=retrieved_docs,
            context=user_prompt,
            model=settings.LLM_MODEL,
            faithfulness_score=faithfulness_score,
            hallucination_flag=hallucination_flag,
            faithfulness_explanation=faithfulness_explanation,
        )
