"""Tests for the rental service."""

from unittest.mock import Mock

import pytest

from services.rental_service import RentalService
from utils.exceptions import ChatException


pytestmark = pytest.mark.unit


class FakeHistoryService:
    def __init__(self):
        self.saved_rounds = []
        self._history = Mock()

    def get_history_obj(self, session_id):
        return self._history

    def save_chat_round(self, session_id, question, answer, course, user_id=None):
        self.saved_rounds.append(
            {
                "session_id": session_id,
                "question": question,
                "answer": answer,
                "course": course,
                "user_id": user_id,
            }
        )


class FakeRAGManager:
    def __init__(self, context=""):
        self.context = context

    def retrieve_context(self, message: str) -> str:
        return self.context


class FakeResponse:
    def __init__(self, content: str):
        self.content = content


class FakeChain:
    def __init__(self, content: str):
        self.content = content
        self.last_payload = None
        self.last_config = None

    def invoke(self, payload, config=None):
        self.last_payload = payload
        self.last_config = config
        return FakeResponse(self.content)


def _build_service(answer='{"answer":"月租 3000 元，押金 3000 元。"}', rag_context=""):
    service = RentalService()
    service.session_history = FakeHistoryService()
    service.rag_manager = FakeRAGManager(rag_context) if rag_context is not None else None
    service.house_chain_with_history = FakeChain(answer)
    service.general_chain_with_history = FakeChain(answer)
    memory_chain = Mock()
    memory_chain.invoke.return_value = FakeResponse(
        '{"memories":[{"type":"budget_preference","content":"预算 3000 元以内"}]}'
    )
    service._memory_prompt = Mock()
    service._memory_prompt.__or__ = Mock(return_value=memory_chain)
    service.llm = Mock()
    return service


def test_house_chat_returns_answer_and_sources():
    service = _build_service(rag_context="租房流程说明")

    result = service.house_chat(
        user_id="rental_user_1",
        session_id="rental:house:1:user:1",
        message="这套房押金多少？",
        user_context={"id": 1, "role": "tenant"},
        house_context={"id": 1, "title": "一室一厅", "status": "listed"},
        platform_context={"domain": "rental", "source": "real-estate-platform"},
    )

    assert result["answer"] == "月租 3000 元，押金 3000 元。"
    assert result["session_id"] == "rental:house:1:user:1"
    assert result["sources"][0]["type"] == "rag"
    assert service.session_history.saved_rounds[0]["course"] == "rental-house"
    assert "platform_context" in service.house_chain_with_history.last_payload
    assert "real-estate-platform" in service.house_chain_with_history.last_payload["platform_context"]


def test_general_chat_works_without_rag():
    service = _build_service(rag_context="")

    result = service.chat(
        user_id="rental_user_2",
        session_id="rental:general:user:2",
        message="签合同要注意什么？",
        user_context={"id": 2, "role": "tenant"},
        platform_context={"domain": "rental", "source": "real-estate-platform"},
    )

    assert result["answer"] == "月租 3000 元，押金 3000 元。"
    assert result["sources"] == []
    assert service.session_history.saved_rounds[0]["course"] == "rental-general"
    assert "platform_context" in service.general_chain_with_history.last_payload
    assert "real-estate-platform" in service.general_chain_with_history.last_payload["platform_context"]


def test_house_chat_requires_house_context():
    service = _build_service()

    with pytest.raises(ChatException):
        service.house_chat(
            user_id="rental_user_1",
            session_id="rental:house:1:user:1",
            message="这套房怎么样？",
            user_context={"id": 1, "role": "tenant"},
            house_context=None,
            platform_context=None,
        )


def test_message_cannot_be_empty():
    service = _build_service()

    with pytest.raises(ChatException):
        service.chat(
            user_id="rental_user_1",
            session_id="rental:general:user:1",
            message="   ",
            user_context={"id": 1, "role": "tenant"},
            platform_context=None,
        )


def test_memory_extraction_filters_sensitive_content():
    service = _build_service()
    assert service._sanitize_memories(
        [
            {"type": "budget_preference", "content": "预算 3000 元以内"},
            {"type": "budget_preference", "content": "手机号 13800000000"},
            {"type": "unknown", "content": "不要这个"},
        ]
    ) == [{"type": "budget_preference", "content": "预算 3000 元以内"}]
