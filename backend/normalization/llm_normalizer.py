import logging
from backend.normalization.base import QueryNormalizer
from backend.normalization.models import NormalizationResult
from backend.detection.models import DetectionResult
from backend.llm.base import LLMProvider
from backend.normalization.prompt import NORMALIZATION_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class LLMNormalizer(QueryNormalizer):
    """
    Uses an LLM to rewrite code-mixed queries into English.
    Implements a strict fallback mechanism if generation fails.
    """
    
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider

    def normalize(self, query: str, detection_result: DetectionResult) -> NormalizationResult:
        # If it's not code mixed (or just English), skip normalization
        if not detection_result.is_code_mixed and "English" in detection_result.languages and len(detection_result.languages) == 1:
            logger.info("Normalization skipped: Query is not code-mixed.")
            return NormalizationResult(
                original_query=query,
                normalized_query=query,
                target_language="English",
                normalization_applied=False,
                error_fallback=False
            )

        logger.info(f"Normalizing code-mixed query: {query}")
        
        try:
            # We use a very low temperature for deterministic translation
            response = self.llm.generate(
                prompt=f"Input: \"{query}\"\nOutput:",
                system_prompt=NORMALIZATION_SYSTEM_PROMPT,
                temperature=0.0,
                max_tokens=256
            )
            
            normalized_text = response.strip().strip('"\'')
            
            # Simple validation: if the model returned nothing, trigger fallback
            if not normalized_text:
                raise ValueError("LLM returned empty normalization string.")
                
            return NormalizationResult(
                original_query=query,
                normalized_query=normalized_text,
                target_language="English",
                normalization_applied=True,
                error_fallback=False
            )
            
        except Exception as e:
            logger.error(f"Normalization failed: {e}. Falling back to raw query.")
            # Fallback to original query
            return NormalizationResult(
                original_query=query,
                normalized_query=query,
                target_language="English",
                normalization_applied=False,
                error_fallback=True
            )
