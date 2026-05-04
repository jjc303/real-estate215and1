"""AI 引擎状态接口响应模型。"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ServiceStatusItem(BaseModel):
    """单个服务的状态快照。"""

    name: str = Field(..., description="服务名称")
    initialized: bool = Field(..., description="服务是否已完成初始化")
    status: str = Field(..., description="服务健康状态，如 ok、warning、error")
    message: str = Field(..., description="服务状态说明")
    dependencies: List[str] = Field(default_factory=list, description="服务声明的依赖列表")
    details: Dict[str, Any] = Field(default_factory=dict, description="服务额外诊断信息")
    last_event: Optional[str] = Field(None, description="最近一次生命周期事件")
    recent_error: Optional[str] = Field(None, description="最近一次错误信息")


class EngineStatusPayload(BaseModel):
    """AI 引擎整体状态信息。"""

    app_name: str = Field(..., description="应用名称")
    app_version: str = Field(..., description="应用版本")
    generated_at: str = Field(..., description="状态生成时间")
    summary: str = Field(..., description="面向人工阅读的状态摘要")
    overall_status: str = Field(..., description="整体状态，如 ok、degraded、error")
    total_services: int = Field(..., description="已注册服务总数")
    initialized_services: int = Field(..., description="已初始化服务数量")
    healthy_services: int = Field(..., description="健康服务数量")
    warning_services: int = Field(..., description="告警服务数量")
    error_services: int = Field(..., description="异常服务数量")
    degraded_services: List[str] = Field(default_factory=list, description="当前处于告警或异常状态的服务")
    unavailable_services: List[str] = Field(default_factory=list, description="当前未初始化或不可用的服务")
    services: List[ServiceStatusItem] = Field(default_factory=list, description="各服务状态明细")
