from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.common.base_repository import BaseRepository
from app.modules.bill.model import Bill


class BillRepository(BaseRepository[Bill]):
    def __init__(self) -> None:
        super().__init__(Bill)

    def get_by_id_and_user_id(
        self,
        db: Session,
        bill_id: int,
        user_id: int,
    ) -> Bill | None:
        stmt = select(Bill).where(
            Bill.id == bill_id,
            or_(
                Bill.tenant_id == user_id,
                Bill.landlord_id == user_id,
            ),
        )
        return db.execute(stmt).scalar_one_or_none()

    def get_by_id_and_landlord_id(
        self,
        db: Session,
        bill_id: int,
        landlord_id: int,
    ) -> Bill | None:
        stmt = select(Bill).where(
            Bill.id == bill_id,
            Bill.landlord_id == landlord_id,
        )
        return db.execute(stmt).scalar_one_or_none()

    def list_related_to_user(
        self,
        db: Session,
        user_id: int,
        offset: int,
        limit: int,
    ) -> list[Bill]:
        stmt = (
            select(Bill)
            .where(
                or_(
                    Bill.tenant_id == user_id,
                    Bill.landlord_id == user_id,
                )
            )
            .order_by(Bill.created_at.desc(), Bill.id.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(db.execute(stmt).scalars().all())

    def count_related_to_user(self, db: Session, user_id: int) -> int:
        stmt = select(func.count()).select_from(Bill).where(
            or_(
                Bill.tenant_id == user_id,
                Bill.landlord_id == user_id,
            )
        )
        return int(db.execute(stmt).scalar_one())
