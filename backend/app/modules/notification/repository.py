from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.common.base_repository import BaseRepository
from app.modules.notification.model import Notification


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self) -> None:
        super().__init__(Notification)

    def get_by_id_and_user_id(self, db: Session, notification_id: int, user_id: int) -> Notification | None:
        stmt = select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
        return db.execute(stmt).scalar_one_or_none()

    def list_by_user_id(self, db: Session, user_id: int, offset: int, limit: int) -> list[Notification]:
        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc(), Notification.id.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(db.execute(stmt).scalars().all())

    def count_by_user_id(self, db: Session, user_id: int) -> int:
        stmt = select(func.count()).select_from(Notification).where(Notification.user_id == user_id)
        return int(db.execute(stmt).scalar_one())

    def list_by_user_id_with_status(
        self,
        db: Session,
        user_id: int,
        status: str,
        offset: int,
        limit: int,
    ) -> list[Notification]:
        stmt = (
            select(Notification)
            .where(Notification.user_id == user_id, Notification.status == status)
            .order_by(Notification.created_at.desc(), Notification.id.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(db.execute(stmt).scalars().all())

    def count_by_user_id_with_status(self, db: Session, user_id: int, status: str) -> int:
        stmt = (
            select(func.count())
            .select_from(Notification)
            .where(Notification.user_id == user_id, Notification.status == status)
        )
        return int(db.execute(stmt).scalar_one())

    def bulk_create(self, db: Session, notifications: list[Notification]) -> list[Notification]:
        db.bulk_save_objects(notifications, return_defaults=True)
        return notifications
