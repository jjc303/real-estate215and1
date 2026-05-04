"""Embedding service backed by Alibaba Bailian (DashScope)."""

from __future__ import annotations

import threading
import time
from collections import OrderedDict
from typing import Iterable, Optional

import httpx

from config.config import settings
from services.base import BaseService
from utils.exceptions import ErrorCode, LLMException


class BailianEmbeddingsAdapter:
    """LangChain-compatible embedding adapter for Chroma."""

    def __init__(self, embedding_service: "EmbeddingService"):
        self._embedding_service = embedding_service

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._embedding_service.embed_documents(texts)

    def embed_query(self, text: str) -> list[float]:
        return self._embedding_service.embed_query(text)


class EmbeddingService(BaseService):
    """Centralized embedding access with caching and retries."""

    EMBEDDING_PATH = "/api/v1/services/embeddings/text-embedding/text-embedding"
    MAX_BATCH_SIZE = 10

    def __init__(self):
        super().__init__()
        self._sync_client: Optional[httpx.Client] = None
        self._async_client: Optional[httpx.AsyncClient] = None
        self._cache: OrderedDict[str, list[float]] = OrderedDict()
        self._cache_lock = threading.RLock()
        self._adapter = BailianEmbeddingsAdapter(self)

    def initialize(self) -> bool:
        try:
            timeout = settings.EMBEDDING_TIMEOUT_SECONDS
            self._sync_client = httpx.Client(timeout=timeout)
            self._async_client = httpx.AsyncClient(timeout=timeout)
            return True
        except Exception as error:
            self._log_error("初始化 embedding 服务失败", error)
            return False

    def health_check(self) -> dict:
        if not self._sync_client or not self._async_client:
            return {"status": "error", "message": "Embedding 服务未初始化"}
        return {
            "status": "ok",
            "message": "Embedding 服务运行正常",
            "model": settings.EMBEDDING_MODEL,
            "dimension": settings.EMBEDDING_DIMENSION,
            "cache_size": len(self._cache),
        }

    def shutdown(self):
        try:
            if self._sync_client:
                self._sync_client.close()
            self._sync_client = None

            if self._async_client:
                try:
                    import asyncio

                    try:
                        loop = asyncio.get_event_loop()
                    except RuntimeError:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(self._async_client.aclose())
                        loop.close()
                    else:
                        if not loop.is_running():
                            loop.run_until_complete(self._async_client.aclose())
                        else:
                            asyncio.create_task(self._async_client.aclose())
                except Exception as error:
                    self._log_error("关闭异步 embedding 客户端失败", error)
                finally:
                    self._async_client = None

            with self._cache_lock:
                self._cache.clear()
        except Exception as error:
            self._log_error("关闭 embedding 服务失败", error)

    def get_langchain_embeddings(self) -> BailianEmbeddingsAdapter:
        return self._adapter

    def embed_query(self, text: str) -> list[float]:
        results = self.embed_documents([text], text_type="query")
        return results[0] if results else []

    def embed_documents(self, texts: list[str], text_type: str = "document") -> list[list[float]]:
        return self._embed_documents_sync(texts, text_type=text_type)

    async def aembed_query(self, text: str) -> list[float]:
        results = await self.aembed_documents([text], text_type="query")
        return results[0] if results else []

    async def aembed_documents(self, texts: list[str], text_type: str = "document") -> list[list[float]]:
        return await self._embed_documents_async(texts, text_type=text_type)

    def _build_payload(self, texts: list[str], text_type: str) -> dict:
        payload = {
            "model": settings.EMBEDDING_MODEL,
            "input": {"texts": texts},
            "parameters": {
                "dimension": settings.EMBEDDING_DIMENSION,
                "text_type": text_type,
            },
        }
        return payload

    def _effective_batch_size(self) -> int:
        configured_batch_size = int(settings.EMBEDDING_BATCH_SIZE)
        if configured_batch_size <= 0:
            return 1
        return min(configured_batch_size, self.MAX_BATCH_SIZE)

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {settings.DASHSCOPE_API_KEY}",
            "Content-Type": "application/json",
        }

    def _url(self) -> str:
        return f"{settings.DASHSCOPE_BASE_URL.rstrip('/')}{self.EMBEDDING_PATH}"

    def _read_cache(self, text: str) -> Optional[list[float]]:
        with self._cache_lock:
            embedding = self._cache.get(text)
            if embedding is None:
                return None
            self._cache.move_to_end(text)
            return list(embedding)

    def _write_cache(self, text: str, embedding: list[float]) -> None:
        with self._cache_lock:
            self._cache[text] = list(embedding)
            self._cache.move_to_end(text)
            while len(self._cache) > settings.EMBEDDING_CACHE_MAX_SIZE:
                self._cache.popitem(last=False)

    def _split_cached_inputs(self, texts: Iterable[str]) -> tuple[dict[int, list[float]], list[int], list[str]]:
        cached_embeddings: dict[int, list[float]] = {}
        uncached_indices: list[int] = []
        uncached_texts: list[str] = []

        for index, text in enumerate(texts):
            embedding = self._read_cache(text)
            if embedding is None:
                uncached_indices.append(index)
                uncached_texts.append(text)
            else:
                cached_embeddings[index] = embedding

        return cached_embeddings, uncached_indices, uncached_texts

    def _merge_embeddings(
        self,
        texts: list[str],
        cached_embeddings: dict[int, list[float]],
        uncached_indices: list[int],
        uncached_embeddings: list[list[float]],
    ) -> list[list[float]]:
        restored: dict[int, list[float]] = dict(cached_embeddings)
        for original_index, embedding in zip(uncached_indices, uncached_embeddings):
            restored[original_index] = embedding
            self._write_cache(texts[original_index], embedding)
        return [restored[index] for index in range(len(texts))]

    def _extract_embeddings(self, payload: dict) -> list[list[float]]:
        output = payload.get("output", {})
        embeddings = output.get("embeddings")
        if not isinstance(embeddings, list):
            raise LLMException("百炼 embedding 返回格式异常", ErrorCode.INTERNAL_SERVER_ERROR)

        vectors: list[list[float]] = []
        for item in embeddings:
            vector = item.get("embedding") if isinstance(item, dict) else None
            if not isinstance(vector, list):
                raise LLMException("百炼 embedding 缺少 embedding 向量", ErrorCode.INTERNAL_SERVER_ERROR)
            vectors.append(vector)
        return vectors

    def _post_sync(self, texts: list[str], text_type: str) -> list[list[float]]:
        if not self._sync_client:
            raise LLMException("Embedding 服务未初始化", ErrorCode.INTERNAL_SERVER_ERROR)

        last_error: Optional[Exception] = None
        for attempt in range(settings.EMBEDDING_MAX_RETRIES):
            try:
                response = self._sync_client.post(
                    self._url(),
                    json=self._build_payload(texts, text_type),
                    headers=self._headers(),
                )
                response.raise_for_status()
                return self._extract_embeddings(response.json())
            except Exception as error:
                last_error = error
                if attempt < settings.EMBEDDING_MAX_RETRIES - 1:
                    time.sleep(2**attempt)
        raise LLMException(f"调用百炼 embedding 失败: {last_error}", ErrorCode.INTERNAL_SERVER_ERROR)

    async def _post_async(self, texts: list[str], text_type: str) -> list[list[float]]:
        if not self._async_client:
            raise LLMException("Embedding 服务未初始化", ErrorCode.INTERNAL_SERVER_ERROR)

        last_error: Optional[Exception] = None
        for attempt in range(settings.EMBEDDING_MAX_RETRIES):
            try:
                response = await self._async_client.post(
                    self._url(),
                    json=self._build_payload(texts, text_type),
                    headers=self._headers(),
                )
                response.raise_for_status()
                return self._extract_embeddings(response.json())
            except Exception as error:
                last_error = error
                if attempt < settings.EMBEDDING_MAX_RETRIES - 1:
                    import asyncio

                    await asyncio.sleep(2**attempt)
        raise LLMException(f"调用百炼 embedding 失败: {last_error}", ErrorCode.INTERNAL_SERVER_ERROR)

    def _embed_documents_sync(self, texts: list[str], text_type: str) -> list[list[float]]:
        if not texts:
            return []

        cached_embeddings, uncached_indices, uncached_texts = self._split_cached_inputs(texts)
        uncached_vectors: list[list[float]] = []
        batch_size = self._effective_batch_size()

        for start in range(0, len(uncached_texts), batch_size):
            batch_texts = uncached_texts[start : start + batch_size]
            uncached_vectors.extend(self._post_sync(batch_texts, text_type=text_type))

        return self._merge_embeddings(texts, cached_embeddings, uncached_indices, uncached_vectors)

    async def _embed_documents_async(self, texts: list[str], text_type: str) -> list[list[float]]:
        if not texts:
            return []

        cached_embeddings, uncached_indices, uncached_texts = self._split_cached_inputs(texts)
        uncached_vectors: list[list[float]] = []
        batch_size = self._effective_batch_size()

        for start in range(0, len(uncached_texts), batch_size):
            batch_texts = uncached_texts[start : start + batch_size]
            uncached_vectors.extend(await self._post_async(batch_texts, text_type=text_type))

        return self._merge_embeddings(texts, cached_embeddings, uncached_indices, uncached_vectors)
