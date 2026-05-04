"""服务基类模块。

本模块定义服务层的统一接口和公共日志能力，
用于约束各类服务的初始化、健康检查与关闭行为。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from utils.async_utils import AsyncExecutionHelper
from utils.logger import get_logger


class BaseService(ABC):
    """所有服务实现的公共基类。"""
    
    def __init__(self):
        """初始化基础服务能力。"""
        self.logger = get_logger(self.__class__.__name__)
    
    def initialize(self) -> bool:
        """初始化服务。"""
        return True
    
    async def initialize_async(self) -> bool:
        """异步初始化服务。"""
        return await AsyncExecutionHelper.run_blocking(self.initialize)
    
    def health_check(self) -> Dict[str, Any]:
        """返回默认健康状态。"""
        return {"status": "ok", "message": "服务运行正常"}
    
    async def health_check_async(self) -> Dict[str, Any]:
        """异步健康检查。"""
        return await AsyncExecutionHelper.run_blocking(self.health_check)
    
    def shutdown(self):
        """关闭服务并释放运行期资源。"""
        pass
    
    async def shutdown_async(self):
        """异步关闭服务。"""
        await AsyncExecutionHelper.run_blocking(self.shutdown)
    
    def _validate_params(self, params: Dict[str, Any], required: list) -> bool:
        """检查必填参数是否齐全。"""
        for param in required:
            if param not in params or params[param] is None:
                return False
        return True
    
    def _log_error(self, message: str, error: Exception = None):
        """记录错误日志。"""
        if error:
            self.logger.error(f"{message}: {str(error)}", exc_info=True)
        else:
            self.logger.error(message)
    
    def _log_info(self, message: str):
        """记录普通信息日志。"""
        self.logger.info(message)
    
    def _log_warning(self, message: str):
        """记录告警日志。"""
        self.logger.warning(message)
