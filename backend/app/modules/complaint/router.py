from __future__ import annotations

from flask import Blueprint, g, request

from app.common.dependencies import get_required_current_user_id
from app.container.services import get_complaint_service
from app.core.response import success
from app.modules.complaint.schema import ComplaintCreateSchema, ComplaintListQuerySchema


bp = Blueprint("complaint", __name__)


@bp.post("")
def create_complaint():
    current_user_id = get_required_current_user_id()
    data = ComplaintCreateSchema(**(request.get_json() or {}))
    service = get_complaint_service()
    result = service.create_complaint(
        g.db,
        current_user_id=current_user_id,
        contract_id=data.contract_id,
        description=data.description,
    )
    return success(data=result, status_code=201)


@bp.get("")
def list_complaints():
    current_user_id = get_required_current_user_id()
    query = ComplaintListQuerySchema(**request.args.to_dict())
    service = get_complaint_service()
    result = service.list_complaints(
        g.db,
        current_user_id=current_user_id,
        page=query.page,
        page_size=query.page_size,
        status=query.status,
    )
    return success(data=result)


@bp.get("/<int:complaint_id>")
def get_complaint_detail(complaint_id: int):
    current_user_id = get_required_current_user_id()
    service = get_complaint_service()
    result = service.get_complaint_detail(
        g.db,
        current_user_id=current_user_id,
        complaint_id=complaint_id,
    )
    return success(data=result)


@bp.patch("/<int:complaint_id>/process")
def process_complaint(complaint_id: int):
    current_user_id = get_required_current_user_id()
    service = get_complaint_service()
    result = service.process_complaint(g.db, current_user_id=current_user_id, complaint_id=complaint_id)
    return success(data=result)


@bp.patch("/<int:complaint_id>/resolve")
def resolve_complaint(complaint_id: int):
    current_user_id = get_required_current_user_id()
    service = get_complaint_service()
    result = service.resolve_complaint(g.db, current_user_id=current_user_id, complaint_id=complaint_id)
    return success(data=result)


@bp.patch("/<int:complaint_id>/reject")
def reject_complaint(complaint_id: int):
    current_user_id = get_required_current_user_id()
    service = get_complaint_service()
    result = service.reject_complaint(g.db, current_user_id=current_user_id, complaint_id=complaint_id)
    return success(data=result)


@bp.patch("/<int:complaint_id>/close")
def close_complaint(complaint_id: int):
    current_user_id = get_required_current_user_id()
    service = get_complaint_service()
    result = service.close_complaint(g.db, current_user_id=current_user_id, complaint_id=complaint_id)
    return success(data=result)
