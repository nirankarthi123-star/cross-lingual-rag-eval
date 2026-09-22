from typing import Optional
import os
import groq
from groq import Groq
from backend.llm.base import LLMProvider
from backend.config.settings import get_settings

class GroqProvider(LLMProvider):
    """
    LLMProvider implementation for Groq.
    """

    def __init__(self, api_key: Optional[str] = None):
        settings = get_settings()
        self.api_key = api_key or settings.GROQ_API_KEY
        
        if not self.api_key or self.api_key == "your-groq-api-key-here":
            raise ValueError("Groq API key is not configured. Please set GROQ_API_KEY in .env")

        self.client = Groq(api_key=self.api_key)
        self.default_model = settings.LLM_MODEL
        self.default_temperature = settings.LLM_TEMPERATURE
        self.default_max_tokens = settings.LLM_MAX_TOKENS

    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})

        model = kwargs.get("model", self.default_model)
        temperature = kwargs.get("temperature", self.default_temperature)
        max_tokens = kwargs.get("max_tokens", self.default_max_tokens)

        try:
            response = self.client.chat.completions.create(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except groq.AuthenticationError as e:
            raise RuntimeError(f"Authentication failed with Groq API: {e}")
        except groq.RateLimitError as e:
            raise RuntimeError(f"Rate limit exceeded with Groq API: {e}")
        except groq.APIConnectionError as e:
            raise RuntimeError(f"Connection error with Groq API: {e}")
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred with Groq API: {e}")
