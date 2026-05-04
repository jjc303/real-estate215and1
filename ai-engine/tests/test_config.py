"""Tests for rental AI engine settings."""

from config.config import settings


def test_settings():
    assert settings is not None
    assert settings.APP_NAME == "rental-ai-engine"
    assert settings.APP_VERSION == "1.0.0"
    assert settings.DEBUG is False
    assert settings.HOST == "0.0.0.0"
    assert settings.PORT == 9000
    assert settings.CHROMA_PERSIST_DIR == "/data/chroma_db"
    assert settings.KNOWLEDGE_BASE_PATH is not None
    assert settings.LLM_MODEL == "qwen-turbo"
    assert settings.LLM_TEMPERATURE == 0.7
    assert settings.EMBEDDING_MODEL == "text-embedding-v4"
    assert settings.OCR_ENABLED is False
