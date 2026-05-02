from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.common.base_repository import BaseRepository
from app.modules.repair.model import Repair


class RepairRepository(BaseRepository[Repair]):
    def __init__(self) -> None:
        super().__init__(Repair)

    def get_by_id_and_tenant_id(self, db: Session, repair_id: int, tenant_id: int) -> Repair | None:
        stmt = select(Repair).where(
            Repair.id == repair_id,
            Repair.tenant_id == tenant_id,
        )
        return db.execute(stmt).scalar_one_or_none()

    def get_by_id_and_landlord_id(self, db: Session, repair_id: int, landlord_id: int) -> Repair | None:
        stmt = select(Repair).where(
            Repair.id == repair_id,
            Repair.landlord_id == landlord_id,
        )
        return db.execute(stmt).scalar_one_or_none()

    def get_by_id_visible_to_user(self, db: Session, repair_id: int, user_id: int) -> Repair | None:
        stmt = select(Repair).where(
            Repair.id == repair_id,
            or_(
                Repair.tenant_id == user_id,
                Repair.landlord_id == user_id,
            ),
        )
        return db.execute(stmt).scalar_one_or_none()

    def list_related_to_user(
        self,
        db: Session,
        user_id: int,
        offset: int,
        limit: int,
        status: str | None = None,
    ) -> list[Repair]:
        stmt = select(Repair).where(
            or_(
                Repair.tenant_id == user_id,
                Repair.landlord_id == user_id,
            )
        )
        if status is not None:
            stmt = stmt.where(Repair.status == status)
        stmt = (
            stmt.order_by(Repair.created_at.desc(), Repair.id.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(db.execute(stmt).scalars().all())

    def count_related_to_user(self, db: Session, user_id: int, status: str | None = None) -> int:
        stmt = select(func.count()).select_from(Repair).where(
            or_(
                Repair.tenant_id == user_id,
                Repair.landlord_id == user_id,
            )
        )
        if status is not None:
            stmt = stmt.where(Repair.status == status)
        return int(db.execute(stmt).scalar_one())

    def list_page_with_filters(
        self,
        db: Session,
        offset: int,
        limit: int,
        status: str | None = None,
    ) -> list[Repair]:
        stmt = select(Repair)
        if status is not None:
            stmt = stmt.where(Repair.status == status)
        stmt = stmt.order_by(Repair.created_at.desc(), Repair.id.desc()).offset(offset).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def count_all_with_filters(self, db: Session, status: str | None = None) -> int:
        stmt = select(func.count()).select_from(Repair)
        if status is not None:
            stmt = stmt.where(Repair.status == status)
        return int(db.execute(stmt).scalar_one())
