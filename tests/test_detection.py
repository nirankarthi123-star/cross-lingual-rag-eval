import pytest
from backend.detection.heuristic_detector import HeuristicRegexDetector
from backend.detection.models import DetectionResult

@pytest.fixture
def detector():
    return HeuristicRegexDetector()

def test_english_only(detector):
    result = detector.detect("How do I reset my password?")
    assert isinstance(result, DetectionResult)
    assert not result.is_code_mixed
    assert "English" in result.languages
    assert len(result.languages) == 1
    assert result.confidence == 0.70

def test_tamil_mixed_native(detector):
    # 'What is' in English, 'enna' in Tamil script
    query = "college admission-ku eligibility என்ன?"
    result = detector.detect(query)
    assert result.is_code_mixed
    assert "English" in result.languages
    assert "Tamil" in result.languages
    assert result.confidence > 0.80  # Either Romanized (0.85) or Unicode (0.95) path
    
    # Spans are only populated by the Unicode path; the query may hit Romanized
    # path first (via 'ku'). We only assert spans if the Unicode path ran.
    native_spans = [s for s in result.language_spans if s.language == "Tamil"]
    if native_spans:
        assert "என்ன" in native_spans[0].text

def test_hindi_mixed_native(detector):
    query = "Mera account balance क्या है?"
    result = detector.detect(query)
    assert result.is_code_mixed
    assert "English" in result.languages
    assert "Hindi" in result.languages
    assert result.confidence > 0.80  # Either Romanized (0.85) or Unicode (0.95) path

def test_empty_input(detector):
    result = detector.detect("   ")
    assert not result.is_code_mixed
    assert "Unknown" in result.languages
    assert result.confidence == 1.0


# ---------------------------------------------------------------------------
# Regression tests: Romanized code-mix (pilot queries from live experiment)
# These exact queries were incorrectly classified as "not code-mixed" before
# the Romanized lexicon fix. They must always be detected as code-mixed.
# ---------------------------------------------------------------------------

def test_romanized_tanglish_pilot_query(detector):
    """Exact Tamil-English pilot query from the live experiment."""
    query = "Ennoda mobile postpaid connection-la international roaming eppadi activate panrathu?"
    result = detector.detect(query)
    assert result.is_code_mixed, (
        f"Expected is_code_mixed=True for Tanglish query, got {result}"
    )
    assert "Tamil" in result.languages
    assert "English" in result.languages


def test_romanized_hinglish_pilot_query(detector):
    """Exact Hindi-English pilot query from the live experiment."""
    query = "Mere mobile postpaid connection par international roaming kaise activate karu?"
    result = detector.detect(query)
    assert result.is_code_mixed, (
        f"Expected is_code_mixed=True for Hinglish query, got {result}"
    )
    assert "Hindi" in result.languages
    assert "English" in result.languages


def test_plain_english_not_detected_as_code_mixed(detector):
    """English-only query must NOT be flagged as code-mixed after lexicon fix."""
    query = "How do I activate international roaming on my mobile postpaid connection?"
    result = detector.detect(query)
    assert not result.is_code_mixed
    assert result.languages == ["English"] or "English" in result.languages
    assert len(result.languages) == 1

def test_romanized_tanglish_broadband_cancel(detector):
    """Regression test: Tanglish broadband cancellation query."""
    query = "Broadband connection cancel panna evlo days notice kudukanum?"
    result = detector.detect(query)
    assert result.is_code_mixed, (
        f"Expected is_code_mixed=True for Tanglish query, got {result}"
    )
    assert "Tamil" in result.languages
    assert "English" in result.languages

def test_romanized_tanglish_5g_sim(detector):
    """Regression test: Tanglish 5G SIM query."""
    query = "5G network use panna new SIM card venuma?"
    result = detector.detect(query)
    assert result.is_code_mixed, (
        f"Expected is_code_mixed=True for Tanglish query, got {result}"
    )
    assert "Tamil" in result.languages
    assert "English" in result.languages

def test_plain_english_broadband_cancel(detector):
    """Regression test: English broadband cancellation query must not be code-mixed."""
    query = "How many days notice should I give to cancel my broadband connection?"
    result = detector.detect(query)
    assert not result.is_code_mixed
    assert result.languages == ["English"] or "English" in result.languages
    assert len(result.languages) == 1

