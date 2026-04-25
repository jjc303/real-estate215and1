from __future__ import annotations

from flask import Blueprint, g, request

from app.common.dependencies import get_required_current_user_id
from app.container.services import get_auth_service
from app.core.response import success
from app.modules.auth.schema import LoginSchema


bp = Blueprint("auth", __name__)


@bp.post("/login")
def login():
    data = LoginSchema(**(request.get_json() or {}))
    service = get_auth_service()
    result = service.login(g.db, username=data.username, password=data.password)
    return success(data=result)


@bp.get("/me")
def get_current_user():
    current_user_id = get_required_current_user_id()
    service = get_auth_service()
    result = service.get_current_user(g.db, current_user_id)
    return success(data=result)
