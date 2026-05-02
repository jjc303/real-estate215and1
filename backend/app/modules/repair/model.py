from __future__ import annotations

from datetime import datetime
from typing import Literal

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.common.base_model import BaseModel
from app.common.enums import RepairStatus as RepairStatusValues


RepairStatus = Literal[
    RepairStatusValues.PENDING,
    RepairStatusValues.PROCESSING,
    RepairStatusValues.COMPLETED,
    RepairStatusValues.CLOSED,
    RepairStatusValues.REJECTED,
    RepairStatusValues.CANCELLED,
    RepairStatusValues.REOPENED,
]


class Repair(BaseModel):
    __tablename__ = "repairs"
    __table_args__ = (
        Index("ix_repairs_created_at", "created_at"),
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
    status: Mapped[RepairStatus] = mapped_column(
        String(20),
        nullable=False,
        server_default=RepairStatusValues.PENDING,
        index=True,
    )
    processed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    reopened_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
