from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

class QueryRecord(BaseModel):
    """
    Represents a single query with three language variants.
    All variants must represent the exact same underlying information need.
    """
    question_id: str = Field(..., description="Unique identifier for the query record.")
    domain: str = Field(..., description="Domain of the query (e.g., Telecom, Banking).")
    
    # Query Variants
    english: str = Field(..., description="Base English query.")
    tamil_english: str = Field(..., description="Intra-sentential code-mixed Tamil-English query.")
    hindi_english: str = Field(..., description="Intra-sentential code-mixed Hindi-English query.")
    
    # Metadata
    script_type: str = Field(..., description="Script type (e.g., 'Romanized' or 'Native').")
    category: Optional[str] = Field(None, description="Optional categorization (e.g., Roaming, Billing).")
    expected_document_ids: Optional[List[str]] = Field(default_factory=list, description="IDs of expected documents holding the answer.")
    difficulty: Optional[str] = Field(None, description="Optional subjective difficulty (e.g., 'Easy', 'Hard').")

    @field_validator('english', 'tamil_english', 'hindi_english')
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Query string cannot be empty or just whitespace.")
        return v.strip()
