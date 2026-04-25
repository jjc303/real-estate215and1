from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import Field, field_validator

from app.common.base_schema import BaseSchema
from app.common.enums import AppointmentStatus as AppointmentStatusValues
from app.modules.house.schema import HouseStatus


AppointmentStatus = Literal[
    AppointmentStatusValues.PENDING,
    AppointmentStatusValues.CONFIRMED,
    AppointmentStatusValues.REJECTED,
    AppointmentStatusValues.CANCELLED,
    AppointmentStatusValues.EXPIRED,
]
AppointmentRelationRole = Literal["tenant", "landlord"]


class AppointmentCreateSchema(BaseSchema):

    house_id: int = Field(ge=1)
    appointment_time: datetime
    remark: str | None = Field(default=None, max_length=1000)

    @field_validator("remark", mode="before")
    @classmethod
    def normalize_remark(cls, value: object) -> object:
        if not isinstance(value, str):
            return value

        value = value.strip()
        if value == "":
            return None
        return value


class AppointmentListQuerySchema(BaseSchema):

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)


class AppointmentHouseSummarySchema(BaseSchema):

    id: int
    title: str
    region: str
    address: str
    house_type: str
    area: Decimal
    rent: Decimal
    deposit: Decimal
    status: HouseStatus


class AppointmentReadSchema(BaseSchema):
    id: int
    house_id: int
    tenant_id: int
    landlord_id: int
    appointment_time: datetime
    remark: str | None = None
    status: AppointmentStatus
    display_status: AppointmentStatus
    created_at: datetime
    updated_at: datetime
    relation_role: AppointmentRelationRole
    house: AppointmentHouseSummarySchema
