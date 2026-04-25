from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt
from flask import current_app
from jwt import ExpiredSignatureError, InvalidTokenError
from werkzeug.security import check_password_hash, generate_password_hash

from app.core.exceptions import UnauthorizedException


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return check_password_hash(hashed, password)


def create_access_token(user_id: int) -> str:
    now = datetime.now(UTC)
    expire_minutes = int(current_app.config["JWT_EXPIRE_MINUTES"])
    payload = {
        "sub": str(user_id),
        "exp": now + timedelta(minutes=expire_minutes),
    }
    return jwt.encode(
        payload,
        current_app.config["JWT_SECRET_KEY"],
        algorithm=current_app.config["JWT_ALGORITHM"],
    )


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            current_app.config["JWT_SECRET_KEY"],
            algorithms=[current_app.config["JWT_ALGORITHM"]],
        )
    except (ExpiredSignatureError, InvalidTokenError) as exc:
        raise UnauthorizedException(message="未登录") from exc

    sub = payload.get("sub")
    if sub is None:
        raise UnauthorizedException(message="未登录")

    try:
        payload["sub"] = int(sub)
    except (TypeError, ValueError) as exc:
        raise UnauthorizedException(message="未登录") from exc

    return payload


def extract_bearer_token(authorization_header: str | None) -> str:
    if not authorization_header:
        raise UnauthorizedException(message="未登录")

    parts = authorization_header.strip().split(" ", 1)
    if len(parts) != 2 or parts[0] != "Bearer" or not parts[1]:
        raise UnauthorizedException(message="未登录")

    return parts[1]


def get_current_user_id_from_token(token: str) -> int:
    payload = decode_access_token(token)

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException("无效 token")

    try:
        return int(user_id)
    except (TypeError, ValueError):
        raise UnauthorizedException("无效 token")
