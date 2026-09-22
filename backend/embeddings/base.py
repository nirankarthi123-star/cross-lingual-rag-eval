from abc import ABC, abstractmethod
from typing import List

class EmbeddingProvider(ABC):
    """
    Abstract base class for all embedding generation models.
    Provides standard interface for embedding queries and documents.
    """

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Embed a single arbitrary string into a dense vector."""
        pass

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a batch of document texts.
        Implementations should handle appropriate prefixing (e.g. 'passage: ' for e5 models).
        """
        pass

    @abstractmethod
    def embed_query(self, query: str) -> List[float]:
        """
        Embed a single search query.
        Implementations should handle appropriate prefixing (e.g. 'query: ' for e5 models).
        """
        pass
