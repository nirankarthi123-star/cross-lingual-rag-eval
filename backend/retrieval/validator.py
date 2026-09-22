from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
from backend.retrieval.models import Chunk, Document
from backend.retrieval.storage import ProcessedStorage


@dataclass
class DatasetStats:
    num_documents: int = 0
    num_chunks: int = 0
    empty_documents: int = 0
    empty_chunks: int = 0
    avg_chunk_length: float = 0.0
    min_chunk_length: int = 0
    max_chunk_length: int = 0
    document_types: Dict[str, int] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    def print_summary(self) -> None:
        """Pretty print dataset statistics to console."""
        print("=" * 60)
        print(" DATASET INGESTION VALIDATION REPORT")
        print("=" * 60)
        print(f"Total Documents Ingested : {self.num_documents}")
        print(f"Total Chunks Generated   : {self.num_chunks}")
        print(f"Empty Documents          : {self.empty_documents}")
        print(f"Empty Chunks             : {self.empty_chunks}")
        print(f"Average Chunk Length     : {self.avg_chunk_length:.1f} chars")
        print(f"Min Chunk Length         : {self.min_chunk_length} chars")
        print(f"Max Chunk Length         : {self.max_chunk_length} chars")
        print("Document Types:")
        for doc_type, count in self.document_types.items():
            print(f"  - {doc_type}: {count}")
        if self.errors:
            print("Validation Errors/Warnings:")
            for err in self.errors:
                print(f"  [!] {err}")
        else:
            print("Validation Status        : PASS (All checks valid)")
        print("=" * 60)


def validate_dataset(
    documents: Optional[List[Document]] = None,
    chunks: Optional[List[Chunk]] = None,
    processed_dir: Optional[Path] = None,
) -> DatasetStats:
    """
    Validate processed documents and chunks in-memory or from storage.
    """
    if (documents is None or chunks is None) and processed_dir is not None:
        storage = ProcessedStorage(processed_dir)
        documents = storage.load_documents() if documents is None else documents
        chunks = storage.load_chunks() if chunks is None else chunks

    docs = documents or []
    chk_list = chunks or []

    stats = DatasetStats()
    stats.num_documents = len(docs)
    stats.num_chunks = len(chk_list)

    # Document-level checks
    for doc in docs:
        stats.document_types[doc.document_type] = stats.document_types.get(doc.document_type, 0) + 1
        if not doc.text or not doc.text.strip():
            stats.empty_documents += 1
            stats.errors.append(f"Document '{doc.document_id}' ({doc.filename}) has empty text content.")

    # Chunk-level checks
    chunk_lengths: List[int] = []
    for chk in chk_list:
        text_len = len(chk.chunk_text.strip())
        if text_len == 0:
            stats.empty_chunks += 1
            stats.errors.append(f"Chunk '{chk.chunk_id}' is empty.")
        else:
            chunk_lengths.append(text_len)

    if chunk_lengths:
        stats.avg_chunk_length = sum(chunk_lengths) / len(chunk_lengths)
        stats.min_chunk_length = min(chunk_lengths)
        stats.max_chunk_length = max(chunk_lengths)
    else:
        stats.avg_chunk_length = 0.0
        stats.min_chunk_length = 0
        stats.max_chunk_length = 0

    return stats
