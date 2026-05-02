from __future__ import annotations

from typing import Literal

from sqlalchemy import ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.common.base_model import BaseModel
from app.common.enums import OperationLogModule as OperationLogModuleValues


OperationLogModule = Literal[
    OperationLogModuleValues.REPAIR,
    OperationLogModuleValues.COMPLAINT,
    OperationLogModuleValues.CONTRACT,
    OperationLogModuleValues.BILL,
    OperationLogModuleValues.PAYMENT,
    OperationLogModuleValues.NEWS,
]


class OperationLog(BaseModel):
    __tablename__ = "operation_logs"
    __table_args__ = (
        Index("ix_operation_logs_created_at", "created_at"),
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    module: Mapped[OperationLogModule] = mapped_column(String(50), nullable=False, index=True)
    record_id: Mapped[int] = mapped_column(Integer, nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    before_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    after_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
