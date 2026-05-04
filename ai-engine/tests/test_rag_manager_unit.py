"""Unit tests for RAG manager with embedding service dependency."""

from types import SimpleNamespace

import pytest

from services.rag.manager import RAGManager


pytestmark = pytest.mark.unit


class FakeEmbeddingService:
    def __init__(self):
        self.adapter = object()

    def get_langchain_embeddings(self):
        return self.adapter


class FakeVectorStore:
    def __init__(self, embeddings):
        self.embeddings = embeddings
        self.vectorstore = SimpleNamespace(
            get=lambda: {"documents": ["doc-1"]},
            as_retriever=lambda search_kwargs=None: SimpleNamespace(
                invoke=lambda question: [SimpleNamespace(page_content=f"context:{question}")]
            ),
        )

    def initialize(self):
        return self.vectorstore

    def rebuild(self):
        return self.vectorstore

    def shutdown(self):
        return None

    def is_ready(self):
        return True


def test_rag_manager_uses_embedding_service(monkeypatch):
    fake_embedding_service = FakeEmbeddingService()

    class FakeServiceManager:
        @staticmethod
        def get_service(name, require_initialized=False):
            if name == "embedding":
                return fake_embedding_service
            return None

    created = {}

    def fake_store_factory(embeddings):
        created["embeddings"] = embeddings
        return FakeVectorStore(embeddings)

    monkeypatch.setattr("services.service_manager.service_manager", FakeServiceManager())
    monkeypatch.setattr("services.rag.manager.RAGVectorStore", fake_store_factory)

    manager = RAGManager()
    assert manager.initialize() is True
    assert created["embeddings"] is fake_embedding_service.get_langchain_embeddings()


def test_rag_manager_retrieve_and_rebuild(monkeypatch):
    fake_embedding_service = FakeEmbeddingService()

    class FakeServiceManager:
        @staticmethod
        def get_service(name, require_initialized=False):
            if name == "embedding":
                return fake_embedding_service
            return None

    monkeypatch.setattr("services.service_manager.service_manager", FakeServiceManager())
    monkeypatch.setattr("services.rag.manager.RAGVectorStore", lambda embeddings: FakeVectorStore(embeddings))

    manager = RAGManager()
    assert manager.initialize() is True
    assert manager.retrieve_context("什么是数据库？") == "context:什么是数据库？"
    assert manager.rebuild_vectorstore() is True
