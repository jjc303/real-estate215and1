from __future__ import annotations

from flask import Blueprint, g, request

from app.common.dependencies import get_required_current_user_id
from app.container.services import get_repair_service
from app.core.response import success
from app.modules.repair.schema import RepairCreateSchema, RepairListQuerySchema


bp = Blueprint("repair", __name__)


@bp.post("")
def create_repair():
    current_user_id = get_required_current_user_id()
    data = RepairCreateSchema(**(request.get_json() or {}))
    service = get_repair_service()
    result = service.create_repair(
        g.db,
        current_user_id=current_user_id,
        contract_id=data.contract_id,
        description=data.description,
    )
    return success(data=result, status_code=201)


@bp.get("")
def list_repairs():
    current_user_id = get_required_current_user_id()
    query = RepairListQuerySchema(**request.args.to_dict())
    service = get_repair_service()
    result = service.list_repairs(
        g.db,
        current_user_id=current_user_id,
        page=query.page,
        page_size=query.page_size,
        status=query.status,
    )
    return success(data=result)


@bp.get("/<int:repair_id>")
def get_repair_detail(repair_id: int):
    current_user_id = get_required_current_user_id()
    service = get_repair_service()
    result = service.get_repair_detail(g.db, current_user_id=current_user_id, repair_id=repair_id)
    return success(data=result)


@bp.patch("/<int:repair_id>/process")
def process_repair(repair_id: int):
    current_user_id = get_required_current_user_id()
    service = get_repair_service()
    result = service.process_repair(g.db, current_user_id=current_user_id, repair_id=repair_id)
    return success(data=result)


@bp.patch("/<int:repair_id>/complete")
def complete_repair(repair_id: int):
    current_user_id = get_required_current_user_id()
    service = get_repair_service()
    result = service.complete_repair(g.db, current_user_id=current_user_id, repair_id=repair_id)
    return success(data=result)


@bp.patch("/<int:repair_id>/reject")
def reject_repair(repair_id: int):
    current_user_id = get_required_current_user_id()
    service = get_repair_service()
    result = service.reject_repair(g.db, current_user_id=current_user_id, repair_id=repair_id)
    return success(data=result)


@bp.patch("/<int:repair_id>/close")
def close_repair(repair_id: int):
    current_user_id = get_required_current_user_id()
    service = get_repair_service()
    result = service.close_repair(g.db, current_user_id=current_user_id, repair_id=repair_id)
    return success(data=result)


@bp.patch("/<int:repair_id>/reopen")
def reopen_repair(repair_id: int):
    current_user_id = get_required_current_user_id()
    service = get_repair_service()
    result = service.reopen_repair(g.db, current_user_id=current_user_id, repair_id=repair_id)
    return success(data=result)
