from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.modules.bill.model import Bill
from app.modules.contract.model import Contract
from app.modules.house.model import House
from app.modules.user.model import User


class AdminRepository:
    def list_all_users(
        self, db: Session, offset: int, limit: int,
        keyword: str | None = None,
        role: str | None = None,
    ) -> list[User]:
        stmt = select(User).order_by(User.id.desc())
        if keyword is not None:
            pattern = f"%{keyword}%"
            stmt = stmt.where(
                or_(
                    User.username.ilike(pattern),
                    User.phone.ilike(pattern),
                    User.email.ilike(pattern),
                )
            )
        if role is not None:
            stmt = stmt.where(User.role == role)
        stmt = stmt.offset(offset).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def count_all_users(
        self, db: Session,
        keyword: str | None = None,
        role: str | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(User)
        if keyword is not None:
            pattern = f"%{keyword}%"
            stmt = stmt.where(
                or_(
                    User.username.ilike(pattern),
                    User.phone.ilike(pattern),
                    User.email.ilike(pattern),
                )
            )
        if role is not None:
            stmt = stmt.where(User.role == role)
        return int(db.execute(stmt).scalar_one())

    def list_all_houses(
        self,
        db: Session,
        offset: int,
        limit: int,
        region: str | None = None,
        house_type: str | None = None,
        min_rent: Decimal | None = None,
        max_rent: Decimal | None = None,
        keyword: str | None = None,
        min_area: Decimal | None = None,
        max_area: Decimal | None = None,
        status: str | None = None,
    ) -> list[House]:
        stmt = select(House).where(House.deleted_at.is_(None))
        stmt = self._apply_house_filters(
            stmt,
            region=region,
            house_type=house_type,
            min_rent=min_rent,
            max_rent=max_rent,
            keyword=keyword,
            min_area=min_area,
            max_area=max_area,
            status=status,
        )
        stmt = stmt.order_by(House.id.desc()).offset(offset).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def count_all_houses(
        self,
        db: Session,
        region: str | None = None,
        house_type: str | None = None,
        min_rent: Decimal | None = None,
        max_rent: Decimal | None = None,
        keyword: str | None = None,
        min_area: Decimal | None = None,
        max_area: Decimal | None = None,
        status: str | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(House).where(House.deleted_at.is_(None))
        stmt = self._apply_house_filters(
            stmt,
            region=region,
            house_type=house_type,
            min_rent=min_rent,
            max_rent=max_rent,
            keyword=keyword,
            min_area=min_area,
            max_area=max_area,
            status=status,
        )
        return int(db.execute(stmt).scalar_one())

    def get_house_by_id_admin(self, db: Session, house_id: int) -> House | None:
        stmt = select(House).where(House.id == house_id, House.deleted_at.is_(None))
        return db.execute(stmt).scalar_one_or_none()

    def list_all_contracts(
        self, db: Session, offset: int, limit: int,
        keyword: str | None = None,
        status: str | None = None,
    ) -> list[tuple[Contract, House]]:
        stmt = (
            select(Contract, House)
            .join(House, House.id == Contract.house_id)
        )
        if keyword is not None:
            pattern = f"%{keyword}%"
            stmt = stmt.where(House.title.ilike(pattern))
        if status is not None:
            stmt = stmt.where(Contract.status == status)
        stmt = stmt.order_by(Contract.created_at.desc(), Contract.id.desc()).offset(offset).limit(limit)
        return list(db.execute(stmt).all())

    def count_all_contracts(
        self, db: Session,
        keyword: str | None = None,
        status: str | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(Contract)
        if keyword is not None:
            pattern = f"%{keyword}%"
            stmt = stmt.where(Contract.house_id.in_(
                select(House.id).where(House.title.ilike(pattern))
            ))
        if status is not None:
            stmt = stmt.where(Contract.status == status)
        return int(db.execute(stmt).scalar_one())

    def get_contract_by_id_admin(self, db: Session, contract_id: int) -> tuple[Contract, House] | None:
        stmt = (
            select(Contract, House)
            .join(House, House.id == Contract.house_id)
            .where(Contract.id == contract_id)
        )
        return db.execute(stmt).one_or_none()

    def list_all_bills(
        self, db: Session, offset: int, limit: int,
        keyword: str | None = None,
        status: str | None = None,
        bill_type: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> list[Bill]:
        stmt = select(Bill).join(House, House.id == Bill.house_id, isouter=True)
        if keyword is not None:
            pattern = f"%{keyword}%"
            stmt = stmt.where(House.title.ilike(pattern))
        if status is not None:
            stmt = stmt.where(Bill.status == status)
        if bill_type is not None:
            stmt = stmt.where(Bill.bill_type == bill_type)
        if date_from is not None:
            stmt = stmt.where(Bill.created_at >= date_from)
        if date_to is not None:
            stmt = stmt.where(Bill.created_at <= date_to)
        stmt = stmt.order_by(Bill.created_at.desc(), Bill.id.desc()).offset(offset).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def count_all_bills(
        self, db: Session,
        keyword: str | None = None,
        status: str | None = None,
        bill_type: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(Bill).join(House, House.id == Bill.house_id, isouter=True)
        if keyword is not None:
            pattern = f"%{keyword}%"
            stmt = stmt.where(House.title.ilike(pattern))
        if status is not None:
            stmt = stmt.where(Bill.status == status)
        if bill_type is not None:
            stmt = stmt.where(Bill.bill_type == bill_type)
        if date_from is not None:
            stmt = stmt.where(Bill.created_at >= date_from)
        if date_to is not None:
            stmt = stmt.where(Bill.created_at <= date_to)
        return int(db.execute(stmt).scalar_one())

    def _apply_house_filters(
        self,
        stmt: Select,
        *,
        region: str | None = None,
        house_type: str | None = None,
        min_rent: Decimal | None = None,
        max_rent: Decimal | None = None,
        keyword: str | None = None,
        min_area: Decimal | None = None,
        max_area: Decimal | None = None,
        status: str | None = None,
    ) -> Select:
        if region is not None:
            stmt = stmt.where(House.region == region)
        if house_type is not None:
            stmt = stmt.where(House.house_type == house_type)
        if min_rent is not None:
            stmt = stmt.where(House.rent >= min_rent)
        if max_rent is not None:
            stmt = stmt.where(House.rent <= max_rent)
        if min_area is not None:
            stmt = stmt.where(House.area >= min_area)
        if max_area is not None:
            stmt = stmt.where(House.area <= max_area)
        if keyword is not None:
            pattern = f"%{keyword}%"
            stmt = stmt.where(
                or_(
                    House.title.ilike(pattern),
                    House.address.ilike(pattern),
                    House.community.ilike(pattern),
                    House.description.ilike(pattern),
                )
            )
        if status is not None:
            stmt = stmt.where(House.status == status)
        return stmt
