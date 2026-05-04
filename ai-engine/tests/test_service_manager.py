"""测试服务状态汇总逻辑。"""

import pytest

from services.base import BaseService
from services.service_manager import ServiceManager


pytestmark = pytest.mark.unit


class DummyService(BaseService):
    """用于测试状态汇总逻辑的假服务。"""

    def __init__(self, status: str, message: str, **details):
        super().__init__()
        self._status = status
        self._message = message
        self._details = details

    def health_check(self):
        return {"status": self._status, "message": self._message, **self._details}


def test_get_runtime_status_summary():
    """状态汇总应正确统计整体状态和各服务明细。"""
    manager = ServiceManager()
    manager._services = {
        "llm": DummyService("ok", "LLM 正常", model="qwen-turbo"),
        "rag": DummyService("warning", "RAG 正在降级运行", doc_count=0),
        "ocr": DummyService("error", "OCR 未连接"),
    }
    manager._dependencies = {
        "llm": [],
        "rag": ["llm"],
        "ocr": [],
    }
    manager._initialized = {
        "llm": True,
        "rag": True,
        "ocr": False,
    }
    manager._init_order = ["llm", "rag"]
    manager._last_event = {
        "llm": "initialized",
        "rag": "initialized",
        "ocr": "initialize_failed",
    }
    manager._recent_error = {
        "llm": None,
        "rag": "向量库为空",
        "ocr": "OCR 未连接",
    }

    runtime_status = manager.get_runtime_status()

    assert runtime_status["generated_at"]
    assert runtime_status["overall_status"] == "degraded"
    assert runtime_status["total_services"] == 3
    assert runtime_status["initialized_services"] == 2
    assert runtime_status["healthy_services"] == 1
    assert runtime_status["warning_services"] == 1
    assert runtime_status["error_services"] == 1
    assert runtime_status["degraded_services"] == ["rag", "ocr"]
    assert runtime_status["unavailable_services"] == ["ocr"]
    assert runtime_status["services"][1]["dependencies"] == ["llm"]
    assert runtime_status["services"][0]["details"]["model"] == "qwen-turbo"
    assert runtime_status["services"][1]["details"]["doc_count"] == 0
    assert runtime_status["services"][1]["last_event"] == "initialized"
    assert runtime_status["services"][1]["recent_error"] == "向量库为空"
