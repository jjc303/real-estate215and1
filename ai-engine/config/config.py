"""Configuration management for the rental AI engine."""

from __future__ import annotations

import os

from pydantic_settings import BaseSettings, SettingsConfigDict

from utils.exceptions import ConfigurationException


class Settings(BaseSettings):
    """Application settings loaded from env files and process env."""

    model_config = SettingsConfigDict(
        env_file=(os.path.join(os.path.dirname(__file__), "local.env"),),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    DASHSCOPE_API_KEY: str
    DASHSCOPE_BASE_URL: str = "https://dashscope.aliyuncs.com"

    APP_NAME: str = "rental-ai-engine"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    HOST: str = "0.0.0.0"
    PORT: int = 9000

    CHROMA_PERSIST_DIR: str = "/data/chroma_db"
    KNOWLEDGE_BASE_PATH: str = os.path.join(
        os.path.dirname(__file__), "..", "data", "rental_knowledge.md"
    )
    RAG_CHUNK_SIZE: int = 500
    RAG_CHUNK_OVERLAP: int = 50
    RAG_RETRIEVE_K: int = 3

    HISTORY_CACHE_MAX_SIZE: int = 100
    HISTORY_CACHE_EXPIRE_SECONDS: int = 3600
    RAG_CACHE_MAX_SIZE: int = 500
    RAG_CACHE_EXPIRE_SECONDS: int = 1800

    LLM_MODEL: str = "qwen-turbo"
    LLM_TEMPERATURE: float = 0.7

    EMBEDDING_MODEL: str = "text-embedding-v4"
    EMBEDDING_DIMENSION: int = 1024
    EMBEDDING_TIMEOUT_SECONDS: float = 30.0
    EMBEDDING_MAX_RETRIES: int = 3
    EMBEDDING_BATCH_SIZE: int = 10
    EMBEDDING_CACHE_MAX_SIZE: int = 1000

    OCR_MODEL: str = "qwen-vl-ocr-latest"
    OCR_TIMEOUT_SECONDS: float = 30.0
    OCR_MAX_RETRIES: int = 3
    OCR_USE_GPU: bool = False
    OCR_SHOW_LOG: bool = False

    AI_ENGINE_API_KEY: str = ""
    RAG_ENABLED: bool = True
    MEMORY_ENABLED: bool = True
    OCR_ENABLED: bool = False

    DB_HOST: str = ""
    DB_PORT: int = 3306
    DB_NAME: str = ""
    DB_USER: str = ""
    DB_PASSWORD: str = ""

    def validate_runtime_config(self):
        """Validate required runtime configuration."""
        required_values = {
            "DASHSCOPE_API_KEY": self.DASHSCOPE_API_KEY,
            "AI_ENGINE_API_KEY": self.AI_ENGINE_API_KEY,
            "DB_HOST": self.DB_HOST,
            "DB_NAME": self.DB_NAME,
            "DB_USER": self.DB_USER,
            "DB_PASSWORD": self.DB_PASSWORD,
        }
        missing = [name for name, value in required_values.items() if not value]
        if missing:
            raise ConfigurationException(f"Missing required config: {', '.join(missing)}")


settings = Settings()
