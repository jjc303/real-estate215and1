from __future__ import annotations

from flask import request

from app.core.security import extract_bearer_token, get_current_user_id_from_token


def get_required_current_user_id() -> int:
    """
    必须登录：
    - 从 Authorization 头提取 Bearer token
    - 解析 token
    - 返回 current_user_id
    - token 缺失/无效时沿用现有 1003 未登录异常
    """
    token = extract_bearer_token(request.headers.get("Authorization"))
    return get_current_user_id_from_token(token)


def get_optional_current_user_id() -> int | None:
    """
    可选登录：
    - 没有 Authorization 时返回 None
    - 有 Authorization 时提取并解析 token
    - token 无效时沿用现有 1003 未登录异常
    """
    authorization = request.headers.get("Authorization")
    if not authorization:
        return None

    token = extract_bearer_token(authorization)
    return get_current_user_id_from_token(token)
