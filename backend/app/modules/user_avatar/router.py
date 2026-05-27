from __future__ import annotations

from flask import Blueprint, g, request

from app.common.dependencies import get_required_current_user_id
from app.container.services import get_user_avatar_service
from app.core.exceptions import BadRequestException
from app.core.response import success
from app.modules.user_avatar.schema import UserAvatarListQuerySchema

bp = Blueprint("user_avatar", __name__)


@bp.post("/me/avatar/upload")
def upload_avatar():
    current_user_id = get_required_current_user_id()
    file = request.files.get("file")
    if file is None:
        raise BadRequestException(message="file is required")
    service = get_user_avatar_service()
    result = service.upload_avatar(g.db, current_user_id=current_user_id, file=file)
    return success(data=result, status_code=201)


@bp.get("/me/avatar")
def get_current_avatar():
    current_user_id = get_required_current_user_id()
    service = get_user_avatar_service()
    result = service.get_current_avatar(g.db, current_user_id=current_user_id)
    return success(data=result)


@bp.get("/me/avatars")
def list_avatars():
    current_user_id = get_required_current_user_id()
    query = UserAvatarListQuerySchema(**request.args.to_dict())
    service = get_user_avatar_service()
    result = service.list_avatars(
        g.db,
        current_user_id=current_user_id,
        page=query.page,
        page_size=query.page_size,
    )
    return success(data=result)
