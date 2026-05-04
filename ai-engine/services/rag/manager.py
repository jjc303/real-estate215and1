"""RAG retrieval manager."""

from __future__ import annotations

import threading
import time
from collections import OrderedDict
from typing import Optional

from config.config import settings
from services.base import BaseService
from services.embedding_service import EmbeddingService
from services.rag.store import RAGVectorStore
from utils.async_utils import AsyncExecutionHelper
from utils.exceptions import RAGException


class RAGManager(BaseService):
    """Manage retrieval, caching, and vector store lifecycle."""

    def __init__(self):
        super().__init__()
        self.embedding_service: Optional[EmbeddingService] = None
        self.store: Optional[RAGVectorStore] = None
        self._init_attempted = False
        self._init_lock = threading.RLock()
        self.rag_cache: OrderedDict[str, tuple[str, float]] = OrderedDict()
        self.cache_lock = threading.RLock()
        self.max_cache_size = settings.RAG_CACHE_MAX_SIZE
        self.cache_expire_seconds = settings.RAG_CACHE_EXPIRE_SECONDS
        self._last_error: Optional[str] = None

    @property
    def vectorstore(self):
        return self.store.vectorstore if self.store else None

    def initialize(self) -> bool:
        with self._init_lock:
            if self.store and self.store.is_ready():
                return True

            self._init_attempted = True
            try:
                if not self.embedding_service:
                    from services.service_manager import service_manager

                    self.embedding_service = service_manager.get_service("embedding", require_initialized=True)
                    if not self.embedding_service:
                        self._last_error = "Embedding 服务初始化失败"
                        return False

                if not self.store:
                    self.store = RAGVectorStore(self.embedding_service.get_langchain_embeddings())

                initialized_store = self.store.initialize()
                if not initialized_store:
                    self._last_error = "知识库为空或向量库初始化失败"
                    return False

                self._last_error = None
                self._log_info("RAG 系统初始化完成")
                return True
            except Exception as exc:
                self._last_error = str(exc)
                self._log_error("初始化 RAG 系统失败", exc)
                if isinstance(exc, RAGException):
                    raise
                raise RAGException(f"初始化 RAG 系统失败: {exc}") from exc

    def health_check(self) -> dict:
        if not self.store or not self.store.is_ready():
            return {
                "status": "error",
                "message": self._last_error or "向量库未初始化",
                "cache_size": len(self.rag_cache),
                "embedding_model": settings.EMBEDDING_MODEL,
                "persist_dir": settings.CHROMA_PERSIST_DIR,
            }

        try:
            collection = self.store.vectorstore.get()
            doc_count = len(collection.get("documents", []))
            if doc_count == 0:
                return {
                    "status": "warning",
                    "message": "向量库为空",
                    "doc_count": 0,
                    "cache_size": len(self.rag_cache),
                    "embedding_model": settings.EMBEDDING_MODEL,
                    "persist_dir": settings.CHROMA_PERSIST_DIR,
                }
            return {
                "status": "ok",
                "message": f"RAG 服务运行正常，向量库包含 {doc_count} 个文档块",
                "doc_count": doc_count,
                "cache_size": len(self.rag_cache),
                "embedding_model": settings.EMBEDDING_MODEL,
                "persist_dir": settings.CHROMA_PERSIST_DIR,
            }
        except Exception as exc:
            return {"status": "error", "message": f"向量库检查失败: {exc}"}

    def shutdown(self):
        try:
            self._log_info("关闭 RAG 服务...")
            if self.store:
                self.store.shutdown()
            self.store = None
            with self.cache_lock:
                self.rag_cache.clear()
            self._log_info("RAG 服务关闭成功")
        except Exception as exc:
            self._log_error("关闭 RAG 服务失败", exc)

    def retrieve_context(self, question: str) -> str:
        try:
            cached_context = self._get_cached_context(question)
            if cached_context is not None:
                return cached_context

            if (not self.store or not self.store.is_ready()) and not self.initialize():
                return ""

            vectorstore = self.vectorstore
            if not vectorstore:
                return ""

            retriever = vectorstore.as_retriever(search_kwargs={"k": settings.RAG_RETRIEVE_K})
            docs = retriever.invoke(question)
            context = "\n\n".join(doc.page_content for doc in docs) if docs else ""

            if context:
                self._cache_context(question, context)
                self._log_info(f"RAG 命中相关文档 {len(docs)} 条")

            return context
        except Exception as exc:
            self._last_error = str(exc)
            self._log_error(f"RAG 检索失败: {exc}")
            return ""

    async def aretrieve_context(self, question: str) -> str:
        return await AsyncExecutionHelper.run_blocking(self.retrieve_context, question)

    def rebuild_vectorstore(self) -> bool:
        with self._init_lock:
            try:
                if not self.embedding_service:
                    from services.service_manager import service_manager

                    self.embedding_service = service_manager.get_service("embedding", require_initialized=True)
                    if not self.embedding_service:
                        self._last_error = "Embedding 服务初始化失败"
                        return False

                if not self.store:
                    self.store = RAGVectorStore(self.embedding_service.get_langchain_embeddings())

                rebuilt = self.store.rebuild()
                with self.cache_lock:
                    self.rag_cache.clear()

                self._last_error = None if rebuilt else "向量库重建失败"
                return rebuilt is not None
            except Exception as exc:
                self._last_error = str(exc)
                self._log_error("重建向量库失败", exc)
                return False

    async def arebuild_vectorstore(self) -> bool:
        return await AsyncExecutionHelper.run_blocking(self.rebuild_vectorstore)

    def _get_cached_context(self, question: str) -> Optional[str]:
        with self.cache_lock:
            if question not in self.rag_cache:
                return None

            context, timestamp = self.rag_cache[question]
            if time.time() - timestamp >= self.cache_expire_seconds:
                del self.rag_cache[question]
                return None
            return context

    def _cache_context(self, question: str, context: str):
        with self.cache_lock:
            if len(self.rag_cache) >= self.max_cache_size:
                self.rag_cache.popitem(last=False)
            self.rag_cache[question] = (context, time.time())
