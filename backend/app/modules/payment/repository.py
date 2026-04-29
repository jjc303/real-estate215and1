from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.common.base_repository import BaseRepository
from app.modules.payment.model import Payment


class PaymentRepository(BaseRepository[Payment]):
    def __init__(self) -> None:
        super().__init__(Payment)

    def get_by_bill_id(self, db: Session, bill_id: int) -> Payment | None:
        stmt = select(Payment).where(Payment.bill_id == bill_id)
        return db.execute(stmt).scalar_one_or_none()

    def get_by_id_and_user_id(
        self,
        db: Session,
        payment_id: int,
        user_id: int,
    ) -> Payment | None:
        stmt = select(Payment).where(
            Payment.id == payment_id,
            or_(
                Payment.tenant_id == user_id,
                Payment.landlord_id == user_id,
            ),
        )
        return db.execute(stmt).scalar_one_or_none()

    def list_related_to_user(
        self,
        db: Session,
        user_id: int,
        offset: int,
        limit: int,
    ) -> list[Payment]:
        stmt = (
            select(Payment)
            .where(
                or_(
                    Payment.tenant_id == user_id,
                    Payment.landlord_id == user_id,
                )
            )
            .order_by(Payment.created_at.desc(), Payment.id.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(db.execute(stmt).scalars().all())

    def count_related_to_user(self, db: Session, user_id: int) -> int:
        stmt = select(func.count()).select_from(Payment).where(
            or_(
                Payment.tenant_id == user_id,
                Payment.landlord_id == user_id,
            )
        )
        return int(db.execute(stmt).scalar_one())
