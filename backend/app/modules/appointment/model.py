from __future__ import annotations

from datetime import datetime
from typing import Literal

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.common.base_model import BaseModel
from app.common.enums import AppointmentStatus as AppointmentStatusValues


AppointmentStatus = Literal[
    AppointmentStatusValues.PENDING,
    AppointmentStatusValues.CONFIRMED,
    AppointmentStatusValues.REJECTED,
    AppointmentStatusValues.CANCELLED,
    AppointmentStatusValues.EXPIRED,
]


class Appointment(BaseModel):
    __tablename__ = "appointments"

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
    appointment_time: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    remark: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[AppointmentStatus] = mapped_column(
        String(20),
        nullable=False,
        server_default=AppointmentStatusValues.PENDING,
    )
