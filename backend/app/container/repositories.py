from __future__ import annotations

from app.modules.favorite.repository import FavoriteRepository
from app.modules.house.repository import HouseRepository
from app.modules.user.repository import UserRepository


_user_repository = UserRepository()
_house_repository = HouseRepository()
_favorite_repository = FavoriteRepository()


def get_user_repository() -> UserRepository:
    return _user_repository


def get_house_repository() -> HouseRepository:
    return _house_repository


def get_favorite_repository() -> FavoriteRepository:
    return _favorite_repository
