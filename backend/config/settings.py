from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central application settings loaded from environment variables and .env file."""

    # Application Configuration
    APP_NAME: str = "Cross-Lingual Faithfulness Evaluation of RAG Chatbots"
    APP_ENV: str = "development"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    # Future Model / Provider Placeholders
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    HUGGINGFACE_API_KEY: Optional[str] = None

    DEFAULT_LLM_PROVIDER: str = "gemini"
    DEFAULT_EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Future Database Configuration (SQLite)
    DATABASE_URL: str = "sqlite:///./data/rag_eval.db"

    # Document Processing & Chunking Configuration
    DOCUMENTS_DIR: str = "data/documents"
    PROCESSED_DIR: str = "data/processed"
    DEFAULT_CHUNK_SIZE: int = 500
    DEFAULT_CHUNK_OVERLAP: int = 100

    # Embeddings & Vector Store Configuration
    EMBEDDING_MODEL: str = "intfloat/multilingual-e5-base"
    EMBEDDING_DIMENSION: int = 768
    VECTOR_STORE_DIR: str = "data/vector_store"
    DEFAULT_TOP_K: int = 5
    
    # LLM Provider Configuration
    LLM_PROVIDER: str = "groq"
    GROQ_API_KEY: str = ""
    LLM_MODEL: str = "openai/gpt-oss-20b"
    LLM_TEMPERATURE: float = 0.0
    LLM_MAX_TOKENS: int = 1024
    RAG_TOP_K: int = 5

    # Experimental Mitigation
    MITIGATION_ENABLED: bool = False
    
    # Faithfulness Judge Configuration
    JUDGE_LLM_MODEL: str = "openai/gpt-oss-20b"
    JUDGE_TEMPERATURE: float = 0.0
    HALLUCINATION_THRESHOLD: float = 0.8
    JUDGE_PROMPT_VERSION: str = "v1"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    """Return a cached singleton instance of application settings."""
    return Settings()
