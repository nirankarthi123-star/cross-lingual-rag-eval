import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import faiss
import numpy as np

from backend.config.settings import get_settings
from backend.retrieval.models import Chunk


class FAISSIndexer:
    """
    Manages the creation, persistence, and loading of a FAISS vector index
    and its associated chunk metadata mapping.
    Uses Inner Product (IndexFlatIP) which corresponds to Cosine Similarity 
    when the input vectors are L2-normalized.
    """

    def __init__(self, vector_store_dir: Optional[Path] = None, dimension: Optional[int] = None):
        settings = get_settings()
        self.vector_store_dir = Path(vector_store_dir) if vector_store_dir else Path(settings.VECTOR_STORE_DIR)
        self.dimension = dimension or settings.EMBEDDING_DIMENSION
        self.index_file = self.vector_store_dir / "index.faiss"
        self.map_file = self.vector_store_dir / "metadata_map.json"
        
        self.index: Optional[faiss.Index] = None
        self.metadata_map: Dict[int, dict] = {}

    def _ensure_dir(self):
        self.vector_store_dir.mkdir(parents=True, exist_ok=True)

    def build_index(self, chunks: List[Chunk], embeddings: List[List[float]]):
        """
        Create a new FAISS index from the provided chunks and their dense embeddings.
        """
        if len(chunks) != len(embeddings):
            raise ValueError(f"Mismatch: {len(chunks)} chunks vs {len(embeddings)} embeddings")

        # Initialize Inner Product index (for Cosine Similarity on normalized vectors)
        self.index = faiss.IndexFlatIP(self.dimension)
        self.metadata_map = {}

        if not chunks:
            return

        # Convert to numpy array of float32 (required by faiss)
        vectors = np.array(embeddings, dtype=np.float32)
        
        # Add to index
        self.index.add(vectors)

        # Store metadata mapping (internal faiss ID 0..N-1 maps to chunk data)
        for idx, chunk in enumerate(chunks):
            self.metadata_map[idx] = chunk.model_dump()

    def save(self):
        """Save the FAISS index and metadata map to disk."""
        if self.index is None:
            raise RuntimeError("Cannot save an empty index.")
        
        self._ensure_dir()
        
        # Save index
        faiss.write_index(self.index, str(self.index_file))
        
        # Save metadata mapping
        with open(self.map_file, "w", encoding="utf-8") as f:
            json.dump(self.metadata_map, f, ensure_ascii=False, indent=2)

    def load(self):
        """Load the FAISS index and metadata map from disk."""
        if not self.index_file.exists() or not self.map_file.exists():
            raise FileNotFoundError(f"Index or map file not found in {self.vector_store_dir}")

        self.index = faiss.read_index(str(self.index_file))
        
        with open(self.map_file, "r", encoding="utf-8") as f:
            raw_map = json.load(f)
            # JSON keys are always strings, convert back to int
            self.metadata_map = {int(k): v for k, v in raw_map.items()}
