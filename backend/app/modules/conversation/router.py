from __future__ import annotations

from flask import Blueprint, g, request

from app.common.dependencies import get_required_current_user_id
from app.container.services import get_conversation_service
from app.core.response import success
from app.modules.conversation.schema import (
    ConversationCreateSchema,
    ConversationListQuerySchema,
    ConversationMessageListQuerySchema,
    MessageCreateSchema,
)


bp = Blueprint("conversation", __name__)


@bp.post("")
def create_conversation():
    current_user_id = get_required_current_user_id()
    data = ConversationCreateSchema(**(request.get_json() or {}))
    service = get_conversation_service()
    result, created = service.create_conversation(
        g.db,
        current_user_id=current_user_id,
        house_id=data.house_id,
    )
    return success(data=result, status_code=201 if created else 200)


@bp.get("")
def list_conversations():
    current_user_id = get_required_current_user_id()
    query = ConversationListQuerySchema(**request.args.to_dict())
    service = get_conversation_service()
    result = service.list_conversations(
        g.db,
        current_user_id=current_user_id,
        page=query.page,
        page_size=query.page_size,
    )
    return success(data=result)


@bp.get("/<int:conversation_id>/messages")
def list_messages(conversation_id: int):
    current_user_id = get_required_current_user_id()
    query = ConversationMessageListQuerySchema(**request.args.to_dict())
    service = get_conversation_service()
    result = service.list_messages(
        g.db,
        current_user_id=current_user_id,
        conversation_id=conversation_id,
        page=query.page,
        page_size=query.page_size,
    )
    return success(data=result)


@bp.post("/<int:conversation_id>/messages")
def send_message(conversation_id: int):
    current_user_id = get_required_current_user_id()
    data = MessageCreateSchema(**(request.get_json() or {}))
    service = get_conversation_service()
    result = service.send_message(
        g.db,
        current_user_id=current_user_id,
        conversation_id=conversation_id,
        content=data.content,
    )
    return success(data=result, status_code=201)


@bp.patch("/<int:conversation_id>/read")
def mark_conversation_read(conversation_id: int):
    current_user_id = get_required_current_user_id()
    service = get_conversation_service()
    result = service.mark_conversation_read(
        g.db,
        current_user_id=current_user_id,
        conversation_id=conversation_id,
    )
    return success(data=result)
