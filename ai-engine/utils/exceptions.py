"""异常处理模块

本文件定义了AI引擎中使用的自定义异常类和错误处理机制。
"""

from fastapi import HTTPException, status

# 错误码常量定义
class ErrorCode:
    """错误码定义"""
    # 通用错误
    INTERNAL_SERVER_ERROR = 500
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    
    # 业务错误
    RAG_ERROR = 5001
    GRADING_ERROR = 5002
    CHAT_ERROR = 5004
    CONFIGURATION_ERROR = 4001
    DB_ERROR = 5005
    DIFFICULTY_ERROR = 5006
    SESSION_ERROR = 5007
    OCR_ERROR = 5008


class AIEngineException(Exception):
    """AI引擎基础异常类"""
    def __init__(self, message: str, error_code: int = ErrorCode.INTERNAL_SERVER_ERROR):
        self.message = message
        self.error_code = error_code
        # 业务错误码与 HTTP 状态码分离，避免 4001 这类业务码被错误地当成响应状态码。
        self.status_code = _derive_http_status(error_code)
        super().__init__(self.message)


class RAGException(AIEngineException):
    """RAG相关异常"""
    def __init__(self, message: str, error_code: int = ErrorCode.RAG_ERROR):
        super().__init__(message, error_code)


class GradingException(AIEngineException):
    """作业批改相关异常"""
    def __init__(self, message: str, error_code: int = ErrorCode.GRADING_ERROR):
        super().__init__(message, error_code)


class ChatException(AIEngineException):
    """对话相关异常"""
    def __init__(self, message: str, error_code: int = ErrorCode.CHAT_ERROR):
        super().__init__(message, error_code)


class ConfigurationException(AIEngineException):
    """配置相关异常"""
    def __init__(self, message: str, error_code: int = ErrorCode.CONFIGURATION_ERROR):
        super().__init__(message, error_code)


class DBException(AIEngineException):
    """数据库相关异常"""
    def __init__(self, message: str, error_code: int = ErrorCode.DB_ERROR):
        super().__init__(message, error_code)


class DifficultyException(AIEngineException):
    """难度评级相关异常"""
    def __init__(self, message: str, error_code: int = ErrorCode.DIFFICULTY_ERROR):
        super().__init__(message, error_code)


class SessionException(AIEngineException):
    """会话管理相关异常"""
    def __init__(self, message: str, error_code: int = ErrorCode.SESSION_ERROR):
        super().__init__(message, error_code)


class OCRException(AIEngineException):
    """OCR相关异常"""
    def __init__(self, message: str, error_code: int = ErrorCode.OCR_ERROR):
        super().__init__(message, error_code)


class LLMException(AIEngineException):
    """LLM相关异常"""
    def __init__(self, message: str, error_code: int = ErrorCode.INTERNAL_SERVER_ERROR):
        super().__init__(message, error_code)


def _derive_http_status(error_code: int) -> int:
    """根据业务错误码推导合法的 HTTP 状态码。"""

    if 100 <= error_code <= 599:
        return error_code
    if 4000 <= error_code < 5000:
        return status.HTTP_400_BAD_REQUEST
    if error_code >= 5000:
        return status.HTTP_500_INTERNAL_SERVER_ERROR
    return status.HTTP_500_INTERNAL_SERVER_ERROR


def handle_exception(e: Exception) -> HTTPException:
    """统一异常处理
    
    Args:
        e: 异常对象
    
    Returns:
        HTTPException: 转换后的HTTP异常
    """
    if isinstance(e, AIEngineException):
        return HTTPException(
            status_code=e.status_code,
            detail={
                "code": e.error_code,
                "message": e.message
            }
        )
    elif isinstance(e, HTTPException):
        return e
    else:
        # 未知异常
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": ErrorCode.INTERNAL_SERVER_ERROR,
                "message": f"Internal server error: {str(e)}"
            }
        )
