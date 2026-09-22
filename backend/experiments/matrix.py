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


def generate_configs(dataset_path: str) -> List[ExperimentConfig]:
    """
    Generate the 6 ExperimentConfig objects (one per condition).
    All fixed controls are read from settings.
    """
    settings = get_settings()
    created_at = datetime.now(timezone.utc).isoformat()
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
                judge_model=settings.JUDGE_LLM_MODEL,
                top_k=settings.RAG_TOP_K,
                judge_prompt_version=settings.JUDGE_PROMPT_VERSION,
                hallucination_threshold=settings.HALLUCINATION_THRESHOLD,
                created_at=created_at,
            ))

    return configs


# Type alias for clarity
MatrixRow = Tuple[ExperimentConfig, QueryRecord, str]  # (config, record, query_string)


def generate_matrix(
    query_records: List[QueryRecord],
    dataset_path: str,
    languages: List[str] = None,
    mitigation_filter: str = None,  # "on", "off", or None (both)
) -> List[MatrixRow]:
    """
    Generate the full experiment matrix as a flat list of runs.

    Args:
        query_records: Loaded query records from the dataset.
        dataset_path: Path string used to record provenance.
        languages: Optional filter list of language conditions.
        mitigation_filter: Optional "on" or "off" to filter mitigation conditions.

    Returns:
        List of (ExperimentConfig, QueryRecord, query_string) tuples.
    """
    configs = generate_configs(dataset_path)

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
