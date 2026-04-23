from __future__ import annotations

from flask import Blueprint, g, request

from app.container.services import get_auth_service
from app.core.response import success
from app.core.security import extract_bearer_token
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
    token = extract_bearer_token(request.headers.get("Authorization"))
    service = get_auth_service()
    result = service.get_current_user(g.db, token)
    return success(data=result)
