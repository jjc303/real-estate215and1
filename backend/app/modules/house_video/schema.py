from __future__ import annotations

from datetime import datetime
from typing import Literal

from app.common.base_schema import BaseSchema

HouseVideoStatus = Literal["active", "deleted"]


class HouseVideoReadSchema(BaseSchema):
    id: int
    house_id: int
    url: str
    object_key: str
    mime_type: str
    size_bytes: int
    duration: int | None = None
    status: HouseVideoStatus
    created_at: datetime
    updated_at: datetime
