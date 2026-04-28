from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import Field, field_validator

from app.common.base_schema import BaseSchema
from app.common.enums import PaymentMethod as PaymentMethodValues
from app.common.enums import PaymentStatus as PaymentStatusValues


PaymentMethod = Literal[
    PaymentMethodValues.MOCK,
    PaymentMethodValues.OFFLINE,
]

PaymentStatus = Literal[
    PaymentStatusValues.SUCCESS,
]


class PaymentCreateSchema(BaseSchema):
    bill_id: int = Field(ge=1)
    amount: Decimal = Field(gt=0)
    payment_method: PaymentMethod
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


class PaymentListQuerySchema(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)


class PaymentReadSchema(BaseSchema):
    id: int
    bill_id: int
    contract_id: int
    house_id: int
    tenant_id: int
    landlord_id: int
    amount: Decimal
    payment_method: PaymentMethod
    status: PaymentStatus
    paid_at: datetime
    remark: str | None = None
    created_at: datetime
    updated_at: datetime
