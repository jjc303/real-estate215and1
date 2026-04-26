from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.common.base_model import BaseModel
from app.common.enums import ContractStatus as ContractStatusValues


ContractStatus = Literal[
    ContractStatusValues.PENDING,
    ContractStatusValues.ACTIVE,
    ContractStatusValues.REJECTED,
    ContractStatusValues.CANCELLED,
    ContractStatusValues.TERMINATED,
]


class Contract(BaseModel):
    __tablename__ = "contracts"

    house_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("houses.id"),
        nullable=False,
        index=True,
    )
    tenant_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    landlord_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    appointment_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("appointments.id"),
        nullable=False,
        index=True,
    )
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    monthly_rent: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    deposit: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[ContractStatus] = mapped_column(
        String(20),
        nullable=False,
        server_default=ContractStatusValues.PENDING,
        index=True,
    )
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
