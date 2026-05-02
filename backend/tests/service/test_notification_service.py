from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

import pytest

BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.core.exceptions import BadRequestException, UserNotFoundException
from app.modules.notification.service import NotificationService


@dataclass
class DummyUser:
    id: int
    role: str = "tenant"


class FakeNotificationRepository:
    def __init__(self, should_fail: bool = False) -> None:
        self.should_fail = should_fail
        self.created = []
        self.next_id = 1

    def bulk_create(self, db, notifications):
        if self.should_fail:
            raise RuntimeError("bulk create failed")
        for notification in notifications:
            notification.id = self.next_id
            self.next_id += 1
        self.created.extend(notifications)
        return notifications


class FakeUserRepository:
    def list_by_ids(self, db, user_ids):
        return [DummyUser(id=user_id) for user_id in user_ids if user_id != 999999]

    def get_by_id(self, db, user_id):
        return DummyUser(id=user_id, role="admin")


class FakeSession:
    def __init__(self) -> None:
        self.committed = False
        self.rolled_back = False
        self.flushed = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True

    def flush(self) -> None:
        self.flushed = True


def test_create_notification_single_user_success() -> None:
    db = FakeSession()
    repository = FakeNotificationRepository()
    service = NotificationService(repository, FakeUserRepository())

    result = service.create_notification(
        db,
        user_id=1,
        source_type="news",
        source_id=1,
        title="Announcement",
        message="Single notification",
        auto_commit=True,
    )

    assert db.committed is True
    assert db.rolled_back is False
    assert len(repository.created) == 1
    assert len(result) == 1
    assert result[0]["user_id"] == 1


def test_create_notification_multi_user_success() -> None:
    db = FakeSession()
    repository = FakeNotificationRepository()
    service = NotificationService(repository, FakeUserRepository())

    result = service.create_notification(
        db,
        user_ids=[1, 2, 3],
        source_type="news",
        source_id=1,
        title="Announcement",
        message="Bulk notification",
        auto_commit=True,
    )

    assert db.committed is True
    assert db.rolled_back is False
    assert len(repository.created) == 3
    assert [item["user_id"] for item in result] == [1, 2, 3]


def test_create_notification_rolls_back_on_bulk_failure() -> None:
    db = FakeSession()
    repository = FakeNotificationRepository(should_fail=True)
    service = NotificationService(repository, FakeUserRepository())

    with pytest.raises(RuntimeError):
        service.create_notification(
            db,
            user_ids=[1, 2],
            source_type="news",
            source_id=1,
            title="Announcement",
            message="Bulk notification",
            auto_commit=True,
        )

    assert db.committed is False
    assert db.rolled_back is True


def test_create_notification_rejects_missing_user() -> None:
    db = FakeSession()
    repository = FakeNotificationRepository()
    service = NotificationService(repository, FakeUserRepository())

    with pytest.raises(UserNotFoundException):
        service.create_notification(
            db,
            user_ids=[1, 999999],
            source_type="news",
            source_id=1,
            title="Announcement",
            message="Bulk notification",
            auto_commit=True,
        )

    assert repository.created == []


@pytest.mark.parametrize(
    ("user_id", "user_ids"),
    [
        (None, None),
        (1, [1]),
        (None, []),
    ],
)
def test_create_notification_validates_target_arguments(
    user_id: int | None,
    user_ids: list[int] | None,
) -> None:
    db = FakeSession()
    repository = FakeNotificationRepository()
    service = NotificationService(repository, FakeUserRepository())

    with pytest.raises(BadRequestException):
        service.create_notification(
            db,
            user_id=user_id,
            user_ids=user_ids,
            source_type="news",
            source_id=1,
            title="Announcement",
            message="Bulk notification",
            auto_commit=True,
        )


def test_create_notification_flushes_without_rollback_when_auto_commit_disabled() -> None:
    db = FakeSession()
    repository = FakeNotificationRepository()
    service = NotificationService(repository, FakeUserRepository())

    result = service.create_notification(
        db,
        user_ids=[1, 2],
        source_type="news",
        source_id=1,
        title="Announcement",
        message="Bulk notification",
        auto_commit=False,
    )

    assert db.committed is False
    assert db.rolled_back is False
    assert db.flushed is True
    assert [item["user_id"] for item in result] == [1, 2]
