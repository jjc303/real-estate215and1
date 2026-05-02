from __future__ import annotations

from decimal import Decimal

from sqlalchemy import distinct, extract, func, select
from sqlalchemy.orm import Session

from app.common.enums import ContractStatus, PaymentStatus
from app.modules.bill.model import Bill
from app.modules.complaint.model import Complaint
from app.modules.contract.model import Contract
from app.modules.house.model import House
from app.modules.payment.model import Payment
from app.modules.repair.model import Repair
from app.modules.user.model import User


class StatisticsRepository:
    def count_total_houses(self, db: Session) -> int:
        stmt = select(func.count()).select_from(House).where(House.deleted_at.is_(None))
        return int(db.execute(stmt).scalar_one())

    def count_occupied_houses(self, db: Session) -> int:
        stmt = (
            select(func.count(distinct(Contract.house_id)))
            .select_from(Contract)
            .join(House, House.id == Contract.house_id)
            .where(
                Contract.status == ContractStatus.ACTIVE,
                House.deleted_at.is_(None),
            )
        )
        return int(db.execute(stmt).scalar_one())

    def sum_total_rent_income(self, db: Session) -> Decimal:
        stmt = (
            select(func.coalesce(func.sum(Payment.amount), 0))
            .select_from(Payment)
            .join(Bill, Bill.id == Payment.bill_id)
            .where(
                Payment.status == PaymentStatus.SUCCESS,
                Bill.bill_type == "rent",
            )
        )
        return db.execute(stmt).scalar_one()

    def list_monthly_rent_income(self, db: Session) -> list[tuple[int, int, Decimal]]:
        stmt = (
            select(
                extract("year", Payment.paid_at),
                extract("month", Payment.paid_at),
                func.coalesce(func.sum(Payment.amount), 0),
            )
            .select_from(Payment)
            .join(Bill, Bill.id == Payment.bill_id)
            .where(
                Payment.status == PaymentStatus.SUCCESS,
                Bill.bill_type == "rent",
            )
            .group_by(
                extract("year", Payment.paid_at),
                extract("month", Payment.paid_at),
            )
            .order_by(
                extract("year", Payment.paid_at),
                extract("month", Payment.paid_at),
            )
        )
        rows = db.execute(stmt).all()
        return [(int(year), int(month), amount) for year, month, amount in rows]

    def count_active_users(self, db: Session) -> int:
        stmt = select(func.count()).select_from(User).where(User.status == "active")
        return int(db.execute(stmt).scalar_one())

    def count_repairs(self, db: Session) -> int:
        stmt = select(func.count()).select_from(Repair)
        return int(db.execute(stmt).scalar_one())

    def count_complaints(self, db: Session) -> int:
        stmt = select(func.count()).select_from(Complaint)
        return int(db.execute(stmt).scalar_one())
