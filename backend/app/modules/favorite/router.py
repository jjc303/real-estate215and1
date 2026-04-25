from __future__ import annotations

from flask import Blueprint, g, request

from app.common.dependencies import get_required_current_user_id
from app.container.services import get_favorite_service
from app.core.response import success
from app.modules.favorite.schema import FavoriteCreateSchema, FavoriteListQuerySchema


bp = Blueprint("favorite", __name__)


@bp.post("")
def add_favorite():
    current_user_id = get_required_current_user_id()
    data = FavoriteCreateSchema(**(request.get_json() or {}))
    service = get_favorite_service()
    result = service.add_favorite(g.db, current_user_id=current_user_id, house_id=data.house_id)
    return success(data=result, status_code=201)


@bp.get("")
def list_favorites():
    current_user_id = get_required_current_user_id()
    query = FavoriteListQuerySchema(**request.args.to_dict())
    service = get_favorite_service()
    result = service.list_favorites(
        g.db,
        current_user_id=current_user_id,
        page=query.page,
        page_size=query.page_size,
    )
    return success(data=result)


@bp.delete("/<int:house_id>")
def remove_favorite(house_id: int):
    current_user_id = get_required_current_user_id()
    service = get_favorite_service()
    service.remove_favorite(g.db, current_user_id=current_user_id, house_id=house_id)
    return success(data=None)
