from abc import ABC, abstractmethod
from typing import Optional

class LLMProvider(ABC):
    """
    Abstract base class for all text generation LLMs.
    """

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """
        Generates text given a prompt.
        
        Args:
            prompt: The main user prompt or instruction.
            system_prompt: Optional system-level instructions for models that support it.
            kwargs: Optional overrides (e.g. temperature, max_tokens)
            
        Returns:
            The generated string text.
        """
        pass
