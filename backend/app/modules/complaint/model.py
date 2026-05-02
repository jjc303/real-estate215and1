from __future__ import annotations

from datetime import datetime
from typing import Literal

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.common.base_model import BaseModel
from app.common.enums import ComplaintStatus as ComplaintStatusValues


ComplaintStatus = Literal[
    ComplaintStatusValues.PENDING,
    ComplaintStatusValues.PROCESSING,
    ComplaintStatusValues.RESOLVED,
    ComplaintStatusValues.CLOSED,
    ComplaintStatusValues.REJECTED,
]


class Complaint(BaseModel):
    __tablename__ = "complaints"
    __table_args__ = (
        Index("ix_complaints_created_at", "created_at"),
    )

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
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ComplaintStatus] = mapped_column(
        String(20),
        nullable=False,
        server_default=ComplaintStatusValues.PENDING,
        index=True,
    )
    processed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
