from pydantic import BaseModel, Field
from typing import Optional

class EvaluationResult(BaseModel):
    """
    Represents the output of a faithfulness evaluation for a single RAG response.
    """
    faithfulness_score: float = Field(..., ge=0.0, le=1.0, description="Faithfulness score between 0.0 and 1.0.")
    hallucination_flag: bool = Field(..., description="True if a hallucination is detected based on the configured threshold.")
    explanation: str = Field(..., description="The judge's explanation of the score.")
    judge_model: str = Field(..., description="The LLM model used as the judge.")
    judge_prompt_version: str = Field(..., description="The version of the prompt used for evaluation.")
