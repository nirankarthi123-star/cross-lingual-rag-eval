"""
ExperimentRunner for Phase 9.

Executes the 3×2 experiment matrix with:
- Resume capability (skips already-completed runs)
- Exponential-backoff retry on rate-limit/transient errors
- Dry-run mode
- Per-run structured logging
"""
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Set, Tuple

from backend.experiments.models import ExperimentConfig, ExperimentResult
from backend.experiments.matrix import MatrixRow
from backend.dataset.schemas import QueryRecord
from backend.database.sqlite_client import SQLiteClient
from backend.config.settings import get_settings

logger = logging.getLogger("experiment_runner")

# Errors considered transient — worth retrying
TRANSIENT_ERROR_SUBSTRINGS = [
    "rate limit", "ratelimit", "rate_limit",
    "too many requests", "429",
    "connection", "timeout", "503", "502",
]

MAX_RETRIES = 4
BASE_RETRY_DELAY = 2.0  # seconds; doubled each attempt


def _is_transient(error_msg: str) -> bool:
    msg = error_msg.lower()
    return any(s in msg for s in TRANSIENT_ERROR_SUBSTRINGS)


class ExperimentRunner:
    """
    Runs the full experiment matrix.
    Initialises the RAG service once and reuses it across all runs.
    """

    def __init__(self, db: Optional[SQLiteClient] = None):
        self.db = db or SQLiteClient()
        self._rag_service = None
        self.settings = get_settings()

    # ------------------------------------------------------------------ #
    # Service initialisation (lazy)                                        #
    # ------------------------------------------------------------------ #

    def _get_rag_service(self):
        if self._rag_service is not None:
            return self._rag_service

        from backend.retrieval.indexer import FAISSIndexer
        from backend.retrieval.searcher import VectorSearcher
        from backend.embeddings.sentence_transformer import SentenceTransformerProvider
        from backend.llm.groq_provider import GroqProvider
        from backend.detection.heuristic_detector import HeuristicRegexDetector
        from backend.normalization.llm_normalizer import LLMNormalizer
        from backend.evaluation.llm_judge import LLMFaithfulnessJudge
        from backend.rag.service import RAGService

        indexer = FAISSIndexer()
        indexer.load()

        embed = SentenceTransformerProvider()
        searcher = VectorSearcher(embed, indexer)

        gen_llm = GroqProvider()
        judge_llm = GroqProvider()

        detector = HeuristicRegexDetector()
        normalizer = LLMNormalizer(gen_llm)
        judge = LLMFaithfulnessJudge(llm=judge_llm)

        self._rag_service = RAGService(
            searcher=searcher,
            llm=gen_llm,
            detector=detector,
            normalizer=normalizer,
            judge=judge,
            db=self.db,
        )
        logger.info("RAGService initialized for experiment runner.")
        return self._rag_service

    # ------------------------------------------------------------------ #
    # Resume logic                                                         #
    # ------------------------------------------------------------------ #

    def _get_completed_keys(self) -> Set[Tuple[str, str, str, bool]]:
        """
        Return the set of (experiment_id, question_id, language, mitigation_enabled)
        tuples that are already stored in the DB as completed runs.
        """
        return self.db.get_completed_run_keys()

    # ------------------------------------------------------------------ #
    # Single run with retry                                                #
    # ------------------------------------------------------------------ #

    def _run_one(
        self,
        config: ExperimentConfig,
        record: QueryRecord,
        query_string: str,
    ) -> ExperimentResult:
        """Execute one pipeline run with retry/backoff."""
        run_id = str(uuid.uuid4())
        started_at = datetime.now(timezone.utc).isoformat()

        last_error: Optional[str] = None

        for attempt in range(MAX_RETRIES):
            try:
                service = self._get_rag_service()
                response = service.answer_query(
                    raw_query=query_string,
                    mitigation_enabled=config.mitigation_enabled,
                    evaluate_faithfulness=True,
                )

                completed_at = datetime.now(timezone.utc).isoformat()

                retrieved_doc_ids = [
                    doc.chunk_id for doc in response.retrieved_documents
                ]

                return ExperimentResult(
                    run_id=run_id,
                    experiment_id=config.experiment_id,
                    question_id=record.question_id,
                    language=config.language,
                    mitigation_enabled=config.mitigation_enabled,
                    original_query=query_string,
                    normalized_query=response.normalized_query,
                    mitigation_applied=response.mitigation_applied,
                    retrieved_document_ids=retrieved_doc_ids,
                    retrieved_context=response.context,
                    generated_answer=response.answer,
                    faithfulness_score=response.faithfulness_score,
                    hallucination_flag=response.hallucination_flag,
                    faithfulness_explanation=response.faithfulness_explanation,
                    embedding_model=config.embedding_model,
                    generator_model=config.generator_model,
                    judge_model=config.judge_model,
                    started_at=started_at,
                    completed_at=completed_at,
                    error=None,
                )

            except Exception as e:
                last_error = str(e)
                if _is_transient(last_error) and attempt < MAX_RETRIES - 1:
                    delay = BASE_RETRY_DELAY * (2 ** attempt)
                    logger.warning(
                        f"Transient error on attempt {attempt+1}/{MAX_RETRIES}: {last_error}. "
                        f"Retrying in {delay:.1f}s…"
                    )
                    time.sleep(delay)
                else:
                    break

        # All retries exhausted or non-transient error
        logger.error(f"Run failed for [{config.experiment_id}] q={record.question_id}: {last_error}")
        return ExperimentResult(
            run_id=run_id,
            experiment_id=config.experiment_id,
            question_id=record.question_id,
            language=config.language,
            mitigation_enabled=config.mitigation_enabled,
            original_query=query_string,
            normalized_query=None,
            mitigation_applied=False,
            retrieved_document_ids=[],
            retrieved_context="",
            generated_answer="",
            faithfulness_score=None,
            hallucination_flag=None,
            faithfulness_explanation=None,
            embedding_model=config.embedding_model,
            generator_model=config.generator_model,
            judge_model=config.judge_model,
            started_at=started_at,
            completed_at=datetime.now(timezone.utc).isoformat(),
            error=last_error,
        )

    # ------------------------------------------------------------------ #
    # Dry-run                                                              #
    # ------------------------------------------------------------------ #

    def dry_run(self, matrix: List[MatrixRow]) -> None:
        """Print what would be executed without making any API calls."""
        completed = self._get_completed_keys()
        conditions: dict = {}

        skipped = 0
        pending = 0

        print(f"\n{'='*70}")
        print(f"DRY-RUN — Experiment Matrix")
        print(f"{'='*70}")
        print(f"Total runs in matrix : {len(matrix)}")
        print(f"Already completed    : {len(completed)}")

        for config, record, query_string in matrix:
            key = (config.experiment_id, record.question_id, config.language, config.mitigation_enabled)
            status = "SKIP (completed)" if key in completed else "PENDING"
            if key in completed:
                skipped += 1
            else:
                pending += 1

            cond_key = config.experiment_id
            if cond_key not in conditions:
                conditions[cond_key] = {
                    "language": config.language,
                    "mitigation": config.mitigation_enabled,
                    "condition": config.condition_name,
                    "count": 0,
                }
            conditions[cond_key]["count"] += 1

        print(f"Pending runs         : {pending}")
        print(f"Skipped (resume)     : {skipped}")
        print(f"\n{'-'*70}")
        print(f"{'Experiment ID':<35} {'Language':<15} {'Mitigation':<12} {'# Queries'}")
        print(f"{'-'*70}")

        for exp_id, info in sorted(conditions.items()):
            mitigation_str = "ON  (mitigated)" if info["mitigation"] else "OFF (baseline)"
            print(f"{exp_id:<35} {info['language']:<15} {mitigation_str:<12} {info['count']}")

        print(f"{'='*70}\n")

    # ------------------------------------------------------------------ #
    # Full run                                                             #
    # ------------------------------------------------------------------ #

    def run_all(self, matrix: List[MatrixRow], delay_between_runs: float = 0.5) -> List[ExperimentResult]:
        """
        Execute all pending runs in the matrix.

        Args:
            matrix: Output of generate_matrix().
            delay_between_runs: Seconds to sleep between runs to respect rate limits.

        Returns:
            List of ExperimentResult for all runs (including resumed runs as None entries).
        """
        completed_keys = self._get_completed_keys()
        total = len(matrix)
        pending = [(c, r, q) for c, r, q in matrix
                   if (c.experiment_id, r.question_id, c.language, c.mitigation_enabled) not in completed_keys]

        logger.info(f"Experiment matrix: {total} total runs | {len(pending)} pending | {total - len(pending)} already completed.")

        results: List[ExperimentResult] = []
        for i, (config, record, query_string) in enumerate(pending, start=1):
            logger.info(
                f"[{i}/{len(pending)}] Running: {config.experiment_id} | q={record.question_id} | "
                f"lang={config.language} | mitigation={config.mitigation_enabled}"
            )
            result = self._run_one(config, record, query_string)
            self.db.save_experiment_result(result)
            results.append(result)

            if result.error:
                logger.warning(f"  -> ERROR: {result.error}")
            else:
                score_str = f"{result.faithfulness_score:.3f}" if result.faithfulness_score is not None else "N/A"
                logger.info(f"  -> OK | faithfulness={score_str} | hallucination={result.hallucination_flag}")

            # Rate-limit friendly pause between API calls
            if i < len(pending):
                time.sleep(delay_between_runs)

        logger.info(f"Experiment complete. {len(results)} runs executed.")
        return results
