"""
Unit tests for Phase 8: Faithfulness Evaluation.

All LLM calls are mocked — no real API calls are made.
"""
import json
import pytest
from unittest.mock import Mock
from backend.evaluation.llm_judge import LLMFaithfulnessJudge
from backend.evaluation.models import EvaluationResult
from backend.llm.base import LLMProvider


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_judge_response(score: float, explanation: str = "Test explanation") -> str:
    return json.dumps({"faithfulness_score": score, "explanation": explanation})


class MockJudgeLLM(LLMProvider):
    """Mock LLM that returns a fixed JSON response for judge prompts."""
    def __init__(self, raw_response: str):
        self._response = raw_response

    def generate(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        return self._response


class FailingJudgeLLM(LLMProvider):
    """LLM that always raises an exception."""
    def generate(self, prompt: str, system_prompt: str = None, **kwargs) -> str:
        raise RuntimeError("Simulated API failure")


# ---------------------------------------------------------------------------
# Tests: score clamping
# ---------------------------------------------------------------------------

def test_score_above_1_is_clamped():
    judge = LLMFaithfulnessJudge(llm=MockJudgeLLM(make_judge_response(1.5)))
    result = judge.evaluate(answer="test", context="test context")
    assert result.faithfulness_score == 1.0


def test_score_below_0_is_clamped():
    judge = LLMFaithfulnessJudge(llm=MockJudgeLLM(make_judge_response(-0.3)))
    result = judge.evaluate(answer="test", context="test context")
    assert result.faithfulness_score == 0.0


def test_valid_score_is_preserved():
    judge = LLMFaithfulnessJudge(llm=MockJudgeLLM(make_judge_response(0.72)))
    result = judge.evaluate(answer="test", context="test context")
    assert result.faithfulness_score == pytest.approx(0.72)


# ---------------------------------------------------------------------------
# Tests: hallucination flag threshold (default = 0.8)
# ---------------------------------------------------------------------------

def test_hallucination_flag_set_when_score_below_threshold():
    judge = LLMFaithfulnessJudge(llm=MockJudgeLLM(make_judge_response(0.5)))
    result = judge.evaluate(answer="test", context="test context")
    assert result.hallucination_flag is True


def test_no_hallucination_when_score_at_threshold():
    # score == threshold: NOT a hallucination (boundary inclusive on passing side)
    judge = LLMFaithfulnessJudge(llm=MockJudgeLLM(make_judge_response(0.8)))
    result = judge.evaluate(answer="test", context="test context")
    assert result.hallucination_flag is False


def test_no_hallucination_when_score_above_threshold():
    judge = LLMFaithfulnessJudge(llm=MockJudgeLLM(make_judge_response(0.95)))
    result = judge.evaluate(answer="test", context="test context")
    assert result.hallucination_flag is False


# ---------------------------------------------------------------------------
# Tests: JSON parsing
# ---------------------------------------------------------------------------

def test_judge_parses_json_correctly():
    judge = LLMFaithfulnessJudge(llm=MockJudgeLLM(
        make_judge_response(0.87, "All claims are supported by the context.")
    ))
    result = judge.evaluate(answer="The sky is blue.", context="The sky appears blue due to Rayleigh scattering.")
    assert result.faithfulness_score == pytest.approx(0.87)
    assert result.explanation == "All claims are supported by the context."


def test_judge_handles_markdown_wrapped_json():
    """LLMs sometimes wrap JSON in markdown code fences."""
    wrapped = "```json\n" + make_judge_response(0.6) + "\n```"
    judge = LLMFaithfulnessJudge(llm=MockJudgeLLM(wrapped))
    result = judge.evaluate(answer="test", context="test context")
    assert result.faithfulness_score == pytest.approx(0.6)


def test_judge_returns_fallback_on_invalid_json():
    judge = LLMFaithfulnessJudge(llm=MockJudgeLLM("this is not valid json"))
    result = judge.evaluate(answer="test", context="test context")
    assert result.faithfulness_score == 0.0
    assert result.hallucination_flag is True
    assert "valid JSON" in result.explanation


# ---------------------------------------------------------------------------
# Tests: API failure and retry
# ---------------------------------------------------------------------------

def test_judge_returns_fallback_on_api_failure():
    """When the LLM always fails, the judge should return a safe fallback (score=0, flag=True)."""
    judge = LLMFaithfulnessJudge(llm=FailingJudgeLLM())
    judge.retry_delay = 0  # Disable real sleep for speed
    result = judge.evaluate(answer="test", context="test context")
    assert result.faithfulness_score == 0.0
    assert result.hallucination_flag is True
    assert "Judge failed" in result.explanation


# ---------------------------------------------------------------------------
# Tests: EvaluationResult schema
# ---------------------------------------------------------------------------

def test_evaluation_result_schema():
    result = EvaluationResult(
        faithfulness_score=0.9,
        hallucination_flag=False,
        explanation="Test",
        judge_model="openai/gpt-oss-20b",
        judge_prompt_version="v1",
    )
    assert result.faithfulness_score == 0.9
    assert result.hallucination_flag is False
