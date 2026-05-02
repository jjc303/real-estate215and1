from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field, field_validator

from app.common.base_schema import BaseSchema
from app.common.enums import NotificationStatus as NotificationStatusValues


NotificationStatus = Literal[
    NotificationStatusValues.UNREAD,
    NotificationStatusValues.READ,
]


class NotificationCreateSchema(BaseSchema):
    user_id: int = Field(ge=1)
    source_type: str = Field(min_length=1, max_length=50)
    source_id: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1, max_length=2000)

    @field_validator("source_type", "title", "message", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        return value.strip()


class NotificationListQuerySchema(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
    status: NotificationStatus | None = None


class NotificationReadSchema(BaseSchema):
    id: int
    user_id: int
    source_type: str
    source_id: int
    title: str
    message: str
    status: NotificationStatus
    created_at: datetime
    updated_at: datetime
