from typing import Any, Dict, List
import numpy as np

from backend.embeddings.base import EmbeddingProvider
from backend.retrieval.indexer import FAISSIndexer


class VectorSearcher:
    """
    Combines an EmbeddingProvider and a loaded FAISSIndexer to execute
    top-K similarity searches over the RAG knowledge base.
    """

    def __init__(self, provider: EmbeddingProvider, indexer: FAISSIndexer):
        self.provider = provider
        self.indexer = indexer

        if self.indexer.index is None:
            raise RuntimeError("FAISS index has not been loaded. Call indexer.load() first.")

    def retrieve(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Embed the query and retrieve the top K most similar chunks.
        Returns a list of dictionaries containing chunk details and similarity score.
        """
        if not query.strip():
            return []

        # Embed query using the provider (which handles normalisation and e5 prefixing)
        query_emb = self.provider.embed_query(query)
        
        # FAISS expects 2D float32 array
        query_vector = np.array([query_emb], dtype=np.float32)

        # Search index
        # For IndexFlatIP (Inner Product), distances are actually similarities (higher is better)
        distances, indices = self.indexer.index.search(query_vector, k)

        results = []
        for i in range(k):
            idx = int(indices[0][i])
            score = float(distances[0][i])

            if idx == -1:
                # FAISS returns -1 if there are fewer than k vectors in the index
                continue

            chunk_data = self.indexer.metadata_map.get(idx)
            if chunk_data:
                results.append({
                    "chunk_id": chunk_data.get("chunk_id"),
                    "document_id": chunk_data.get("document_id"),
                    "text": chunk_data.get("chunk_text"),
                    "score": score,
                    "metadata": chunk_data.get("metadata", {})
                })

        return results
