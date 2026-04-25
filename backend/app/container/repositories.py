from __future__ import annotations

from app.modules.house.repository import HouseRepository
from app.modules.user.repository import UserRepository


_user_repository = UserRepository()
_house_repository = HouseRepository()


def get_user_repository() -> UserRepository:
    return _user_repository


def get_house_repository() -> HouseRepository:
    return _house_repository
