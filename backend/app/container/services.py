from __future__ import annotations

from app.container.repositories import get_user_repository
from app.modules.auth.service import AuthService
from app.modules.user.service import UserService


_user_service = UserService(get_user_repository())
_auth_service = AuthService(get_user_repository())


def get_user_service() -> UserService:
    return _user_service


def get_auth_service() -> AuthService:
    return _auth_service
