from __future__ import annotations

from flask import Blueprint, g, request

from app.container.services import get_user_service
from app.core.response import success
from app.modules.user.schema import UserCreateSchema, UserListQuerySchema


bp = Blueprint("user", __name__)


@bp.post("")
def create_user():
    data = UserCreateSchema(**(request.get_json() or {}))
    service = get_user_service()
    result = service.create_user(g.db, data)
    return success(data=result, status_code=201)


@bp.get("")
def list_users():
    query = UserListQuerySchema(**request.args.to_dict())
    service = get_user_service()
    result = service.list_users(g.db, page=query.page, page_size=query.page_size)
    return success(data=result)


@bp.get("/<int:user_id>")
def get_user(user_id: int):
    service = get_user_service()
    data = service.get_user_by_id(g.db, user_id)
    return success(data=data)
