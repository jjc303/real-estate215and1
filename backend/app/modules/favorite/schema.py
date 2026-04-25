from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import Field

from app.common.base_schema import BaseSchema
from app.modules.house.schema import HouseStatus


class FavoriteCreateSchema(BaseSchema):

    house_id: int = Field(ge=1)


class FavoriteListQuerySchema(BaseSchema):

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)


class FavoriteHouseSummarySchema(BaseSchema):

    id: int
    title: str
    region: str
    address: str
    house_type: str
    area: Decimal
    rent: Decimal
    deposit: Decimal
    status: HouseStatus


class FavoriteReadSchema(BaseSchema):
    house_id: int
    favorite_created_at: datetime
    house: FavoriteHouseSummarySchema
