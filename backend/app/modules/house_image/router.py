from __future__ import annotations

from flask import Blueprint, g, request

from app.common.dependencies import get_optional_current_user_id, get_required_current_user_id
from app.container.services import get_house_image_service
from app.core.exceptions import BadRequestException
from app.core.response import success
from app.modules.house_image.schema import HouseImageUpdateSchema

bp = Blueprint("house_image", __name__)


def _parse_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    candidate = value.strip().lower()
    if candidate in {"1", "true", "yes", "on"}:
        return True
    if candidate in {"0", "false", "no", "off"}:
        return False
    raise BadRequestException(message="invalid boolean value")


@bp.post("/<int:house_id>/images/upload")
def upload_house_image(house_id: int):
    current_user_id = get_required_current_user_id()
    file = request.files.get("file")
    if file is None:
        raise BadRequestException(message="file is required")

    sort_order_value = request.form.get("sort_order")
    sort_order = int(sort_order_value) if sort_order_value not in {None, ""} else None
    is_cover = _parse_bool(request.form.get("is_cover"))

    service = get_house_image_service()
    result = service.upload_image(
        g.db,
        current_user_id=current_user_id,
        house_id=house_id,
        file=file,
        sort_order=sort_order,
        is_cover=is_cover,
    )
    return success(data=result, status_code=201)


@bp.get("/<int:house_id>/images")
def list_house_images(house_id: int):
    current_user_id = get_optional_current_user_id()
    service = get_house_image_service()
    result = service.list_images(g.db, house_id=house_id, current_user_id=current_user_id)
    return success(data=result)


@bp.patch("/<int:house_id>/images/<int:image_id>")
def update_house_image(house_id: int, image_id: int):
    current_user_id = get_required_current_user_id()
    data = HouseImageUpdateSchema(**(request.get_json() or {}))
    service = get_house_image_service()
    result = service.update_image(
        g.db,
        current_user_id=current_user_id,
        house_id=house_id,
        image_id=image_id,
        data=data,
    )
    return success(data=result)


@bp.delete("/<int:house_id>/images/<int:image_id>")
def delete_house_image(house_id: int, image_id: int):
    current_user_id = get_required_current_user_id()
    service = get_house_image_service()
    service.delete_image(g.db, current_user_id=current_user_id, house_id=house_id, image_id=image_id)
    return success(data=None)
