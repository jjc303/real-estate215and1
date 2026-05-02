from __future__ import annotations

from typing import Literal

from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.common.base_model import BaseModel
from app.common.enums import NotificationStatus as NotificationStatusValues


NotificationStatus = Literal[
    NotificationStatusValues.UNREAD,
    NotificationStatusValues.READ,
]


class Notification(BaseModel):
    __tablename__ = "notifications"
    __table_args__ = (
        Index("ix_notifications_created_at", "created_at"),
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_id: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[NotificationStatus] = mapped_column(
        String(20),
        nullable=False,
        server_default=NotificationStatusValues.UNREAD,
        index=True,
    )
