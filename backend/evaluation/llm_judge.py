import json
import logging
import time
from typing import Optional

from backend.evaluation.base import FaithfulnessJudge
from backend.evaluation.models import EvaluationResult
from backend.evaluation.prompt import JUDGE_SYSTEM_PROMPT, JUDGE_PROMPT_VERSION, build_judge_prompt
from backend.llm.base import LLMProvider
from backend.config.settings import get_settings

logger = logging.getLogger(__name__)

class LLMFaithfulnessJudge(FaithfulnessJudge):
    def __init__(self, llm: LLMProvider):
        self.llm = llm
        self.settings = get_settings()
        self.max_retries = 3
        self.retry_delay = 2.0  # seconds

    def evaluate(self, answer: str, context: str) -> EvaluationResult:
        user_prompt = build_judge_prompt(answer, context)
        
        for attempt in range(self.max_retries):
            try:
                response_text = self.llm.generate(
                    prompt=user_prompt,
                    system_prompt=JUDGE_SYSTEM_PROMPT,
                    temperature=self.settings.JUDGE_TEMPERATURE,
                    max_tokens=256,   # increased: short JSON payload needs ~80 tokens; 256 gives ample headroom
                    model=self.settings.JUDGE_LLM_MODEL,  # judge uses its own model
                )
                
                return self._parse_response(response_text)
                
            except Exception as e:
                logger.warning(f"Judge API call failed on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    logger.error("Judge API failed after max retries.")
                    # Fallback on failure
                    return EvaluationResult(
                        faithfulness_score=0.0,
                        hallucination_flag=True,
                        explanation=f"Judge failed: {str(e)}",
                        judge_model=self.settings.JUDGE_LLM_MODEL,
                        judge_prompt_version=JUDGE_PROMPT_VERSION
                    )
                    
    def _parse_response(self, response_text: str) -> EvaluationResult:
        import re

        # ------------------------------------------------------------------
        # Guard: empty or whitespace-only response from the API.
        # This happens when Groq returns HTTP 200 with no body content after
        # a 429 retry — json.loads would raise "Expecting value: line 1 col 1"
        # which is confusing.  Catch it explicitly with a clear log message.
        # ------------------------------------------------------------------
        if not response_text or not response_text.strip():
            logger.warning("Judge returned an empty response after successful API call.")
            return EvaluationResult(
                faithfulness_score=0.0,
                hallucination_flag=True,
                explanation="Judge returned an empty response.",
                judge_model=self.settings.JUDGE_LLM_MODEL,
                judge_prompt_version=JUDGE_PROMPT_VERSION
            )

        try:
            # Strip potential markdown code fences.
            cleaned_text = response_text.strip()
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]

            cleaned_text = cleaned_text.strip()
            data = json.loads(cleaned_text)

            score = float(data.get("faithfulness_score", 0.0))
            # Clamp to 0.0 - 1.0
            score = max(0.0, min(1.0, score))

            explanation = data.get("explanation", "No explanation provided.")

            # Determine hallucination flag based on threshold
            is_hallucination = score < self.settings.HALLUCINATION_THRESHOLD

            return EvaluationResult(
                faithfulness_score=score,
                hallucination_flag=is_hallucination,
                explanation=explanation,
                judge_model=self.settings.JUDGE_LLM_MODEL,
                judge_prompt_version=JUDGE_PROMPT_VERSION
            )

        except json.JSONDecodeError as e:
            # ---------------------------------------------------------------
            # Recovery: the judge response was truncated mid-string (a common
            # failure when max_tokens is tight).  Attempt to salvage the
            # faithfulness_score from the partial JSON via regex so we do NOT
            # silently return a false 0.0 score.
            # ---------------------------------------------------------------
            logger.warning(f"Judge JSON truncated or malformed: {e}. Attempting score recovery.")
            score_match = re.search(r'"faithfulness_score"\s*:\s*([0-9]*\.?[0-9]+)', response_text)
            if score_match:
                try:
                    recovered_score = float(score_match.group(1))
                    recovered_score = max(0.0, min(1.0, recovered_score))
                    logger.info(f"Recovered faithfulness_score={recovered_score} from truncated judge response.")
                    is_hallucination = recovered_score < self.settings.HALLUCINATION_THRESHOLD
                    return EvaluationResult(
                        faithfulness_score=recovered_score,
                        hallucination_flag=is_hallucination,
                        explanation="[Recovered from truncated response] " + response_text[:200],
                        judge_model=self.settings.JUDGE_LLM_MODEL,
                        judge_prompt_version=JUDGE_PROMPT_VERSION
                    )
                except ValueError:
                    pass

            # Could not recover score — fall back safely.
            logger.error(f"Judge returned invalid JSON and score recovery failed. Raw: {response_text[:300]}")
            return EvaluationResult(
                faithfulness_score=0.0,
                hallucination_flag=True,
                explanation="Judge returned invalid JSON and score could not be recovered.",
                judge_model=self.settings.JUDGE_LLM_MODEL,
                judge_prompt_version=JUDGE_PROMPT_VERSION
            )
        except Exception as e:
            logger.error(f"Unexpected error parsing judge response: {e}")
            return EvaluationResult(
                faithfulness_score=0.0,
                hallucination_flag=True,
                explanation=f"Parse error: {str(e)}",
                judge_model=self.settings.JUDGE_LLM_MODEL,
                judge_prompt_version=JUDGE_PROMPT_VERSION
            )
