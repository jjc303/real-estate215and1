from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.common.enums import NotificationStatus
from app.common.pagination import build_page_result, get_offset
from app.core.exceptions import (
    BadRequestException,
    ForbiddenException,
    InvalidNotificationStatusException,
    NotificationNotFoundException,
    UnauthorizedException,
    UserNotFoundException,
)
from app.modules.notification.model import Notification
from app.modules.notification.repository import NotificationRepository
from app.modules.notification.schema import NotificationReadSchema
from app.modules.user.model import User
from app.modules.user.repository import UserRepository


class NotificationService:
    def __init__(
        self,
        notification_repository: NotificationRepository,
        user_repository: UserRepository,
    ) -> None:
        self.notification_repository = notification_repository
        self.user_repository = user_repository

    def create_notification(
        self,
        db: Session,
        *,
        user_ids: list[int] | None = None,
        user_id: int | None = None,
        source_type: str,
        source_id: int,
        title: str,
        message: str,
        current_user_id: int | None = None,
        require_admin: bool = False,
        auto_commit: bool = True,
    ) -> list[dict[str, object]]:
        if require_admin:
            user = self._get_current_user(db, current_user_id)
            self._require_role(user, {"admin"})

        normalized_user_ids = self._normalize_user_ids(user_ids=user_ids, user_id=user_id)
        target_users = self.user_repository.list_by_ids(db, normalized_user_ids)
        existing_ids = {user.id for user in target_users}
        missing_ids = [target_user_id for target_user_id in normalized_user_ids if target_user_id not in existing_ids]
        if missing_ids:
            raise UserNotFoundException()

        now = self._utc_now()
        notifications = [
            Notification(
                user_id=target_user_id,
                source_type=source_type,
                source_id=source_id,
                title=title,
                message=message,
                status=NotificationStatus.UNREAD,
                created_at=now,
                updated_at=now,
            )
            for target_user_id in normalized_user_ids
        ]
        try:
            self.notification_repository.bulk_create(db, notifications)
            if auto_commit:
                db.commit()
            else:
                db.flush()
        except Exception:
            if auto_commit:
                db.rollback()
            raise

        return [self._serialize(notification) for notification in notifications]

    def _normalize_user_ids(
        self,
        *,
        user_ids: list[int] | None,
        user_id: int | None,
    ) -> list[int]:
        if user_ids is None and user_id is None:
            raise BadRequestException(message="bad request")
        if user_ids is not None and user_id is not None:
            raise BadRequestException(message="bad request")
        if user_id is not None:
            return [user_id]
        if user_ids is None or len(user_ids) == 0:
            raise BadRequestException(message="bad request")
        return user_ids

    def list_notifications(
        self,
        db: Session,
        current_user_id: int,
        page: int,
        page_size: int,
        status: str | None = None,
    ) -> dict[str, object]:
        self._get_current_user(db, current_user_id)
        offset = get_offset(page, page_size)

        if status is None:
            notifications = self.notification_repository.list_by_user_id(
                db,
                user_id=current_user_id,
                offset=offset,
                limit=page_size,
            )
            total = self.notification_repository.count_by_user_id(db, current_user_id)
        else:
            notifications = self.notification_repository.list_by_user_id_with_status(
                db,
                user_id=current_user_id,
                status=status,
                offset=offset,
                limit=page_size,
            )
            total = self.notification_repository.count_by_user_id_with_status(db, current_user_id, status)

        return build_page_result(
            items=[self._serialize(notification) for notification in notifications],
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_notification_detail(
        self,
        db: Session,
        current_user_id: int,
        notification_id: int,
    ) -> dict[str, object]:
        notification = self._get_visible_notification(db, current_user_id, notification_id)
        return self._serialize(notification)

    def mark_notification_read(
        self,
        db: Session,
        current_user_id: int,
        notification_id: int,
    ) -> dict[str, object]:
        notification = self._get_visible_notification(db, current_user_id, notification_id)
        if notification.status != NotificationStatus.UNREAD:
            raise InvalidNotificationStatusException()

        notification.status = NotificationStatus.READ
        notification.updated_at = self._next_updated_at(notification.updated_at)
        try:
            db.commit()
            db.refresh(notification)
        except Exception:
            db.rollback()
            raise

        return self._serialize(notification)

    def _get_current_user(self, db: Session, current_user_id: int | None) -> User:
        if current_user_id is None:
            raise UnauthorizedException(message="unauthorized")
        user = self.user_repository.get_by_id(db, current_user_id)
        if user is None:
            raise UnauthorizedException(message="unauthorized")
        return user

    def _require_role(self, user: User, allowed_roles: set[str]) -> None:
        if user.role not in allowed_roles:
            raise ForbiddenException()

    def _get_visible_notification(
        self,
        db: Session,
        current_user_id: int,
        notification_id: int,
    ) -> Notification:
        self._get_current_user(db, current_user_id)
        notification = self.notification_repository.get_by_id_and_user_id(db, notification_id, current_user_id)
        if notification is None:
            raise NotificationNotFoundException()
        return notification

    def _serialize(self, notification: Notification) -> dict[str, object]:
        return NotificationReadSchema.model_validate(notification).model_dump(mode="json")

    def _utc_now(self) -> datetime:
        return datetime.now(timezone.utc).replace(tzinfo=None)

    def _next_updated_at(self, previous_updated_at: datetime) -> datetime:
        now = self._utc_now()
        minimum_next = previous_updated_at.replace(microsecond=0) + timedelta(seconds=1)
        if now < minimum_next:
            return minimum_next
        return now
