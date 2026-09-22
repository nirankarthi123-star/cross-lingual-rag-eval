"""Experiment schemas for Phase 9: Complete Experiment Runner."""
from pydantic import BaseModel, Field
from typing import List, Optional


class ExperimentConfig(BaseModel):
    """
    Records the full configuration for one experimental condition.
    Fixed variables are recorded here for reproducibility.
    Only 'language' and 'mitigation_enabled' vary across conditions.
    """
    experiment_id: str = Field(..., description="Unique identifier for this experimental condition.")
    language: str = Field(..., description="Language condition: 'english', 'tamil_english', or 'hindi_english'.")
    condition_name: str = Field(..., description="Human-readable condition label: 'baseline' or 'mitigated'.")
    mitigation_enabled: bool = Field(..., description="Whether the normalization mitigation layer is active.")

    # Fixed experimental controls — recorded for reproducibility
    dataset_path: str = Field(..., description="Path to the query dataset file used.")
    embedding_model: str = Field(..., description="Embedding model identifier.")
    generator_model: str = Field(..., description="LLM model used for answer generation.")
    judge_model: str = Field(..., description="LLM model used as the faithfulness judge.")
    top_k: int = Field(..., description="Number of retrieved documents passed to the generator.")
    judge_prompt_version: str = Field(..., description="Prompt version used by the judge.")
    hallucination_threshold: float = Field(..., description="Score threshold below which hallucination_flag is set.")
    created_at: str = Field(..., description="ISO timestamp when this config was created.")


class ExperimentResult(BaseModel):
    """
    Records the complete result of a single pipeline run:
    one query × one language condition × one mitigation condition.
    """
    run_id: str = Field(..., description="Unique identifier for this individual run.")
    experiment_id: str = Field(..., description="Experiment condition this run belongs to.")
    question_id: str = Field(..., description="Question identifier from the dataset.")
    language: str = Field(..., description="Language variant used.")
    mitigation_enabled: bool = Field(..., description="Whether mitigation was enabled for this run.")

    # Query
    original_query: str = Field(..., description="The raw query string (as loaded from dataset).")
    normalized_query: Optional[str] = Field(None, description="Normalized query if mitigation was applied.")
    mitigation_applied: bool = Field(False, description="True if normalization actively changed the query.")

    # Retrieval
    retrieved_document_ids: List[str] = Field(default_factory=list, description="IDs of retrieved chunks.")
    retrieved_context: str = Field("", description="Concatenated retrieved context passed to the generator.")

    # Generation
    generated_answer: str = Field("", description="The generated answer text.")

    # Faithfulness Evaluation
    faithfulness_score: Optional[float] = Field(None, description="Judge faithfulness score [0.0–1.0].")
    hallucination_flag: Optional[bool] = Field(None, description="True if score is below hallucination threshold.")
    faithfulness_explanation: Optional[str] = Field(None, description="Judge's explanation.")

    # Provenance
    embedding_model: str = Field(..., description="Embedding model used.")
    generator_model: str = Field(..., description="Generator model used.")
    judge_model: str = Field(..., description="Judge model used.")

    # Timing
    started_at: str = Field(..., description="ISO timestamp when this run started.")
    completed_at: Optional[str] = Field(None, description="ISO timestamp when this run completed.")

    # Error tracking
    error: Optional[str] = Field(None, description="Error message if this run failed.")
