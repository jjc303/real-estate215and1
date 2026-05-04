"""Public rental chat routes."""

from fastapi import APIRouter, Depends

from api.dependencies import get_required_service
from api.schemas.common import ApiResponse, success_response
from api.schemas.rental import RentalChatRequest, RentalChatResponse, RentalHouseChatRequest
from utils.auth import verify_api_key

router = APIRouter()


@router.post(
    "/house-chat",
    response_model=ApiResponse[RentalChatResponse],
    summary="房源 AI 问答",
)
async def rental_house_chat(
    request: RentalHouseChatRequest,
    api_key: str = Depends(verify_api_key),
):
    rental_service = get_required_service("rental", "租房 AI 服务")
    result = await rental_service.ahouse_chat(
        user_id=request.user_id,
        session_id=request.session_id,
        message=request.message,
        user_context=request.user_context.model_dump() if request.user_context else None,
        house_context=request.house_context.model_dump(),
        platform_context=request.platform_context.model_dump() if request.platform_context else None,
    )
    return success_response(RentalChatResponse(**result))


@router.post(
    "/chat",
    response_model=ApiResponse[RentalChatResponse],
    summary="通用租房助手对话",
)
async def rental_chat(
    request: RentalChatRequest,
    api_key: str = Depends(verify_api_key),
):
    rental_service = get_required_service("rental", "租房 AI 服务")
    result = await rental_service.achat(
        user_id=request.user_id,
        session_id=request.session_id,
        message=request.message,
        user_context=request.user_context.model_dump() if request.user_context else None,
        platform_context=request.platform_context.model_dump() if request.platform_context else None,
    )
    return success_response(RentalChatResponse(**result))
