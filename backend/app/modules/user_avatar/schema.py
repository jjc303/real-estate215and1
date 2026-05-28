from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from app.common.base_schema import BaseSchema

UserAvatarStatus = Literal["active", "deleted"]


class UserAvatarReadSchema(BaseSchema):
    id: int
    user_id: int
    url: str
    object_key: str
    mime_type: str
    size_bytes: int
    width: int | None = None
    height: int | None = None
    is_current: bool
    status: UserAvatarStatus
    created_at: datetime
    updated_at: datetime


class UserAvatarListQuerySchema(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
