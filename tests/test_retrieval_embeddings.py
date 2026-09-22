import pytest
from pathlib import Path
import numpy as np

from backend.embeddings.sentence_transformer import SentenceTransformerProvider
from backend.retrieval.indexer import FAISSIndexer
from backend.retrieval.searcher import VectorSearcher
from backend.retrieval.models import Chunk


@pytest.fixture
def dummy_provider():
    """Returns a provider using a very small model for fast testing."""
    return SentenceTransformerProvider(model_name="all-MiniLM-L6-v2")

@pytest.fixture
def temp_vector_store(tmp_path):
    return tmp_path / "vector_store"

@pytest.fixture
def sample_chunks():
    return [
        Chunk(document_id="doc1", chunk_id="chunk1", chunk_text="This is a test chunk about UPI.", chunk_index=0),
        Chunk(document_id="doc2", chunk_id="chunk2", chunk_text="Another test chunk regarding banking.", chunk_index=0),
        Chunk(document_id="doc3", chunk_id="chunk3", chunk_text="Random text not related to finance.", chunk_index=0),
    ]

def test_embedding_generation(dummy_provider):
    query_emb = dummy_provider.embed_query("test query")
    assert isinstance(query_emb, list)
    assert len(query_emb) == dummy_provider.model.get_sentence_embedding_dimension()
    
    # Check normalization (L2 norm should be close to 1.0)
    norm = np.linalg.norm(query_emb)
    assert pytest.approx(norm, 0.0001) == 1.0

def test_faiss_indexing_and_saving(temp_vector_store, dummy_provider, sample_chunks):
    texts = [c.chunk_text for c in sample_chunks]
    embeddings = dummy_provider.embed_documents(texts)
    
    indexer = FAISSIndexer(vector_store_dir=temp_vector_store, dimension=len(embeddings[0]))
    indexer.build_index(sample_chunks, embeddings)
    
    assert indexer.index.ntotal == 3
    assert len(indexer.metadata_map) == 3
    
    indexer.save()
    assert (temp_vector_store / "index.faiss").exists()
    assert (temp_vector_store / "metadata_map.json").exists()

def test_vector_searcher(temp_vector_store, dummy_provider, sample_chunks):
    # Setup index
    texts = [c.chunk_text for c in sample_chunks]
    embeddings = dummy_provider.embed_documents(texts)
    indexer = FAISSIndexer(vector_store_dir=temp_vector_store, dimension=len(embeddings[0]))
    indexer.build_index(sample_chunks, embeddings)
    
    searcher = VectorSearcher(provider=dummy_provider, indexer=indexer)
    
    # Search for something related to UPI
    results = searcher.retrieve("What is UPI?", k=2)
    assert len(results) == 2
    
    # The first result should be the chunk containing "UPI"
    assert results[0]["chunk_id"] == "chunk1"
    assert results[0]["score"] <= 1.0  # Cosine similarity max is 1.0
