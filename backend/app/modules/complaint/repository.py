from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.common.base_repository import BaseRepository
from app.modules.complaint.model import Complaint


class ComplaintRepository(BaseRepository[Complaint]):
    def __init__(self) -> None:
        super().__init__(Complaint)

    def get_by_id_and_tenant_id(self, db: Session, complaint_id: int, tenant_id: int) -> Complaint | None:
        stmt = select(Complaint).where(
            Complaint.id == complaint_id,
            Complaint.tenant_id == tenant_id,
        )
        return db.execute(stmt).scalar_one_or_none()

    def get_by_id_and_landlord_id(self, db: Session, complaint_id: int, landlord_id: int) -> Complaint | None:
        stmt = select(Complaint).where(
            Complaint.id == complaint_id,
            Complaint.landlord_id == landlord_id,
        )
        return db.execute(stmt).scalar_one_or_none()

    def get_by_id_visible_to_user(self, db: Session, complaint_id: int, user_id: int) -> Complaint | None:
        stmt = select(Complaint).where(
            Complaint.id == complaint_id,
            or_(
                Complaint.tenant_id == user_id,
                Complaint.landlord_id == user_id,
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
    ) -> list[Complaint]:
        stmt = select(Complaint).where(
            or_(
                Complaint.tenant_id == user_id,
                Complaint.landlord_id == user_id,
            )
        )
        if status is not None:
            stmt = stmt.where(Complaint.status == status)
        stmt = (
            stmt.order_by(Complaint.created_at.desc(), Complaint.id.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(db.execute(stmt).scalars().all())

    def count_related_to_user(self, db: Session, user_id: int, status: str | None = None) -> int:
        stmt = select(func.count()).select_from(Complaint).where(
            or_(
                Complaint.tenant_id == user_id,
                Complaint.landlord_id == user_id,
            )
        )
        if status is not None:
            stmt = stmt.where(Complaint.status == status)
        return int(db.execute(stmt).scalar_one())

    def list_page_with_filters(
        self,
        db: Session,
        offset: int,
        limit: int,
        status: str | None = None,
    ) -> list[Complaint]:
        stmt = select(Complaint)
        if status is not None:
            stmt = stmt.where(Complaint.status == status)
        stmt = stmt.order_by(Complaint.created_at.desc(), Complaint.id.desc()).offset(offset).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def count_all_with_filters(self, db: Session, status: str | None = None) -> int:
        stmt = select(func.count()).select_from(Complaint)
        if status is not None:
            stmt = stmt.where(Complaint.status == status)
        return int(db.execute(stmt).scalar_one())
