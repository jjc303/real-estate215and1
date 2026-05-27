from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from app.common.base_schema import BaseSchema

HouseImageStatus = Literal["active", "deleted"]


class HouseImageReadSchema(BaseSchema):
    id: int
    house_id: int
    url: str
    object_key: str
    mime_type: str
    size_bytes: int
    width: int | None = None
    height: int | None = None
    sort_order: int
    is_cover: bool
    status: HouseImageStatus
    created_at: datetime
    updated_at: datetime


class HouseImageUpdateSchema(BaseSchema):
    sort_order: int | None = Field(default=None, ge=0, le=9999)
    is_cover: bool | None = None
