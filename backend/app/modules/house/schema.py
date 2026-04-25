from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


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
