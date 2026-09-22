from pydantic import BaseModel, Field
from typing import List

class LanguageSpan(BaseModel):
    """Represents a contiguous span of text identified as a specific language."""
    start: int = Field(..., description="Start character index (inclusive).")
    end: int = Field(..., description="End character index (exclusive).")
    language: str = Field(..., description="Detected language (e.g., 'English', 'Tamil', 'Hindi').")
    text: str = Field(..., description="The substring corresponding to this span.")

class DetectionResult(BaseModel):
    """The result of a code-mix detection pass over a query."""
    is_code_mixed: bool = Field(..., description="True if multiple languages are detected.")
    languages: List[str] = Field(..., description="List of unique languages detected.")
    language_spans: List[LanguageSpan] = Field(..., description="Detailed spans of identified languages.")
    confidence: float = Field(..., description="Confidence score from 0.0 to 1.0.")
