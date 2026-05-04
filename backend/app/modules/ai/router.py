from __future__ import annotations

from flask import Blueprint, g, request

from app.common.dependencies import get_required_current_user_id
from app.container.services import get_ai_service
from app.core.response import success
from app.modules.ai.schema import ChatSchema, HouseChatSchema


bp = Blueprint("ai", __name__)


@bp.post("/house-chat")
def house_chat():
    data = HouseChatSchema(**(request.get_json() or {}))
    current_user_id = get_required_current_user_id()
    service = get_ai_service()
    result = service.house_chat(
        g.db,
        current_user_id=current_user_id,
        house_id=data.house_id,
        message=data.message,
        session_id=data.session_id,
    )
    return success(data=result)


@bp.post("/chat")
def chat():
    data = ChatSchema(**(request.get_json() or {}))
    current_user_id = get_required_current_user_id()
    service = get_ai_service()
    result = service.chat(
        g.db,
        current_user_id=current_user_id,
        message=data.message,
        session_id=data.session_id,
    )
    return success(data=result)
