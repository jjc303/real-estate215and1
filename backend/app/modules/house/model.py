from __future__ import annotations

from decimal import Decimal
from typing import Literal

from sqlalchemy import ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.common.base_model import BaseModel, SoftDeleteMixin
from app.common.enums import HouseStatus as HouseStatusValues


HouseStatus = Literal[
    HouseStatusValues.DRAFT,
    HouseStatusValues.LISTED,
    HouseStatusValues.RENTED,
    HouseStatusValues.OFFLINE,
    HouseStatusValues.MAINTENANCE,
]


class House(BaseModel, SoftDeleteMixin):
    __tablename__ = "houses"

    landlord_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    region: Mapped[str] = mapped_column(String(100), nullable=False)
    community: Mapped[str | None] = mapped_column(String(100), nullable=True)
    house_type: Mapped[str] = mapped_column(String(50), nullable=False)
    area: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    rent: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    deposit: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    decoration: Mapped[str | None] = mapped_column(String(50), nullable=True)
    floor: Mapped[str | None] = mapped_column(String(50), nullable=True)
    orientation: Mapped[str | None] = mapped_column(String(50), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[HouseStatus] = mapped_column(
        String(20),
        nullable=False,
        server_default=HouseStatusValues.DRAFT,
    )
