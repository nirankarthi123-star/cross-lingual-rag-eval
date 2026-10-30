import json
import logging
import re
import time
from typing import Optional

from backend.evaluation.base import FaithfulnessJudge
from backend.evaluation.models import EvaluationResult
from backend.evaluation.prompt import (
    JUDGE_SYSTEM_PROMPT,
    JUDGE_PROMPT_VERSION,
    build_judge_prompt,
)
from backend.llm.base import LLMProvider
from backend.config.settings import get_settings

logger = logging.getLogger(__name__)


class LLMFaithfulnessJudge(FaithfulnessJudge):
    def __init__(self, llm: LLMProvider):
        self.llm = llm
        self.settings = get_settings()
        self.max_retries = 3
        self.retry_delay = 2.0

    def evaluate(self, answer: str, context: str) -> EvaluationResult:
        user_prompt = build_judge_prompt(answer, context)

        for attempt in range(self.max_retries):
            try:
                response_text = self.llm.generate(
                    prompt=user_prompt,
                    system_prompt=JUDGE_SYSTEM_PROMPT,
                    temperature=self.settings.JUDGE_TEMPERATURE,
                    max_tokens=256,
                    model=self.settings.JUDGE_LLM_MODEL,
                )

                return self._parse_response(response_text)

            except Exception as e:
                logger.warning(
                    f"Judge API call failed on attempt {attempt + 1}: {e}"
                )

                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))
                else:
                    logger.error(
                        "Judge API failed after maximum retries."
                    )

                    # IMPORTANT:
                    # API failure is NOT the same as hallucination.
                    return EvaluationResult(
                        faithfulness_score=None,
                        hallucination_flag=None,
                        explanation=f"Judge unavailable: {str(e)}",
                        judge_model=self.settings.JUDGE_LLM_MODEL,
                        judge_prompt_version=JUDGE_PROMPT_VERSION,
                    )

        # Defensive fallback
        return EvaluationResult(
            faithfulness_score=None,
            hallucination_flag=None,
            explanation="Judge unavailable.",
            judge_model=self.settings.JUDGE_LLM_MODEL,
            judge_prompt_version=JUDGE_PROMPT_VERSION,
        )

    def _parse_response(self, response_text: str) -> EvaluationResult:
        """
        Parse the LLM judge response.

        Handles:
        - Normal JSON
        - JSON inside markdown code fences
        - Truncated JSON
        - Empty responses
        - Invalid JSON
        - Unexpected parsing errors

        IMPORTANT:
        Judge failures are represented as None rather than
        faithfulness=0.0 / hallucination=True.
        This prevents infrastructure failures from being
        incorrectly interpreted as hallucinations.
        """

        # ---------------------------------------------------------------
        # 1. Empty response
        # ---------------------------------------------------------------
        if not response_text or not response_text.strip():
            logger.warning(
                "Judge returned an empty response after successful API call."
            )

            return EvaluationResult(
                faithfulness_score=None,
                hallucination_flag=None,
                explanation="Judge unavailable: empty response from LLM.",
                judge_model=self.settings.JUDGE_LLM_MODEL,
                judge_prompt_version=JUDGE_PROMPT_VERSION,
            )

        try:
            # -----------------------------------------------------------
            # 2. Clean markdown code fences
            # -----------------------------------------------------------
            cleaned_text = response_text.strip()

            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]

            elif cleaned_text.startswith("```"):
                cleaned_text = cleaned_text[3:]

            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]

            cleaned_text = cleaned_text.strip()

            # -----------------------------------------------------------
            # 3. Parse JSON
            # -----------------------------------------------------------
            data = json.loads(cleaned_text)

            # -----------------------------------------------------------
            # 4. Extract score
            # -----------------------------------------------------------
            if "faithfulness_score" not in data:
                logger.warning(
                    "Judge response does not contain faithfulness_score."
                )

                return EvaluationResult(
                    faithfulness_score=None,
                    hallucination_flag=None,
                    explanation="Judge response did not contain a faithfulness score.",
                    judge_model=self.settings.JUDGE_LLM_MODEL,
                    judge_prompt_version=JUDGE_PROMPT_VERSION,
                )

            score = float(data["faithfulness_score"])

            # Clamp score to [0.0, 1.0]
            score = max(0.0, min(1.0, score))

            # -----------------------------------------------------------
            # 5. Explanation
            # -----------------------------------------------------------
            explanation = data.get(
                "explanation",
                "No explanation provided."
            )

            if explanation is None:
                explanation = "No explanation provided."

            explanation = str(explanation)

            # -----------------------------------------------------------
            # 6. Determine hallucination
            # -----------------------------------------------------------
            is_hallucination = (
                score < self.settings.HALLUCINATION_THRESHOLD
            )

            logger.info(
                f"Judge evaluation successful: "
                f"score={score}, "
                f"hallucination={is_hallucination}"
            )

            return EvaluationResult(
                faithfulness_score=score,
                hallucination_flag=is_hallucination,
                explanation=explanation,
                judge_model=self.settings.JUDGE_LLM_MODEL,
                judge_prompt_version=JUDGE_PROMPT_VERSION,
            )

        except json.JSONDecodeError as e:
            # -----------------------------------------------------------
            # 7. Recover score from truncated/malformed JSON
            # -----------------------------------------------------------
            logger.warning(
                f"Judge JSON truncated or malformed: {e}. "
                "Attempting score recovery."
            )

            score_match = re.search(
                r'"faithfulness_score"\s*:\s*([0-9]*\.?[0-9]+)',
                response_text,
            )

            if score_match:
                try:
                    recovered_score = float(score_match.group(1))

                    recovered_score = max(
                        0.0,
                        min(1.0, recovered_score)
                    )

                    is_hallucination = (
                        recovered_score
                        < self.settings.HALLUCINATION_THRESHOLD
                    )

                    logger.info(
                        f"Recovered faithfulness_score="
                        f"{recovered_score} from truncated response."
                    )

                    return EvaluationResult(
                        faithfulness_score=recovered_score,
                        hallucination_flag=is_hallucination,
                        explanation=(
                            "[Recovered from truncated judge response] "
                            + response_text[:200]
                        ),
                        judge_model=self.settings.JUDGE_LLM_MODEL,
                        judge_prompt_version=JUDGE_PROMPT_VERSION,
                    )

                except ValueError:
                    pass

            # -----------------------------------------------------------
            # 8. Could not recover score
            # -----------------------------------------------------------
            logger.error(
                "Judge returned invalid JSON and score recovery failed. "
                f"Raw response: {response_text[:300]}"
            )

            return EvaluationResult(
                faithfulness_score=None,
                hallucination_flag=None,
                explanation=(
                    "Judge unavailable: invalid JSON response "
                    "and score could not be recovered."
                ),
                judge_model=self.settings.JUDGE_LLM_MODEL,
                judge_prompt_version=JUDGE_PROMPT_VERSION,
            )

        except (TypeError, ValueError) as e:
            # -----------------------------------------------------------
            # 9. Invalid score/type
            # -----------------------------------------------------------
            logger.error(
                f"Invalid judge response value: {e}"
            )

            return EvaluationResult(
                faithfulness_score=None,
                hallucination_flag=None,
                explanation=f"Judge unavailable: invalid response value. {str(e)}",
                judge_model=self.settings.JUDGE_LLM_MODEL,
                judge_prompt_version=JUDGE_PROMPT_VERSION,
            )

        except Exception as e:
            # -----------------------------------------------------------
            # 10. Unexpected parsing error
            # -----------------------------------------------------------
            logger.error(
                f"Unexpected error parsing judge response: {e}"
            )

            return EvaluationResult(
                faithfulness_score=None,
                hallucination_flag=None,
                explanation=f"Judge unavailable: {str(e)}",
                judge_model=self.settings.JUDGE_LLM_MODEL,
                judge_prompt_version=JUDGE_PROMPT_VERSION,
            )