from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class RAGQueryRequest(BaseModel):
    query: str = Field(..., description="The user's query (potentially code-mixed).")
    mitigation_enabled: Optional[bool] = Field(
        None, 
        description="Override the global MITIGATION_ENABLED setting. True routes through detection/normalization."
    )
    evaluate_faithfulness: bool = Field(
        False,
        description="If True, run the LLM-as-judge faithfulness evaluation after generation."
    )

class RetrievedDocument(BaseModel):
    chunk_id: str
    document_id: str
    text: str
    score: float
    metadata: Dict[str, Any]

class RAGQueryResponse(BaseModel):
    query: str
    normalized_query: Optional[str] = Field(None, description="The normalized query used for retrieval, if mitigation was applied.")
    mitigation_applied: bool = Field(False, description="True if normalization actively modified the query.")
    answer: str
    retrieved_documents: List[RetrievedDocument]
    context: str
    model: str
    # Optional faithfulness evaluation fields
    faithfulness_score: Optional[float] = Field(None, description="Score between 0.0–1.0 from the LLM judge.")
    hallucination_flag: Optional[bool] = Field(None, description="True if the faithfulness score is below the configured threshold.")
    faithfulness_explanation: Optional[str] = Field(None, description="Explanation from the faithfulness judge.")

class DetectionRequest(BaseModel):
    query: str = Field(..., description="The raw query string to analyze for code-mixing.")

