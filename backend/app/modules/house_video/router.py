from __future__ import annotations

from flask import Blueprint, g, request

from app.common.dependencies import get_optional_current_user_id, get_required_current_user_id
from app.container.services import get_house_video_service
from app.core.exceptions import BadRequestException
from app.core.response import success

bp = Blueprint("house_video", __name__)


def _parse_int(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        raise BadRequestException(message="invalid integer value")


@bp.post("/<int:house_id>/videos/upload")
def upload_house_video(house_id: int):
    current_user_id = get_required_current_user_id()
    file = request.files.get("file")
    if file is None:
        raise BadRequestException(message="file is required")

    duration = _parse_int(request.form.get("duration"))

    service = get_house_video_service()
    result = service.upload_video(
        g.db,
        current_user_id=current_user_id,
        house_id=house_id,
        file=file,
        duration=duration,
    )
    return success(data=result, status_code=201)


@bp.get("/<int:house_id>/videos")
def list_house_videos(house_id: int):
    current_user_id = get_optional_current_user_id()
    service = get_house_video_service()
    result = service.list_videos(g.db, house_id=house_id, current_user_id=current_user_id)
    return success(data=result)


@bp.delete("/<int:house_id>/videos/<int:video_id>")
def delete_house_video(house_id: int, video_id: int):
    current_user_id = get_required_current_user_id()
    service = get_house_video_service()
    service.delete_video(g.db, current_user_id=current_user_id, house_id=house_id, video_id=video_id)
    return success(data=None)
