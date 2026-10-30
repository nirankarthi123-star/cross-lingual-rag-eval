"""
Experiment matrix generation for the 3×2 design.

Generates all (ExperimentConfig, QueryRecord, query_string) tuples
for a given dataset, producing 6 conditions × N queries runs.
"""
from datetime import datetime, timezone
from typing import List, Tuple

from backend.experiments.models import ExperimentConfig
from backend.dataset.schemas import QueryRecord
from backend.config.settings import get_settings

# The 6 experimental conditions
LANGUAGES = ["english", "tamil_english", "hindi_english"]
MITIGATION_CONDITIONS = [
    {"condition_name": "baseline",  "mitigation_enabled": False},
    {"condition_name": "mitigated", "mitigation_enabled": True},
]


def get_language_variant(record: QueryRecord, language: str) -> str:
    """Extract the correct query string for a given language condition."""
    if language == "english":
        return record.english
    elif language == "tamil_english":
        return record.tamil_english
    elif language == "hindi_english":
        return record.hindi_english
    else:
        raise ValueError(f"Unknown language condition: '{language}'. "
                         f"Expected one of: {LANGUAGES}")


def make_experiment_id(language: str, condition_name: str) -> str:
    """Generate a deterministic, human-readable experiment ID."""
    return f"{language}_{condition_name}"


def generate_configs(
    dataset_path: str,
    corpus_manifest_hash: Optional[str] = None,
    dataset_hash: Optional[str] = None,
) -> List[ExperimentConfig]:
    """
    Generate the 6 ExperimentConfig objects (one per condition).
    All fixed controls and reproducibility metadata are recorded.
    """
    import hashlib
    import json
    from pathlib import Path
    from backend.rag.prompt import SYSTEM_PROMPT as RAG_SYSTEM_PROMPT
    from backend.evaluation.prompt import JUDGE_SYSTEM_PROMPT
    from backend.normalization.prompt import NORMALIZATION_SYSTEM_PROMPT

    settings = get_settings()
    created_at = datetime.now(timezone.utc).isoformat()

    # Compute prompt hashes
    rag_prompt_hash = hashlib.sha256(RAG_SYSTEM_PROMPT.encode("utf-8")).hexdigest()
    judge_prompt_hash = hashlib.sha256(JUDGE_SYSTEM_PROMPT.encode("utf-8")).hexdigest()
    norm_prompt_hash = hashlib.sha256(NORMALIZATION_SYSTEM_PROMPT.encode("utf-8")).hexdigest()

    # Load corpus manifest hash if not provided
    if not corpus_manifest_hash:
        manifest_p = Path("data/processed/corpus_manifest.json")
        if manifest_p.exists():
            try:
                with open(manifest_p, "r", encoding="utf-8") as f:
                    manifest_data = json.load(f)
                    corpus_manifest_hash = manifest_data.get("corpus_hash")
            except Exception:
                pass

    # Compute dataset hash if not provided
    if not dataset_hash:
        d_p = Path(dataset_path)
        if d_p.exists():
            try:
                h = hashlib.sha256()
                with open(d_p, "rb") as f:
                    while chunk := f.read(65536):
                        h.update(chunk)
                dataset_hash = h.hexdigest()
            except Exception:
                pass

    normalizer_model = getattr(settings, "NORMALIZER_LLM_MODEL", settings.LLM_MODEL)

    configs = []
    for lang in LANGUAGES:
        for cond in MITIGATION_CONDITIONS:
            configs.append(ExperimentConfig(
                experiment_id=make_experiment_id(lang, cond["condition_name"]),
                language=lang,
                condition_name=cond["condition_name"],
                mitigation_enabled=cond["mitigation_enabled"],
                dataset_path=dataset_path,
                embedding_model=settings.EMBEDDING_MODEL,
                generator_model=settings.LLM_MODEL,
                normalizer_model=normalizer_model,
                judge_model=settings.JUDGE_LLM_MODEL,
                top_k=settings.RAG_TOP_K,
                judge_prompt_version=settings.JUDGE_PROMPT_VERSION,
                hallucination_threshold=settings.HALLUCINATION_THRESHOLD,
                created_at=created_at,
                corpus_manifest_hash=corpus_manifest_hash,
                dataset_hash=dataset_hash,
                chunk_size=settings.DEFAULT_CHUNK_SIZE,
                chunk_overlap=settings.DEFAULT_CHUNK_OVERLAP,
                temperature=settings.LLM_TEMPERATURE,
                rag_prompt_hash=rag_prompt_hash,
                judge_prompt_hash=judge_prompt_hash,
                normalizer_prompt_hash=norm_prompt_hash,
                detector_version="v1-two-pass-heuristic",
            ))

    return configs


# Type alias for clarity
MatrixRow = Tuple[ExperimentConfig, QueryRecord, str]  # (config, record, query_string)


def generate_matrix(
    query_records: List[QueryRecord],
    dataset_path: str,
    languages: List[str] = None,
    mitigation_filter: str = None,  # "on", "off", or None (both)
    corpus_manifest_hash: Optional[str] = None,
    dataset_hash: Optional[str] = None,
) -> List[MatrixRow]:
    """
    Generate the full experiment matrix as a flat list of runs.

    Args:
        query_records: Loaded query records from the dataset.
        dataset_path: Path string used to record provenance.
        languages: Optional filter list of language conditions.
        mitigation_filter: Optional "on" or "off" to filter mitigation conditions.
        corpus_manifest_hash: Optional SHA-256 hash of corpus manifest.
        dataset_hash: Optional SHA-256 hash of query dataset.

    Returns:
        List of (ExperimentConfig, QueryRecord, query_string) tuples.
    """
    configs = generate_configs(
        dataset_path=dataset_path,
        corpus_manifest_hash=corpus_manifest_hash,
        dataset_hash=dataset_hash,
    )

    # Apply filters
    if languages:
        configs = [c for c in configs if c.language in languages]
    if mitigation_filter == "on":
        configs = [c for c in configs if c.mitigation_enabled]
    elif mitigation_filter == "off":
        configs = [c for c in configs if not c.mitigation_enabled]

    matrix: List[MatrixRow] = []
    for config in configs:
        for record in query_records:
            query_string = get_language_variant(record, config.language)
            matrix.append((config, record, query_string))

    return matrix
