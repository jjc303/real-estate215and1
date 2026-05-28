from __future__ import annotations

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.common.base_repository import BaseRepository
from app.modules.user_avatar.model import UserAvatar


class UserAvatarRepository(BaseRepository[UserAvatar]):
    def __init__(self) -> None:
        super().__init__(UserAvatar)

    def count_active_by_user_id(self, db: Session, user_id: int) -> int:
        stmt = select(func.count()).select_from(UserAvatar).where(
            UserAvatar.user_id == user_id,
            UserAvatar.status == "active",
        )
        return int(db.execute(stmt).scalar_one())

    def clear_current_flags(self, db: Session, user_id: int) -> None:
        stmt = (
            update(UserAvatar)
            .where(UserAvatar.user_id == user_id, UserAvatar.status == "active", UserAvatar.is_current.is_(True))
            .values(is_current=False)
        )
        db.execute(stmt)

    def get_current_by_user_id(self, db: Session, user_id: int) -> UserAvatar | None:
        stmt = select(UserAvatar).where(
            UserAvatar.user_id == user_id,
            UserAvatar.status == "active",
            UserAvatar.is_current.is_(True),
        )
        return db.execute(stmt).scalar_one_or_none()

    def list_active_by_user_id(self, db: Session, user_id: int, offset: int, limit: int) -> list[UserAvatar]:
        stmt = (
            select(UserAvatar)
            .where(UserAvatar.user_id == user_id, UserAvatar.status == "active")
            .order_by(UserAvatar.id.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(db.execute(stmt).scalars().all())

