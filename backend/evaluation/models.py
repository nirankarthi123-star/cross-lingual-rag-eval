from typing import Optional

from pydantic import BaseModel, Field


class EvaluationResult(BaseModel):
    """
    Represents the output of a faithfulness evaluation
    for a single RAG response.

    A None score/flag indicates that the LLM judge was
    unavailable or returned an unusable response.
    """

    faithfulness_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description=(
            "Faithfulness score between 0.0 and 1.0. "
            "None if the judge was unavailable."
        ),
    )

    hallucination_flag: Optional[bool] = Field(
        default=None,
        description=(
            "True if a hallucination is detected based on "
            "the configured threshold. None if the judge "
            "was unavailable."
        ),
    )

    explanation: str = Field(
        ...,
        description="The judge's explanation of the score.",
    )

    judge_model: str = Field(
        ...,
        description="The LLM model used as the judge.",
    )

    judge_prompt_version: str = Field(
        ...,
        description="The version of the prompt used for evaluation.",
    )