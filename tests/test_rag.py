import pytest
from unittest.mock import Mock

from backend.rag.service import RAGService
from backend.api.schemas import RAGQueryResponse
from backend.llm.base import LLMProvider

class MockLLMProvider(LLMProvider):
    def generate(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        # Simulate LLM taking the context and answering
        if "unable to answer" in prompt.lower():
            return "I cannot answer this question based on the provided context."
        return "This is a mocked answer based on the context."

@pytest.fixture
def mock_searcher():
    searcher = Mock()
    searcher.retrieve.return_value = [
        {
            "chunk_id": "test1",
            "document_id": "doc1",
            "text": "This is a retrieved test document.",
            "score": 0.95,
            "metadata": {}
        },
        {
            "chunk_id": "test2",
            "document_id": "doc2",
            "text": "Another piece of retrieved context.",
            "score": 0.82,
            "metadata": {}
        }
    ]
    return searcher

def test_rag_service_answer(mock_searcher):
    llm = MockLLMProvider()
    service = RAGService(searcher=mock_searcher, llm=llm)
    
    response = service.answer_query("test query")
    
    assert isinstance(response, RAGQueryResponse)
    assert response.query == "test query"
    assert response.answer == "This is a mocked answer based on the context."
    assert len(response.retrieved_documents) == 2
    assert response.retrieved_documents[0].chunk_id == "test1"
    assert "This is a retrieved test document." in response.context

def test_rag_service_empty_retrieval():
    searcher = Mock()
    searcher.retrieve.return_value = []
    
    llm = MockLLMProvider()
    service = RAGService(searcher=searcher, llm=llm)
    
    response = service.answer_query("unable to answer query")
    assert response.answer == "I cannot answer this question based on the provided context."
    assert len(response.retrieved_documents) == 0
