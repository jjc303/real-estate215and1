from __future__ import annotations

from typing import Iterable

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.common.base_repository import BaseRepository
from app.modules.user.model import User


class UserRepository(BaseRepository[User]):
    def __init__(self) -> None:
        super().__init__(User)

    def get_by_username(self, db: Session, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        return db.execute(stmt).scalar_one_or_none()

    def list_users(self, db: Session, offset: int, limit: int) -> list[User]:
        stmt = select(User).order_by(User.id.desc()).offset(offset).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def count_users(self, db: Session) -> int:
        stmt = select(func.count()).select_from(User)
        return int(db.execute(stmt).scalar_one())

    def list_active_by_roles(self, db: Session, roles: Iterable[str]) -> list[User]:
        role_values = tuple(roles)
        stmt = (
            select(User)
            .where(User.status == "active", User.role.in_(role_values))
            .order_by(User.id.asc())
        )
        return list(db.execute(stmt).scalars().all())

    def list_by_ids(self, db: Session, user_ids: Iterable[int]) -> list[User]:
        values = tuple(user_ids)
        if not values:
            return []
        stmt = select(User).where(User.id.in_(values))
        return list(db.execute(stmt).scalars().all())
