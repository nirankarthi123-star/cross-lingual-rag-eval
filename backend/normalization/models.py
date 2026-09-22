from pydantic import BaseModel, Field

class NormalizationResult(BaseModel):
    """The result of normalizing a potentially code-mixed query."""
    original_query: str = Field(..., description="The raw input query.")
    normalized_query: str = Field(..., description="The rewritten canonical query.")
    target_language: str = Field(..., description="The language it was normalized to (e.g., 'English').")
    normalization_applied: bool = Field(..., description="True if the normalizer actively modified the query.")
    error_fallback: bool = Field(False, description="True if normalization failed and fell back to the original query.")
