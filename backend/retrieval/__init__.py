"""
Retrieval and document processing module.
Provides loaders, cleaner, chunker, models, and storage for knowledge base ingestion.
"""

from backend.retrieval.models import Document, Chunk
from backend.retrieval.cleaner import clean_text
from backend.retrieval.loaders import (
    BaseLoader,
    TXTLoader,
    PDFLoader,
    CSVLoader,
    JSONLoader,
    LoaderRegistry,
    DocumentLoadingError,
    UnsupportedFileTypeError,
)
from backend.retrieval.chunker import TextChunker
from backend.retrieval.storage import ProcessedStorage
from backend.retrieval.indexer import FAISSIndexer
from backend.retrieval.searcher import VectorSearcher

__all__ = [
    "Document",
    "Chunk",
    "clean_text",
    "BaseLoader",
    "TXTLoader",
    "PDFLoader",
    "CSVLoader",
    "JSONLoader",
    "LoaderRegistry",
    "DocumentLoadingError",
    "UnsupportedFileTypeError",
    "TextChunker",
    "ProcessedStorage",
    "FAISSIndexer",
    "VectorSearcher",
]
