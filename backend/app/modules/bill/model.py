from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Literal

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.common.base_model import BaseModel
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


class Bill(BaseModel):
    __tablename__ = "bills"

    contract_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("contracts.id"),
        nullable=False,
        index=True,
    )
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
    bill_type: Mapped[BillType] = mapped_column(String(20), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    status: Mapped[BillStatus] = mapped_column(
        String(20),
        nullable=False,
        server_default=BillStatusValues.UNPAID,
        index=True,
    )
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
