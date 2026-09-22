import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.config.settings import get_settings
from backend.retrieval.storage import ProcessedStorage
from backend.embeddings.sentence_transformer import SentenceTransformerProvider
from backend.retrieval.indexer import FAISSIndexer

def main():
    parser = argparse.ArgumentParser(description="Build FAISS index from processed chunks.")
    args = parser.parse_args()

    settings = get_settings()
    
    print(f"[INFO] Initializing EmbeddingProvider ({settings.EMBEDDING_MODEL})...")
    print("[INFO] (This may take a moment to download weights on first run)")
    provider = SentenceTransformerProvider()

    print("[INFO] Loading chunks from storage...")
    storage = ProcessedStorage(settings.PROCESSED_DIR)
    chunks = storage.load_chunks()
    
    if not chunks:
        print("[WARN] No chunks found. Have you run ingest_documents.py yet?")
        sys.exit(1)
        
    print(f"[INFO] Found {len(chunks)} chunks.")

    print("[INFO] Generating embeddings (this may take a while)...")
    texts = [chunk.chunk_text for chunk in chunks]
    embeddings = provider.embed_documents(texts)
    
    print("[INFO] Building FAISS index...")
    indexer = FAISSIndexer()
    indexer.build_index(chunks, embeddings)
    
    print("[INFO] Saving index to disk...")
    indexer.save()
    
    print(f"[SUCCESS] Index built and saved to {indexer.vector_store_dir}")

if __name__ == "__main__":
    main()
