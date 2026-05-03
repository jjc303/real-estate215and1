from __future__ import annotations

from flask import Blueprint, g, request

from app.common.dependencies import get_required_current_user_id
from app.container.services import get_auth_service
from app.core.response import success
from app.modules.auth.schema import (
    EmailLoginSchema,
    EmailRegisterSchema,
    LoginSchema,
    SendEmailCodeSchema,
)


bp = Blueprint("auth", __name__)


@bp.post("/login")
def login():
    data = LoginSchema(**(request.get_json() or {}))
    service = get_auth_service()
    result = service.login(g.db, username=data.username, password=data.password)
    return success(data=result)


@bp.post("/email/code")
def send_email_code():
    data = SendEmailCodeSchema(**(request.get_json() or {}))
    service = get_auth_service()
    result = service.send_email_code(g.db, email=str(data.email), biz_type=data.biz_type)
    return success(data=result)


@bp.post("/email/register")
def email_register():
    data = EmailRegisterSchema(**(request.get_json() or {}))
    service = get_auth_service()
    result = service.email_register(
        g.db,
        email=str(data.email),
        code=data.code,
        role=data.role,
        real_name=data.real_name,
        phone=data.phone,
        avatar=data.avatar,
        password=data.password,
    )
    return success(data=result)


@bp.post("/email/login")
def email_login():
    data = EmailLoginSchema(**(request.get_json() or {}))
    service = get_auth_service()
    result = service.email_login(g.db, email=str(data.email), code=data.code)
    return success(data=result)


@bp.get("/me")
def get_current_user():
    current_user_id = get_required_current_user_id()
    service = get_auth_service()
    result = service.get_current_user(g.db, current_user_id)
    return success(data=result)
