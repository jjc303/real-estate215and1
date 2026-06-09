"""Rental chat service built on top of the shared LLM, RAG, and session stack."""

from __future__ import annotations

import json
import re
from typing import Any

from langchain_core.runnables.history import RunnableWithMessageHistory

from prompts import (
    build_rental_general_chat_prompt,
    build_rental_house_chat_prompt,
    build_rental_memory_extract_prompt,
)
from services.base import BaseService
from utils.async_utils import AsyncExecutionHelper
from utils.exceptions import ChatException


class RentalService(BaseService):
    """Rental-specific AI chat service."""

    ALLOWED_MEMORY_TYPES = {
        "budget_preference",
        "region_preference",
        "house_type_preference",
        "area_preference",
        "commute_preference",
        "facility_preference",
        "decoration_preference",
        "floor_preference",
        "rental_constraint",
        "avoid_preference",
    }

    SENSITIVE_PATTERNS = [
        re.compile(r"\b\d{15,18}[0-9Xx]?\b"),
        re.compile(r"\b1\d{10}\b"),
        re.compile(r"\b\d{12,19}\b"),
    ]

    def __init__(self):
        super().__init__()
        self.llm_service = None
        self.rag_manager = None
        self.session_history = None
        self.llm = None
        self.house_chain = None
        self.general_chain = None
        self.house_chain_with_history = None
        self.general_chain_with_history = None
        self._memory_prompt = build_rental_memory_extract_prompt()
        self._preference_memory: dict[str, list[dict[str, str]]] = {}

    def initialize(self) -> bool:
        try:
            from services.service_manager import service_manager

            self.llm_service = service_manager.get_service("llm", require_initialized=True)
            self.session_history = service_manager.get_service("session_history", require_initialized=True)
            self.rag_manager = service_manager.get_service("rag")

            if not self.llm_service or not self.session_history:
                self._log_error("Rental service dependencies are not ready")
                return False

            self.llm = self.llm_service.llm
            if not self.llm:
                self._log_error("LLM model is not initialized")
                return False

            self.house_chain = build_rental_house_chat_prompt() | self.llm
            self.general_chain = build_rental_general_chat_prompt() | self.llm

            def get_session_history(session_id: str):
                return self.session_history.get_history_obj(session_id)

            self.house_chain_with_history = RunnableWithMessageHistory(
                self.house_chain,
                get_session_history,
                input_messages_key="message",
                history_messages_key="chat_history",
            )
            self.general_chain_with_history = RunnableWithMessageHistory(
                self.general_chain,
                get_session_history,
                input_messages_key="message",
                history_messages_key="chat_history",
            )

            self._log_info("Rental service initialized")
            return True
        except Exception as exc:
            self._log_error("Failed to initialize rental service", exc)
            return False

    def health_check(self) -> dict:
        if not self.llm or not self.house_chain_with_history or not self.general_chain_with_history:
            return {"status": "error", "message": "Rental service is not initialized"}
        return {
            "status": "ok",
            "message": "Rental service is running",
            "memory_sessions": len(self._preference_memory),
            "rag_enabled": bool(self.rag_manager),
        }

    def shutdown(self):
        self.llm = None
        self.house_chain = None
        self.general_chain = None
        self.house_chain_with_history = None
        self.general_chain_with_history = None
        self._preference_memory.clear()

    def house_chat(
        self,
        *,
        user_id: str,
        session_id: str,
        message: str,
        user_context: dict[str, Any] | None,
        house_context: dict[str, Any] | None,
        platform_context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        self._validate_message(message)
        if not house_context:
            raise ChatException("house_context is required", 400)

        rag_context = self._get_rag_context(message)
        response = self.house_chain_with_history.invoke(
            {
                "message": message,
                "user_context": self._json_text(user_context or {}),
                "platform_context": self._json_text(platform_context or {}),
                "house_context": self._json_text(house_context),
                "memory_context": self._format_memory(session_id),
                "rag_context": rag_context or "暂无额外知识库内容",
            },
            config={"configurable": {"session_id": session_id}},
        )
        answer = self._extract_answer(response)
        self.session_history.save_chat_round(
            session_id,
            message,
            answer,
            "rental-house",
            user_id,
        )
        self._maybe_extract_memory(session_id, message, answer)
        return {
            "answer": answer,
            "session_id": session_id,
            "sources": self._build_sources(rag_context),
            "suggestions": [],
            "metadata": {"mode": "house-chat"},
        }

    def chat(
        self,
        *,
        user_id: str,
        session_id: str,
        message: str,
        user_context: dict[str, Any] | None,
        platform_context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        self._validate_message(message)

        rag_context = self._get_rag_context(message)
        response = self.general_chain_with_history.invoke(
            {
                "message": message,
                "user_context": self._json_text(user_context or {}),
                "platform_context": self._json_text(platform_context or {}),
                "memory_context": self._format_memory(session_id),
                "rag_context": rag_context or "暂无额外知识库内容",
            },
            config={"configurable": {"session_id": session_id}},
        )
        answer = self._extract_answer(response)
        self.session_history.save_chat_round(
            session_id,
            message,
            answer,
            "rental-general",
            user_id,
        )
        self._maybe_extract_memory(session_id, message, answer)
        return {
            "answer": answer,
            "session_id": session_id,
            "sources": self._build_sources(rag_context),
            "suggestions": [],
            "metadata": {"mode": "general-chat"},
        }

    async def ahouse_chat(self, **kwargs) -> dict[str, Any]:
        return await AsyncExecutionHelper.run_blocking(self.house_chat, **kwargs)

    async def achat(self, **kwargs) -> dict[str, Any]:
        return await AsyncExecutionHelper.run_blocking(self.chat, **kwargs)

    def _validate_message(self, message: str):
        if not message or not message.strip():
            raise ChatException("message is required", 400)

    def _get_rag_context(self, message: str) -> str:
        if not self.rag_manager:
            return ""
        try:
            return self.rag_manager.retrieve_context(message)
        except Exception as exc:
            self._log_warning(f"Rental RAG retrieval failed, fallback to plain answer: {exc}")
            return ""

    def _extract_answer(self, response: Any) -> str:
        content = getattr(response, "content", response)
        if not isinstance(content, str):
            raise ChatException("invalid LLM response", 500)

        content = content.strip()
        if not content:
            raise ChatException("empty LLM response", 500)

        # 优先尝试直接解析整个内容为 JSON
        try:
            parsed = json.loads(content)
            answer = parsed.get("answer")
            if isinstance(answer, str) and answer.strip():
                return answer.strip()
        except json.JSONDecodeError:
            pass

        # 如果整体不是 JSON，尝试从内容中提取 {...} 部分
        import re
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group())
                answer = parsed.get("answer")
                if isinstance(answer, str) and answer.strip():
                    return answer.strip()
            except (json.JSONDecodeError, KeyError):
                pass

        return content

    def _maybe_extract_memory(self, session_id: str, user_message: str, answer: str):
        try:
            chain = self._memory_prompt | self.llm
            response = chain.invoke({"user_message": user_message, "answer": answer})
            content = getattr(response, "content", response)
            parsed = json.loads(content) if isinstance(content, str) else {}
            memories = parsed.get("memories", [])
            if not isinstance(memories, list):
                return
            sanitized = self._sanitize_memories(memories)
            if sanitized:
                self._preference_memory[session_id] = sanitized
        except Exception:
            # Memory extraction is best-effort only.
            return

    def _sanitize_memories(self, memories: list[Any]) -> list[dict[str, str]]:
        sanitized: list[dict[str, str]] = []
        for item in memories:
            if not isinstance(item, dict):
                continue
            memory_type = item.get("type")
            content = item.get("content")
            if memory_type not in self.ALLOWED_MEMORY_TYPES:
                continue
            if not isinstance(content, str):
                continue
            content = content.strip()
            if not content or self._contains_sensitive_data(content):
                continue
            sanitized.append({"type": memory_type, "content": content[:200]})
        return sanitized

    def _contains_sensitive_data(self, content: str) -> bool:
        lowered = content.lower()
        if any(token in lowered for token in ("身份证", "手机号", "银行卡", "住址", "姓名", "合同编号", "签名")):
            return True
        return any(pattern.search(content) for pattern in self.SENSITIVE_PATTERNS)

    def _format_memory(self, session_id: str) -> str:
        memories = self._preference_memory.get(session_id, [])
        if not memories:
            return "暂无已提取的长期租房偏好"
        return self._json_text(memories)

    def _build_sources(self, rag_context: str) -> list[dict[str, Any]]:
        if not rag_context:
            return []
        return [{"type": "rag", "content": rag_context[:500]}]

    def _json_text(self, value: Any) -> str:
        return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)
