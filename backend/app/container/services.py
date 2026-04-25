from __future__ import annotations

from app.container.repositories import get_house_repository, get_user_repository
from app.modules.auth.service import AuthService
from app.modules.house.service import HouseService
from app.modules.user.service import UserService


_user_service = UserService(get_user_repository())
_auth_service = AuthService(get_user_repository())
_house_service = HouseService(get_house_repository())


def get_user_service() -> UserService:
    return _user_service


def get_auth_service() -> AuthService:
    return _auth_service


def get_house_service() -> HouseService:
    return _house_service
