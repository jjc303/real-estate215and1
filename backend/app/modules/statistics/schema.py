from __future__ import annotations

from pydantic import Field

from app.common.base_schema import BaseSchema


class HouseUtilizationSchema(BaseSchema):
    total_houses: int = Field(ge=0)
    occupied_houses: int = Field(ge=0)
    utilization_rate: float = Field(ge=0.0)


class RentIncomeItemSchema(BaseSchema):
    month: str = Field(min_length=7, max_length=7)
    amount: float = Field(ge=0.0)


class RentIncomeSchema(BaseSchema):
    total_income: float = Field(ge=0.0)
    monthly_income: list[RentIncomeItemSchema]


class ActiveUsersSchema(BaseSchema):
    active_user_count: int = Field(ge=0)


class ComplaintRepairCountSchema(BaseSchema):
    repair_count: int = Field(ge=0)
    complaint_count: int = Field(ge=0)
