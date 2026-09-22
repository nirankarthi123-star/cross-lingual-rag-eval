import sys
import json
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from backend.retrieval.indexer import FAISSIndexer
from backend.retrieval.searcher import VectorSearcher
from backend.embeddings.sentence_transformer import SentenceTransformerProvider
from backend.rag.service import RAGService
from tests.test_rag import MockLLMProvider

def main():
    query = "How do I reset my password?"
    print(f"Mocking a POST request to /api/rag/query with payload:")
    print(json.dumps({"query": query}, indent=2))
    print("\nProcessing (using Mock LLM)...\n")

    indexer = FAISSIndexer()
    indexer.load()
    
    provider = SentenceTransformerProvider()
    searcher = VectorSearcher(provider, indexer)
    llm = MockLLMProvider()
    
    service = RAGService(searcher, llm)
    response = service.answer_query(query)
    
    print("Response:")
    print(response.model_dump_json(indent=2))

if __name__ == "__main__":
    main()
