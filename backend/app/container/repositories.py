from __future__ import annotations

from app.modules.user.repository import UserRepository


_user_repository = UserRepository()


def get_user_repository() -> UserRepository:
    return _user_repository
