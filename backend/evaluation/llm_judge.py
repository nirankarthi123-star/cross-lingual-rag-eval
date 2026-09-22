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
                    max_tokens=512,
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
        try:
            # Try to parse the response as JSON. Strip potential markdown blocks.
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
            logger.error(f"Failed to parse judge JSON: {e}. Raw response: {response_text}")
            return EvaluationResult(
                faithfulness_score=0.0,
                hallucination_flag=True,
                explanation="Judge failed to return valid JSON.",
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
