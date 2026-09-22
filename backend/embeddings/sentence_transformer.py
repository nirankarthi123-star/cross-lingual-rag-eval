from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer

from backend.embeddings.base import EmbeddingProvider
from backend.config.settings import get_settings


class SentenceTransformerProvider(EmbeddingProvider):
    """
    Implementation of EmbeddingProvider using the sentence-transformers library.
    Specifically tuned to support the multilingual-e5-base model which requires 
    'query: ' and 'passage: ' prefixes to achieve symmetric/asymmetric retrieval.
    """

    def __init__(self, model_name: str = None):
        settings = get_settings()
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self.model = SentenceTransformer(self.model_name)
        
        # Determine if the model requires E5 prefixes
        self.is_e5 = "e5" in self.model_name.lower()

    def _normalize(self, embeddings: np.ndarray) -> List[List[float]]:
        """L2 normalize embeddings. Required for Cosine Similarity via Inner Product."""
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        # Avoid division by zero
        norms = np.where(norms == 0, 1e-10, norms)
        normalized = embeddings / norms
        return normalized.tolist()

    def embed_text(self, text: str) -> List[float]:
        # Default fallback, treats text as passage if e5
        prefix = "passage: " if self.is_e5 else ""
        formatted_text = prefix + text
        embedding = self.model.encode([formatted_text], convert_to_numpy=True)
        return self._normalize(embedding)[0]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        prefix = "passage: " if self.is_e5 else ""
        formatted_texts = [prefix + t for t in texts]
        embeddings = self.model.encode(formatted_texts, convert_to_numpy=True)
        return self._normalize(embeddings)

    def embed_query(self, query: str) -> List[float]:
        prefix = "query: " if self.is_e5 else ""
        formatted_query = prefix + query
        embedding = self.model.encode([formatted_query], convert_to_numpy=True)
        return self._normalize(embedding)[0]
