"""
Embeddings package for converting textual chunks to dense vector representations.
Modular design allows swapping multilingual-e5 with other models like mBERT or HingBERT.
"""

from backend.embeddings.base import EmbeddingProvider
from backend.embeddings.sentence_transformer import SentenceTransformerProvider

__all__ = [
    "EmbeddingProvider",
    "SentenceTransformerProvider",
]
