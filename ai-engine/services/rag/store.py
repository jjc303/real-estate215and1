"""RAG 向量库生命周期管理。

本模块只负责向量库相关的底层行为，包括：
1. 读取知识库原始内容
2. 按配置完成文档切块
3. 复用、校验或重建 Chroma 向量库
4. 维护签名文件，判断是否需要重新构建
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import threading
import time
from typing import Optional

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config.config import settings
from utils.exceptions import RAGException
from utils.logger import get_logger


class RAGVectorStore:
    """负责向量库的构建、加载与修复。"""

    SIGNATURE_FILE = ".rag_signature.json"

    def __init__(self, embeddings):
        self._logger = get_logger(__name__)
        self._embeddings = embeddings
        self._vectorstore: Optional[Chroma] = None
        self._build_lock = threading.RLock()

    @property
    def vectorstore(self) -> Optional[Chroma]:
        return self._vectorstore

    def is_ready(self) -> bool:
        return self._vectorstore is not None

    def initialize(self) -> Optional[Chroma]:
        with self._build_lock:
            if self._vectorstore is not None:
                return self._vectorstore

            content = self._load_knowledge_base()
            if not content:
                return None

            splits = self._split_documents(content)
            if not splits:
                return None

            # 启动时优先复用旧库，只有知识库内容或关键配置变化时才重建。
            self._vectorstore = self._load_or_rebuild_vectorstore(content, splits)
            return self._vectorstore

    def rebuild(self) -> Optional[Chroma]:
        with self._build_lock:
            content = self._load_knowledge_base()
            if not content:
                return None

            splits = self._split_documents(content)
            if not splits:
                return None

            self._clear_persist_dir()
            self._vectorstore = self._create_vectorstore(content, splits)
            return self._vectorstore

    def shutdown(self):
        with self._build_lock:
            self._vectorstore = None

    def _load_knowledge_base(self) -> str:
        try:
            with open(settings.KNOWLEDGE_BASE_PATH, "r", encoding="utf-8") as file:
                return file.read()
        except Exception as exc:
            self._logger.error(f"加载知识库失败: {exc}")
            return ""

    def _split_documents(self, content: str) -> list[Document]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.RAG_CHUNK_SIZE,
            chunk_overlap=settings.RAG_CHUNK_OVERLAP,
        )
        return splitter.split_documents(
            [Document(page_content=content, metadata={"source": "know.md"})]
        )

    def _load_or_rebuild_vectorstore(self, content: str, splits: list[Document]) -> Chroma:
        persist_dir = settings.CHROMA_PERSIST_DIR
        signature = self._compute_signature(content)

        # 签名覆盖知识库内容和切块/模型参数，用来判断旧库是否还能继续复用。
        if os.path.exists(persist_dir) and self._signature_matches(signature):
            try:
                vectorstore = Chroma(
                    persist_directory=persist_dir,
                    embedding_function=self._embeddings,
                )
                if self._validate_vectorstore(vectorstore):
                    self._logger.info("已加载现有向量库")
                    return vectorstore
                self._logger.warning("现有向量库无效，将重新构建")
            except Exception as exc:
                self._logger.warning(f"加载现有向量库失败，将重新构建: {exc}")

        self._clear_persist_dir()
        return self._create_vectorstore(content, splits)

    def _create_vectorstore(self, content: str, splits: list[Document]) -> Chroma:
        try:
            vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=self._embeddings,
                persist_directory=settings.CHROMA_PERSIST_DIR,
            )
            self._write_signature(self._compute_signature(content))
            self._logger.info(f"向量库构建完成，共 {len(splits)} 个文档块")
            return vectorstore
        except Exception as exc:
            raise RAGException(f"构建向量库失败: {exc}") from exc

    def _validate_vectorstore(self, vectorstore: Chroma) -> bool:
        try:
            collection = vectorstore.get()
            return len(collection.get("documents", [])) > 0
        except Exception as exc:
            self._logger.error(f"校验向量库失败: {exc}")
            return False

    def _compute_signature(self, content: str) -> dict:
        try:
            stat = os.stat(settings.KNOWLEDGE_BASE_PATH)
            source_meta = {"mtime": stat.st_mtime, "size": stat.st_size}
        except OSError:
            source_meta = {"mtime": None, "size": None}

        # 只要知识库文件、Embedding 模型或切块策略变化，就会触发重建。
        return {
            "knowledge_base": source_meta,
            "content_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
            "embedding_model": settings.EMBEDDING_MODEL,
            "chunk_size": settings.RAG_CHUNK_SIZE,
            "chunk_overlap": settings.RAG_CHUNK_OVERLAP,
        }

    def _signature_path(self) -> str:
        return os.path.join(settings.CHROMA_PERSIST_DIR, self.SIGNATURE_FILE)

    def _signature_matches(self, signature: dict) -> bool:
        try:
            with open(self._signature_path(), "r", encoding="utf-8") as file:
                stored_signature = json.load(file)
            return stored_signature == signature
        except Exception:
            return False

    def _write_signature(self, signature: dict):
        os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
        with open(self._signature_path(), "w", encoding="utf-8") as file:
            json.dump(signature, file, ensure_ascii=False, indent=2)

    def _clear_persist_dir(self):
        persist_dir = settings.CHROMA_PERSIST_DIR
        if not os.path.exists(persist_dir):
            return

        for attempt in range(3):
            try:
                # 这里只清空目录内容，不直接删除挂载点本身，避免 Docker volume 出现 device busy。
                for entry in os.listdir(persist_dir):
                    path = os.path.join(persist_dir, entry)
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
                return
            except Exception as exc:
                self._logger.warning(
                    f"清理向量库目录失败（尝试 {attempt + 1}/3）: {exc}"
                )
                if attempt == 2:
                    raise RAGException(f"清理向量库目录失败: {exc}") from exc
                time.sleep(1)
