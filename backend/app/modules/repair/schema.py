from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field, field_validator

from app.common.base_schema import BaseSchema
from app.common.enums import RepairStatus as RepairStatusValues


RepairStatus = Literal[
    RepairStatusValues.PENDING,
    RepairStatusValues.PROCESSING,
    RepairStatusValues.COMPLETED,
    RepairStatusValues.CLOSED,
    RepairStatusValues.REJECTED,
    RepairStatusValues.CANCELLED,
    RepairStatusValues.REOPENED,
]


class RepairCreateSchema(BaseSchema):
    contract_id: int = Field(ge=1)
    description: str = Field(min_length=1, max_length=2000)

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        return value.strip()


class RepairListQuerySchema(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
    status: RepairStatus | None = None


class RepairReadSchema(BaseSchema):
    id: int
    contract_id: int
    house_id: int
    tenant_id: int
    landlord_id: int
    description: str
    status: RepairStatus
    processed_at: datetime | None = None
    completed_at: datetime | None = None
    closed_at: datetime | None = None
    rejected_at: datetime | None = None
    cancelled_at: datetime | None = None
    reopened_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
