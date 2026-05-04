"""测试异常处理模块。

本文件测试 exceptions.py 模块的功能。
"""

from utils.exceptions import (
    AIEngineException,
    ChatException,
    ConfigurationException,
    GradingException,
    RAGException,
    handle_exception
)
from fastapi import HTTPException


def test_aie_engine_exception():
    """测试AI引擎基础异常类"""
    exception = AIEngineException("测试异常", 400)
    assert str(exception) == "测试异常"
    assert exception.error_code == 400


def test_chat_exception():
    """测试对话异常类"""
    exception = ChatException("对话失败", 400)
    assert str(exception) == "对话失败"
    assert exception.error_code == 400


def test_rag_exception():
    """测试RAG异常类"""
    exception = RAGException("RAG失败", 500)
    assert str(exception) == "RAG失败"
    assert exception.error_code == 500


def test_grading_exception():
    """测试批改异常类"""
    exception = GradingException("批改失败", 400)
    assert str(exception) == "批改失败"
    assert exception.error_code == 400


def test_handle_exception():
    """测试统一异常处理函数"""
    # 测试AI引擎异常
    ai_exception = AIEngineException("测试异常", 400)
    http_exception = handle_exception(ai_exception)
    assert isinstance(http_exception, HTTPException)
    assert http_exception.status_code == 400
    assert http_exception.detail["code"] == 400
    assert http_exception.detail["message"] == "测试异常"
    
    # 测试其他异常
    other_exception = Exception("其他异常")
    http_exception = handle_exception(other_exception)
    assert isinstance(http_exception, HTTPException)
    assert http_exception.status_code == 500
    assert http_exception.detail["code"] == 500
    assert "其他异常" in http_exception.detail["message"]


def test_configuration_exception_maps_to_bad_request():
    """配置类业务错误码应映射为合法的 400 状态码。"""
    exception = ConfigurationException("配置缺失")
    http_exception = handle_exception(exception)

    assert isinstance(http_exception, HTTPException)
    assert http_exception.status_code == 400
    assert http_exception.detail["code"] == 4001
    assert http_exception.detail["message"] == "配置缺失"
