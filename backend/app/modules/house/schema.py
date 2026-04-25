from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


HouseStatus = Literal["draft", "listed", "offline"]


class HouseCreateSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=100)
    address: str = Field(min_length=1, max_length=255)
    region: str = Field(min_length=1, max_length=100)
    community: str | None = Field(default=None, max_length=100)
    house_type: str = Field(min_length=1, max_length=50)
    area: Decimal = Field(gt=0)
    rent: Decimal = Field(ge=0)
    deposit: Decimal = Field(ge=0)
    decoration: str | None = Field(default=None, max_length=50)
    floor: str | None = Field(default=None, max_length=50)
    orientation: str | None = Field(default=None, max_length=50)
    description: str | None = None


class HouseUpdateSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=100)
    address: str = Field(min_length=1, max_length=255)
    region: str = Field(min_length=1, max_length=100)
    community: str | None = Field(default=None, max_length=100)
    house_type: str = Field(min_length=1, max_length=50)
    area: Decimal = Field(gt=0)
    rent: Decimal = Field(ge=0)
    deposit: Decimal = Field(ge=0)
    decoration: str | None = Field(default=None, max_length=50)
    floor: str | None = Field(default=None, max_length=50)
    orientation: str | None = Field(default=None, max_length=50)
    description: str | None = None


class HouseListQuerySchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
    mine: bool = False
    region: str | None = Field(default=None, min_length=1, max_length=100)
    house_type: str | None = Field(default=None, min_length=1, max_length=50)
    min_rent: Decimal | None = Field(default=None, ge=0)
    max_rent: Decimal | None = Field(default=None, ge=0)
    keyword: str | None = Field(default=None, min_length=1, max_length=255)
    min_area: Decimal | None = Field(default=None, ge=0)
    max_area: Decimal | None = Field(default=None, ge=0)

    @field_validator("region", "house_type", "keyword", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: object) -> object:
        if not isinstance(value, str):
            return value

        value = value.strip()
        if value == "":
            return None
        return value

    @model_validator(mode="after")
    def validate_ranges(self) -> "HouseListQuerySchema":
        if self.min_rent is not None and self.max_rent is not None and self.min_rent > self.max_rent:
            raise ValueError("min_rent cannot be greater than max_rent")
        if self.min_area is not None and self.max_area is not None and self.min_area > self.max_area:
            raise ValueError("min_area cannot be greater than max_area")
        return self


class HouseReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    landlord_id: int
    title: str
    address: str
    region: str
    community: str | None = None
    house_type: str
    area: Decimal
    rent: Decimal
    deposit: Decimal
    decoration: str | None = None
    floor: str | None = None
    orientation: str | None = None
    description: str | None = None
    status: HouseStatus
    created_at: datetime
    updated_at: datetime
