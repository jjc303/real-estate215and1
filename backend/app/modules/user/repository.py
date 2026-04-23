from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.user.model import User


class UserRepository:
    def get_by_id(self, db: Session, user_id: int) -> User | None:
        return db.get(User, user_id)

    def get_by_username(self, db: Session, username: str) -> User | None:
        stmt = select(User).where(User.username == username)
        return db.execute(stmt).scalar_one_or_none()

    def list_users(self, db: Session, offset: int, limit: int) -> list[User]:
        stmt = select(User).order_by(User.id.desc()).offset(offset).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def count_users(self, db: Session) -> int:
        stmt = select(func.count()).select_from(User)
        return int(db.execute(stmt).scalar_one())

    def create(self, db: Session, user: User) -> User:
        db.add(user)
        return user
