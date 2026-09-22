from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class Document(BaseModel):
    """
    Representation of an ingested raw document in the RAG corpus.
    """
    document_id: str = Field(description="Unique deterministic or random identifier for the document")
    filename: str = Field(description="Base file name of the document source")
    source: str = Field(description="Full path or origin URL/identifier of the document")
    document_type: str = Field(description="Format of the document, e.g. pdf, txt, csv, json")
    title: Optional[str] = Field(default=None, description="Document title if available")
    text: str = Field(description="Cleaned full text of the document")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary auxiliary metadata")
    ingestion_timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp of ingestion"
    )


class Chunk(BaseModel):
    """
    Representation of a discrete textual chunk sliced from a Document.
    """
    chunk_id: str = Field(description="Unique identifier for the chunk, e.g. {document_id}_c{index}")
    document_id: str = Field(description="Foreign key pointing to the source Document")
    chunk_index: int = Field(default=0, description="Sequential index of the chunk within the document")
    chunk_text: str = Field(description="Textual payload of the chunk")
    char_start: int = Field(default=0, description="Starting character offset in the source document text")
    char_end: int = Field(default=0, description="Ending character offset in the source document text")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata dictionary inherited from Document and augmented with chunk attributes"
    )
