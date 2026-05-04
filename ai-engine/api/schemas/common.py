"""通用 API 响应模型。"""

from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    # 统一响应外壳，方便前后端和接口文档复用同一套结构。
    code: int
    msg: str
    data: Optional[T] = None


def success_response(data: T) -> ApiResponse[T]:
    # 成功响应统一从这里构造，避免各个路由重复手拼字典。
    return ApiResponse(code=200, msg="success", data=data)
