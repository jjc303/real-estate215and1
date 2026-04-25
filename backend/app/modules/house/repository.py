from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.house.model import House


class HouseRepository:
    def create(self, db: Session, house: House) -> House:
        db.add(house)
        return house

    def get_by_id(self, db: Session, house_id: int) -> House | None:
        stmt = select(House).where(House.id == house_id)
        return db.execute(stmt).scalar_one_or_none()

    def get_by_id_and_landlord_id(
        self,
        db: Session,
        house_id: int,
        landlord_id: int,
    ) -> House | None:
        stmt = select(House).where(
            House.id == house_id,
            House.landlord_id == landlord_id,
            House.deleted_at.is_(None),
        )
        return db.execute(stmt).scalar_one_or_none()

    def list_public(self, db: Session, offset: int, limit: int) -> list[House]:
        stmt = (
            select(House)
            .where(House.deleted_at.is_(None), House.status == "listed")
            .order_by(House.id.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(db.execute(stmt).scalars().all())

    def count_public(self, db: Session) -> int:
        stmt = select(func.count()).select_from(House).where(
            House.deleted_at.is_(None),
            House.status == "listed",
        )
        return int(db.execute(stmt).scalar_one())

    def list_by_landlord(
        self,
        db: Session,
        landlord_id: int,
        offset: int,
        limit: int,
    ) -> list[House]:
        stmt = (
            select(House)
            .where(House.deleted_at.is_(None), House.landlord_id == landlord_id)
            .order_by(House.id.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(db.execute(stmt).scalars().all())

    def count_by_landlord(self, db: Session, landlord_id: int) -> int:
        stmt = select(func.count()).select_from(House).where(
            House.deleted_at.is_(None),
            House.landlord_id == landlord_id,
        )
        return int(db.execute(stmt).scalar_one())
