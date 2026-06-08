from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import Field, field_validator

from app.common.base_schema import BaseSchema
from app.common.enums import BillStatus as BillStatusValues
from app.common.enums import BillType as BillTypeValues


BillType = Literal[
    BillTypeValues.RENT,
    BillTypeValues.DEPOSIT,
    BillTypeValues.OTHER,
]

BillStatus = Literal[
    BillStatusValues.UNPAID,
    BillStatusValues.PAID,
    BillStatusValues.CANCELLED,
    BillStatusValues.OVERDUE,
]


class BillCreateSchema(BaseSchema):
    contract_id: int = Field(ge=1)
    bill_type: BillType
    amount: Decimal = Field(gt=0)
    due_date: date
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


class BillListQuerySchema(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)


class BillReadSchema(BaseSchema):
    id: int
    contract_id: int
    house_id: int
    tenant_id: int
    landlord_id: int
    bill_type: BillType
    amount: Decimal
    due_date: date
    status: BillStatus
    remark: str | None = None
    created_at: datetime
    updated_at: datetime


class MonthlyIncomeItem(BaseSchema):
    month: str
    amount: float


class LandlordIncomeSummarySchema(BaseSchema):
    total_income: float
    pending_amount: float
    overdue_amount: float
    unpaid_count: int
    monthly_income: list[MonthlyIncomeItem]
