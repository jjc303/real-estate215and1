from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.common.base_repository import BaseRepository
from app.modules.appointment.model import Appointment
from app.modules.house.model import House


class AppointmentRepository(BaseRepository[Appointment]):
    def __init__(self) -> None:
        super().__init__(Appointment)

    def get_by_id_and_landlord_id(
        self,
        db: Session,
        appointment_id: int,
        landlord_id: int,
    ) -> Appointment | None:
        stmt = select(Appointment).where(
            Appointment.id == appointment_id,
            Appointment.landlord_id == landlord_id,
        )
        return db.execute(stmt).scalar_one_or_none()

    def get_by_id_and_tenant_id(
        self,
        db: Session,
        appointment_id: int,
        tenant_id: int,
    ) -> Appointment | None:
        stmt = select(Appointment).where(
            Appointment.id == appointment_id,
            Appointment.tenant_id == tenant_id,
        )
        return db.execute(stmt).scalar_one_or_none()

    def list_related_to_user(
        self,
        db: Session,
        user_id: int,
        offset: int,
        limit: int,
    ) -> list[tuple[Appointment, House]]:
        stmt = (
            select(Appointment, House)
            .join(House, House.id == Appointment.house_id)
            .where(
                or_(
                    Appointment.tenant_id == user_id,
                    Appointment.landlord_id == user_id,
                )
            )
            .order_by(Appointment.created_at.desc(), Appointment.id.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(db.execute(stmt).all())

    def count_related_to_user(self, db: Session, user_id: int) -> int:
        stmt = select(func.count()).select_from(Appointment).where(
            or_(
                Appointment.tenant_id == user_id,
                Appointment.landlord_id == user_id,
            )
        )
        return int(db.execute(stmt).scalar_one())
