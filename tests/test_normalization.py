import pytest
from unittest.mock import Mock
from backend.rag.service import RAGService
from backend.normalization.llm_normalizer import LLMNormalizer
from backend.detection.heuristic_detector import HeuristicRegexDetector
from tests.test_rag import MockLLMProvider

class NormalizerMockLLMProvider(MockLLMProvider):
    def generate(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        # If it's a normalization prompt
        if system_prompt and "translate and rewrite" in system_prompt.lower():
            if "college admission-ku eligibility என்ன" in prompt:
                return "What is the eligibility for college admission?"
            elif "fail_test" in prompt:
                # Simulate a failure by returning empty string
                return ""
            else:
                return "Normalized query fallback"
        
        # Otherwise, handle normal RAG answer generation
        return "This is a mocked answer based on the context."

@pytest.fixture
def rag_service():
    searcher = Mock()
    searcher.retrieve.return_value = []
    
    llm = NormalizerMockLLMProvider()
    detector = HeuristicRegexDetector()
    normalizer = LLMNormalizer(llm)
    return RAGService(searcher, llm, detector, normalizer)

def test_mitigation_off_uses_raw_query(rag_service):
    # Test English baseline
    response = rag_service.answer_query("How do I activate roaming?", mitigation_enabled=False)
    assert not response.mitigation_applied
    assert response.normalized_query is None

def test_mitigation_on_with_english_skips_normalization(rag_service):
    # Test English but with mitigation ON (should skip because detector sees no code-mixing)
    response = rag_service.answer_query("How do I activate roaming?", mitigation_enabled=True)
    assert not response.mitigation_applied
    assert response.normalized_query is None

def test_mitigation_on_with_code_mix_normalizes(rag_service):
    # Test code-mixed string with mitigation ON
    query = "college admission-ku eligibility என்ன?"
    response = rag_service.answer_query(query, mitigation_enabled=True)
    
    assert response.mitigation_applied
    assert response.normalized_query == "What is the eligibility for college admission?"
    assert response.query == query

def test_mitigation_fallback_on_llm_failure(rag_service):
    # Test fallback behavior when the normalizer throws an error or returns empty
    # The detector will flag this as Tamil (என்ன) + English (fail_test)
    query = "fail_test என்ன?"
    response = rag_service.answer_query(query, mitigation_enabled=True)
    
    # Mitigation should not be applied due to fallback
    assert not response.mitigation_applied
    assert response.normalized_query is None
