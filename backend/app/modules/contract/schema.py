from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import Field, field_validator

from app.common.base_schema import BaseSchema
from app.common.enums import ContractStatus as ContractStatusValues
from app.modules.house.schema import HouseStatus


ContractStatus = Literal[
    ContractStatusValues.PENDING,
    ContractStatusValues.ACTIVE,
    ContractStatusValues.REJECTED,
    ContractStatusValues.CANCELLED,
    ContractStatusValues.TERMINATED,
]


class ContractCreateSchema(BaseSchema):
    appointment_id: int = Field(ge=1)
    start_date: date
    end_date: date
    monthly_rent: Decimal = Field(ge=0)
    deposit: Decimal = Field(ge=0)
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


class ContractListQuerySchema(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)


class ContractHouseSummarySchema(BaseSchema):
    id: int
    title: str
    region: str
    address: str
    house_type: str
    area: Decimal
    rent: Decimal
    deposit: Decimal
    status: HouseStatus


class ContractReadSchema(BaseSchema):
    id: int
    house_id: int
    tenant_id: int
    landlord_id: int
    appointment_id: int
    start_date: date
    end_date: date
    monthly_rent: Decimal
    deposit: Decimal
    status: ContractStatus
    remark: str | None = None
    created_at: datetime
    updated_at: datetime
    house: ContractHouseSummarySchema
