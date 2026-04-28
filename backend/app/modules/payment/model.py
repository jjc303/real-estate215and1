from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.common.base_model import BaseModel
from app.common.enums import PaymentMethod as PaymentMethodValues
from app.common.enums import PaymentStatus as PaymentStatusValues


PaymentMethod = Literal[
    PaymentMethodValues.MOCK,
    PaymentMethodValues.OFFLINE,
]

PaymentStatus = Literal[
    PaymentStatusValues.SUCCESS,
]


class Payment(BaseModel):
    __tablename__ = "payments"
    __table_args__ = (
        UniqueConstraint("bill_id", name="uq_payments_bill_id"),
        Index("ix_payments_created_at", "created_at"),
    )

    bill_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("bills.id"),
        nullable=False,
    )
    contract_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("contracts.id"),
        nullable=False,
    )
    house_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("houses.id"),
        nullable=False,
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
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    payment_method: Mapped[PaymentMethod] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )
    status: Mapped[PaymentStatus] = mapped_column(
        String(20),
        nullable=False,
        server_default=PaymentStatusValues.SUCCESS,
        index=True,
    )
    paid_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
