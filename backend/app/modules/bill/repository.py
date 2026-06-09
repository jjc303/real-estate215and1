from __future__ import annotations

from datetime import date, datetime, timedelta

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.common.base_repository import BaseRepository
from app.common.enums import BillStatus
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

    def sum_paid_by_landlord(self, db: Session, landlord_id: int) -> float:
        stmt = select(func.coalesce(func.sum(Bill.amount), 0)).where(
            Bill.landlord_id == landlord_id,
            Bill.status == BillStatus.PAID,
        )
        return float(db.execute(stmt).scalar())

    def sum_unpaid_by_landlord(self, db: Session, landlord_id: int) -> float:
        stmt = select(func.coalesce(func.sum(Bill.amount), 0)).where(
            Bill.landlord_id == landlord_id,
            Bill.status == BillStatus.UNPAID,
        )
        return float(db.execute(stmt).scalar())

    def sum_overdue_by_landlord(self, db: Session, landlord_id: int) -> float:
        stmt = select(func.coalesce(func.sum(Bill.amount), 0)).where(
            Bill.landlord_id == landlord_id,
            Bill.status == BillStatus.OVERDUE,
        )
        return float(db.execute(stmt).scalar())

    def count_by_status(self, db: Session, landlord_id: int) -> dict[str, int]:
        stmt = select(
            Bill.status,
            func.count(Bill.id),
        ).where(
            Bill.landlord_id == landlord_id,
        ).group_by(Bill.status)
        return {row[0]: row[1] for row in db.execute(stmt).all()}

    def list_monthly_income_by_landlord(
        self, db: Session, landlord_id: int, months: int = 12
    ) -> list[tuple[str, float]]:
        since = date.today() - timedelta(days=months * 30)
        stmt = select(
            func.date_format(Bill.updated_at, "%Y-%m").label("month"),
            func.coalesce(func.sum(Bill.amount), 0).label("amount"),
        ).where(
            Bill.landlord_id == landlord_id,
            Bill.status == BillStatus.PAID,
            Bill.updated_at >= since,
        ).group_by("month").order_by("month")
        return [(str(row[0]), float(row[1])) for row in db.execute(stmt).all()]

    def list_overdue_unpaid(self, db: Session) -> list[Bill]:
        stmt = select(Bill).where(
            Bill.status == BillStatus.UNPAID,
            Bill.due_date < date.today(),
        )
        return list(db.execute(stmt).scalars().all())
