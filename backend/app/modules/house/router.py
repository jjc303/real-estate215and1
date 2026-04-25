from __future__ import annotations

from flask import Blueprint, g, request

from app.container.services import get_house_service
from app.core.response import success
from app.core.security import extract_bearer_token, get_current_user_id_from_token
from app.modules.house.schema import HouseCreateSchema, HouseListQuerySchema, HouseUpdateSchema


bp = Blueprint("house", __name__)


@bp.post("")
def create_house():
    token = extract_bearer_token(request.headers.get("Authorization"))
    current_user_id = get_current_user_id_from_token(token)
    data = HouseCreateSchema(**(request.get_json() or {}))
    service = get_house_service()
    result = service.create_house(g.db, landlord_id=current_user_id, data=data)
    return success(data=result, status_code=201)


@bp.get("")
def list_houses():
    query = HouseListQuerySchema(**request.args.to_dict())
    current_user_id = None
    if query.mine:
        token = extract_bearer_token(request.headers.get("Authorization"))
        current_user_id = get_current_user_id_from_token(token)
    service = get_house_service()
    result = service.list_houses(
        g.db,
        page=query.page,
        page_size=query.page_size,
        mine=query.mine,
        landlord_id=current_user_id,
    )
    return success(data=result)


@bp.get("/<int:house_id>")
def get_house_detail(house_id: int):
    current_user_id = None
    authorization = request.headers.get("Authorization")
    if authorization:
        token = extract_bearer_token(authorization)
        current_user_id = get_current_user_id_from_token(token)
    service = get_house_service()
    result = service.get_house_detail(g.db, house_id=house_id, current_user_id=current_user_id)
    return success(data=result)


@bp.put("/<int:house_id>")
def update_house(house_id: int):
    token = extract_bearer_token(request.headers.get("Authorization"))
    current_user_id = get_current_user_id_from_token(token)
    data = HouseUpdateSchema(**(request.get_json() or {}))
    service = get_house_service()
    result = service.update_house(g.db, house_id=house_id, landlord_id=current_user_id, data=data)
    return success(data=result)


@bp.patch("/<int:house_id>/publish")
def publish_house(house_id: int):
    token = extract_bearer_token(request.headers.get("Authorization"))
    current_user_id = get_current_user_id_from_token(token)
    service = get_house_service()
    result = service.publish_house(g.db, house_id=house_id, landlord_id=current_user_id)
    return success(data=result)


@bp.patch("/<int:house_id>/offline")
def offline_house(house_id: int):
    token = extract_bearer_token(request.headers.get("Authorization"))
    current_user_id = get_current_user_id_from_token(token)
    service = get_house_service()
    result = service.offline_house(g.db, house_id=house_id, landlord_id=current_user_id)
    return success(data=result)


@bp.delete("/<int:house_id>")
def delete_house(house_id: int):
    token = extract_bearer_token(request.headers.get("Authorization"))
    current_user_id = get_current_user_id_from_token(token)
    service = get_house_service()
    service.delete_house(g.db, house_id=house_id, landlord_id=current_user_id)
    return success(data=None)
