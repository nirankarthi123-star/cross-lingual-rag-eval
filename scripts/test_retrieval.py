import argparse
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.embeddings.sentence_transformer import SentenceTransformerProvider
from backend.retrieval.indexer import FAISSIndexer
from backend.retrieval.searcher import VectorSearcher

def main():
    parser = argparse.ArgumentParser(description="Test RAG retrieval from the FAISS index.")
    parser.add_argument("query", type=str, help="The query string to search for.")
    parser.add_argument("-k", "--top-k", type=int, default=5, help="Number of results to return.")
    args = parser.parse_args()

    print("[INFO] Loading index and embedding model...")
    try:
        indexer = FAISSIndexer()
        indexer.load()
    except Exception as e:
        print(f"[ERROR] Failed to load index: {e}")
        print("Make sure you run scripts/build_index.py first.")
        sys.exit(1)

    provider = SentenceTransformerProvider()
    searcher = VectorSearcher(provider, indexer)
    
    print(f"\n[INFO] Searching for: '{args.query}'")
    results = searcher.retrieve(args.query, k=args.top_k)

    if not results:
        print("\n[WARN] No results found.")
        sys.exit(0)
        
    print(f"\n--- TOP {len(results)} RESULTS ---")
    for i, res in enumerate(results, 1):
        print(f"\n[{i}] Score (Cosine Similarity): {res['score']:.4f}")
        print(f"Document ID: {res['document_id']}")
        print(f"Chunk ID: {res['chunk_id']}")
        print(f"Text: {res['text']}")
        print("-" * 40)

if __name__ == "__main__":
    main()
