from __future__ import annotations

from datetime import datetime

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.common.base_repository import BaseRepository
from app.modules.auth.model import EmailVerificationCode


class EmailVerificationCodeRepository(BaseRepository[EmailVerificationCode]):
    def __init__(self) -> None:
        super().__init__(EmailVerificationCode)

    def get_latest_unexpired_unused(
        self,
        db: Session,
        email: str,
        biz_type: str,
        now: datetime,
    ) -> EmailVerificationCode | None:
        stmt = (
            select(EmailVerificationCode)
            .where(
                EmailVerificationCode.email == email,
                EmailVerificationCode.biz_type == biz_type,
                EmailVerificationCode.is_used.is_(False),
                EmailVerificationCode.expires_at > now,
            )
            .order_by(desc(EmailVerificationCode.created_at), desc(EmailVerificationCode.id))
        )
        return db.execute(stmt).scalar_one_or_none()

    def get_latest_by_email_and_biz_type(
        self,
        db: Session,
        email: str,
        biz_type: str,
    ) -> EmailVerificationCode | None:
        stmt = (
            select(EmailVerificationCode)
            .where(
                EmailVerificationCode.email == email,
                EmailVerificationCode.biz_type == biz_type,
            )
            .order_by(desc(EmailVerificationCode.created_at), desc(EmailVerificationCode.id))
        )
        return db.execute(stmt).scalar_one_or_none()

    def mark_used(self, record: EmailVerificationCode) -> None:
        record.is_used = True
