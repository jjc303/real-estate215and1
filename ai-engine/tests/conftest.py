"""Shared pytest fixtures."""

import os
import sys
import tempfile
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

os.environ.setdefault("DASHSCOPE_API_KEY", "test-api-key")
os.environ.setdefault("AI_ENGINE_API_KEY", "test-api-key")
os.environ.setdefault("DB_HOST", "127.0.0.1")
os.environ.setdefault("DB_NAME", "test_ai")
os.environ.setdefault("DB_USER", "tester")
os.environ.setdefault("DB_PASSWORD", "secret")


@pytest.fixture
def test_env():
    """Set minimal env vars required by settings."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as temp_file:
        temp_file.write("DASHSCOPE_API_KEY=test-api-key\n")
        temp_file.write("AI_ENGINE_API_KEY=test-api-key\n")
        temp_env_file = temp_file.name

    original_env = os.environ.copy()
    os.environ["DASHSCOPE_API_KEY"] = "test-api-key"
    os.environ["AI_ENGINE_API_KEY"] = "test-api-key"
    os.environ["DB_HOST"] = "127.0.0.1"
    os.environ["DB_NAME"] = "test_ai"
    os.environ["DB_USER"] = "tester"
    os.environ["DB_PASSWORD"] = "secret"

    yield

    os.environ.clear()
    os.environ.update(original_env)
    os.unlink(temp_env_file)


@pytest.fixture
def mock_llm():
    with patch("langchain_community.chat_models.ChatTongyi") as mock:
        mock_instance = Mock()
        mock_instance.invoke.return_value = "测试回答"
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_embeddings():
    with patch("services.embedding_service.EmbeddingService") as mock:
        mock_instance = Mock()
        mock_instance.embed_documents.return_value = [[0.1, 0.2, 0.3]]
        mock_instance.embed_query.return_value = [0.1, 0.2, 0.3]
        mock_instance.aembed_documents.return_value = [[0.1, 0.2, 0.3]]
        mock_instance.aembed_query.return_value = [0.1, 0.2, 0.3]
        mock.return_value = mock_instance
        yield mock_instance
