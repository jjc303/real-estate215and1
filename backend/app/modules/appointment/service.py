from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.common.enums import AppointmentStatus, HouseStatus
from app.common.pagination import build_page_result, get_offset
from app.core.exceptions import (
    AppointmentNotFoundException,
    AppointmentTimeInvalidException,
    HouseNotFoundException,
    InvalidAppointmentStatusException,
    OwnHouseAppointmentForbiddenException,
)
from app.modules.appointment.model import Appointment
from app.modules.appointment.repository import AppointmentRepository
from app.modules.appointment.schema import (
    AppointmentHouseSummarySchema,
    AppointmentReadSchema,
)
from app.modules.house.model import House
from app.modules.house.repository import HouseRepository


class AppointmentService:
    def __init__(
        self,
        appointment_repository: AppointmentRepository,
        house_repository: HouseRepository,
    ) -> None:
        self.appointment_repository = appointment_repository
        self.house_repository = house_repository

    def create_appointment(
        self,
        db: Session,
        current_user_id: int,
        house_id: int,
        appointment_time: datetime,
        remark: str | None = None,
    ) -> dict[str, object]:
        house = self._get_available_house(db, house_id)
        if house.landlord_id == current_user_id:
            raise OwnHouseAppointmentForbiddenException()

        appointment_time = self._normalize_appointment_time(appointment_time)
        if appointment_time <= self._now():
            raise AppointmentTimeInvalidException()

        appointment = Appointment(
            house_id=house.id,
            tenant_id=current_user_id,
            landlord_id=house.landlord_id,
            appointment_time=appointment_time,
            remark=remark,
            status=AppointmentStatus.PENDING,
        )

        try:
            self.appointment_repository.create(db, appointment)
            db.commit()
            db.refresh(appointment)
        except Exception:
            db.rollback()
            raise

        return self._serialize(appointment, house, current_user_id)

    def list_appointments(self, db: Session, current_user_id: int, page: int, page_size: int) -> dict[str, object]:
        offset = get_offset(page, page_size)
        rows = self.appointment_repository.list_related_to_user(
            db,
            user_id=current_user_id,
            offset=offset,
            limit=page_size,
        )
        total = self.appointment_repository.count_related_to_user(db, current_user_id)
        return build_page_result(
            items=[self._serialize(appointment, house, current_user_id) for appointment, house in rows],
            total=total,
            page=page,
            page_size=page_size,
        )

    def confirm_appointment(self, db: Session, current_user_id: int, appointment_id: int) -> dict[str, object]:
        appointment = self.appointment_repository.get_by_id_and_landlord_id(db, appointment_id, current_user_id)
        if appointment is None:
            raise AppointmentNotFoundException()

        self._ensure_pending_and_not_expired(appointment)
        appointment.status = AppointmentStatus.CONFIRMED

        try:
            db.commit()
            db.refresh(appointment)
        except Exception:
            db.rollback()
            raise

        house = self._get_house_or_not_found(db, appointment.house_id)
        return self._serialize(appointment, house, current_user_id)

    def reject_appointment(self, db: Session, current_user_id: int, appointment_id: int) -> dict[str, object]:
        appointment = self.appointment_repository.get_by_id_and_landlord_id(db, appointment_id, current_user_id)
        if appointment is None:
            raise AppointmentNotFoundException()

        self._ensure_pending_and_not_expired(appointment)
        appointment.status = AppointmentStatus.REJECTED

        try:
            db.commit()
            db.refresh(appointment)
        except Exception:
            db.rollback()
            raise

        house = self._get_house_or_not_found(db, appointment.house_id)
        return self._serialize(appointment, house, current_user_id)

    def cancel_appointment(self, db: Session, current_user_id: int, appointment_id: int) -> dict[str, object]:
        appointment = self.appointment_repository.get_by_id_and_tenant_id(db, appointment_id, current_user_id)
        if appointment is None:
            raise AppointmentNotFoundException()

        if self._display_status(appointment) == AppointmentStatus.EXPIRED:
            raise InvalidAppointmentStatusException()
        if appointment.status not in {AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED}:
            raise InvalidAppointmentStatusException()

        appointment.status = AppointmentStatus.CANCELLED

        try:
            db.commit()
            db.refresh(appointment)
        except Exception:
            db.rollback()
            raise

        house = self._get_house_or_not_found(db, appointment.house_id)
        return self._serialize(appointment, house, current_user_id)

    def _ensure_pending_and_not_expired(self, appointment: Appointment) -> None:
        if appointment.status != AppointmentStatus.PENDING:
            raise InvalidAppointmentStatusException()
        if self._display_status(appointment) == AppointmentStatus.EXPIRED:
            raise InvalidAppointmentStatusException()

    def _get_available_house(self, db: Session, house_id: int) -> House:
        house = self.house_repository.get_by_id(db, house_id)
        if house is None or house.deleted_at is not None or house.status != HouseStatus.LISTED:
            raise HouseNotFoundException()
        return house

    def _get_house_or_not_found(self, db: Session, house_id: int) -> House:
        house = self.house_repository.get_by_id(db, house_id)
        if house is None:
            raise HouseNotFoundException()
        return house

    def _normalize_appointment_time(self, appointment_time: datetime) -> datetime:
        local_tz = datetime.now().astimezone().tzinfo
        if appointment_time.tzinfo is None:
            return appointment_time.replace(tzinfo=local_tz)
        return appointment_time.astimezone(local_tz)

    def _now(self) -> datetime:
        return datetime.now().astimezone()

    def _display_status(self, appointment: Appointment) -> str:
        appointment_time = self._normalize_appointment_time(appointment.appointment_time)
        if appointment.status == AppointmentStatus.PENDING and appointment_time < self._now():
            return AppointmentStatus.EXPIRED
        return appointment.status

    def _relation_role(self, appointment: Appointment, current_user_id: int) -> str:
        if appointment.tenant_id == current_user_id:
            return "tenant"
        return "landlord"

    def _serialize(self, appointment: Appointment, house: House, current_user_id: int) -> dict[str, object]:
        house_data = AppointmentHouseSummarySchema.model_validate(house)
        return AppointmentReadSchema(
            id=appointment.id,
            house_id=appointment.house_id,
            tenant_id=appointment.tenant_id,
            landlord_id=appointment.landlord_id,
            appointment_time=self._normalize_appointment_time(appointment.appointment_time),
            remark=appointment.remark,
            status=appointment.status,
            display_status=self._display_status(appointment),
            created_at=appointment.created_at,
            updated_at=appointment.updated_at,
            relation_role=self._relation_role(appointment, current_user_id),
            house=house_data,
        ).model_dump(mode="json")
