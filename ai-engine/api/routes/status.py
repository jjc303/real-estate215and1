"""Rental AI engine status routes."""

from fastapi import APIRouter, Depends

from api.schemas.common import ApiResponse, success_response
from api.schemas.status import EngineStatusPayload, ServiceStatusItem
from config.config import settings
from services.service_manager import service_manager
from utils.auth import verify_api_key

router = APIRouter()


@router.get(
    "/status",
    summary="租房 AI 引擎状态",
    response_model=ApiResponse[EngineStatusPayload],
)
async def get_engine_status(api_key: str = Depends(verify_api_key)):
    runtime_status = service_manager.get_runtime_status()
    payload = EngineStatusPayload(
        app_name=settings.APP_NAME,
        app_version=settings.APP_VERSION,
        generated_at=runtime_status["generated_at"],
        summary=runtime_status["summary"],
        overall_status=runtime_status["overall_status"],
        total_services=runtime_status["total_services"],
        initialized_services=runtime_status["initialized_services"],
        healthy_services=runtime_status["healthy_services"],
        warning_services=runtime_status["warning_services"],
        error_services=runtime_status["error_services"],
        degraded_services=runtime_status["degraded_services"],
        unavailable_services=runtime_status["unavailable_services"],
        services=[ServiceStatusItem(**item) for item in runtime_status["services"]],
    )
    return success_response(payload)
