from __future__ import annotations

from flask import Blueprint, g, request

from app.common.dependencies import get_required_current_user_id
from app.container.services import get_notification_service
from app.core.response import success
from app.modules.notification.schema import NotificationCreateSchema, NotificationListQuerySchema


bp = Blueprint("notification", __name__)


@bp.post("")
def create_notification():
    current_user_id = get_required_current_user_id()
    data = NotificationCreateSchema(**(request.get_json() or {}))
    service = get_notification_service()
    result = service.create_notification(
        g.db,
        current_user_id=current_user_id,
        require_admin=True,
        user_id=data.user_id,
        source_type=data.source_type,
        source_id=data.source_id,
        title=data.title,
        message=data.message,
    )
    return success(data=result[0], status_code=201)


@bp.get("")
def list_notifications():
    current_user_id = get_required_current_user_id()
    query = NotificationListQuerySchema(**request.args.to_dict())
    service = get_notification_service()
    result = service.list_notifications(
        g.db,
        current_user_id=current_user_id,
        page=query.page,
        page_size=query.page_size,
        status=query.status,
    )
    return success(data=result)


@bp.get("/<int:notification_id>")
def get_notification_detail(notification_id: int):
    current_user_id = get_required_current_user_id()
    service = get_notification_service()
    result = service.get_notification_detail(
        g.db,
        current_user_id=current_user_id,
        notification_id=notification_id,
    )
    return success(data=result)


@bp.patch("/<int:notification_id>/read")
def mark_notification_read(notification_id: int):
    current_user_id = get_required_current_user_id()
    service = get_notification_service()
    result = service.mark_notification_read(
        g.db,
        current_user_id=current_user_id,
        notification_id=notification_id,
    )
    return success(data=result)
