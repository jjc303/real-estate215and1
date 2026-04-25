from __future__ import annotations

from flask import Blueprint, g, request

from app.common.dependencies import get_required_current_user_id
from app.container.services import get_appointment_service
from app.core.response import success
from app.modules.appointment.schema import AppointmentCreateSchema, AppointmentListQuerySchema


bp = Blueprint("appointment", __name__)


@bp.post("")
def create_appointment():
    current_user_id = get_required_current_user_id()
    data = AppointmentCreateSchema(**(request.get_json() or {}))
    service = get_appointment_service()
    result = service.create_appointment(
        g.db,
        current_user_id=current_user_id,
        house_id=data.house_id,
        appointment_time=data.appointment_time,
        remark=data.remark,
    )
    return success(data=result, status_code=201)


@bp.get("")
def list_appointments():
    current_user_id = get_required_current_user_id()
    query = AppointmentListQuerySchema(**request.args.to_dict())
    service = get_appointment_service()
    result = service.list_appointments(
        g.db,
        current_user_id=current_user_id,
        page=query.page,
        page_size=query.page_size,
    )
    return success(data=result)


@bp.patch("/<int:appointment_id>/confirm")
def confirm_appointment(appointment_id: int):
    current_user_id = get_required_current_user_id()
    service = get_appointment_service()
    result = service.confirm_appointment(g.db, current_user_id=current_user_id, appointment_id=appointment_id)
    return success(data=result)


@bp.patch("/<int:appointment_id>/reject")
def reject_appointment(appointment_id: int):
    current_user_id = get_required_current_user_id()
    service = get_appointment_service()
    result = service.reject_appointment(g.db, current_user_id=current_user_id, appointment_id=appointment_id)
    return success(data=result)


@bp.patch("/<int:appointment_id>/cancel")
def cancel_appointment(appointment_id: int):
    current_user_id = get_required_current_user_id()
    service = get_appointment_service()
    result = service.cancel_appointment(g.db, current_user_id=current_user_id, appointment_id=appointment_id)
    return success(data=result)
