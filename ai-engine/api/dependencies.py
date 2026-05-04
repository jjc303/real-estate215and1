"""路由层依赖辅助函数。

本模块统一处理路由层常见的依赖获取逻辑：
1. 从服务管理器获取已初始化服务
2. 服务不可用时抛出统一的 503 异常
"""

from fastapi import HTTPException


def get_required_service(service_name: str, display_name: str):
    """获取已初始化服务，不可用时抛出统一的 503 错误。"""

    from services.service_manager import service_manager

    service = service_manager.get_service(service_name, require_initialized=True)
    if not service:
        raise HTTPException(status_code=503, detail=f"{display_name}未初始化")
    return service
