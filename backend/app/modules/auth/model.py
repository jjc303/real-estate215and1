from __future__ import annotations

from datetime import datetime
from typing import Literal

from sqlalchemy import Boolean, DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.common.base_model import BaseModel


EmailVerificationBizType = Literal["register", "login"]


class EmailVerificationCode(BaseModel):
    __tablename__ = "email_verification_codes"
    __table_args__ = (
        Index("ix_email_verification_codes_created_at", "created_at"),
    )

    email: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    code_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    biz_type: Mapped[EmailVerificationBizType] = mapped_column(String(20), nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="0")
