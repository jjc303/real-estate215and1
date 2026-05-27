from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import Field, field_validator

from app.common.base_schema import BaseSchema
from app.common.enums import ContractStatus as ContractStatusValues
from app.modules.complaint.schema import ComplaintReadSchema
from app.modules.contract.schema import ContractReadSchema
from app.modules.house.schema import HouseReadSchema
from app.modules.repair.schema import RepairReadSchema


UserStatus = Literal["active", "disabled"]
UserRole = Literal["tenant", "landlord", "admin"]
ContractAdminStatus = Literal[
    ContractStatusValues.ACTIVE,
    ContractStatusValues.TERMINATED,
    ContractStatusValues.CANCELLED,
]


class UserAdminSchema(BaseSchema):
    id: int
    username: str
    role: UserRole
    real_name: str | None = None
    phone: str | None = None
    email: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime


class UserAdminCreateSchema(BaseSchema):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=6, max_length=255)
    role: UserRole = "tenant"
    real_name: str | None = Field(default=None, max_length=50)
    phone: str | None = Field(default=None, max_length=20)
    email: str | None = Field(default=None, max_length=100)
    status: UserStatus = "active"

    @field_validator("username", "real_name", "phone", "email", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        value = value.strip()
        if value == "":
            return None
        return value


class UserAdminUpdateSchema(BaseSchema):
    username: str = Field(min_length=1, max_length=50)
    password: str | None = Field(default=None, min_length=6, max_length=255)
    role: UserRole
    real_name: str | None = Field(default=None, max_length=50)
    phone: str | None = Field(default=None, max_length=20)
    email: str | None = Field(default=None, max_length=100)

    @field_validator("username", "password", "real_name", "phone", "email", mode="before")
    @classmethod
    def normalize_update_text(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        value = value.strip()
        if value == "":
            return None
        return value


class UserAdminStatusSchema(BaseSchema):
    status: UserStatus


class UserAdminListQuerySchema(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)


class HouseAdminSchema(HouseReadSchema):
    pass


class HouseAdminListQuerySchema(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
    region: str | None = Field(default=None, min_length=1, max_length=100)
    house_type: str | None = Field(default=None, min_length=1, max_length=50)
    min_rent: Decimal | None = Field(default=None, ge=0)
    max_rent: Decimal | None = Field(default=None, ge=0)
    keyword: str | None = Field(default=None, min_length=1, max_length=255)
    min_area: Decimal | None = Field(default=None, ge=0)
    max_area: Decimal | None = Field(default=None, ge=0)

    @field_validator("region", "house_type", "keyword", mode="before")
    @classmethod
    def normalize_house_query_text(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        value = value.strip()
        if value == "":
            return None
        return value


class ComplaintAdminSchema(ComplaintReadSchema):
    pass


class RepairAdminSchema(RepairReadSchema):
    pass


class ContractAdminSchema(ContractReadSchema):
    pass


class ContractAdminListQuerySchema(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)


class ContractAdminStatusSchema(BaseSchema):
    status: ContractAdminStatus
