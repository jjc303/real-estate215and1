from __future__ import annotations

from flask import Blueprint, g, request

from app.common.dependencies import get_required_current_user_id
from app.container.services import get_admin_service
from app.core.response import success
from app.modules.admin.schema import (
    ContractAdminListQuerySchema,
    ContractAdminStatusSchema,
    HouseAdminListQuerySchema,
    UserAdminCreateSchema,
    UserAdminListQuerySchema,
    UserAdminStatusSchema,
    UserAdminUpdateSchema,
)
from app.modules.complaint.schema import ComplaintListQuerySchema
from app.modules.repair.schema import RepairListQuerySchema


bp = Blueprint("admin", __name__)


@bp.get("/users")
def list_users():
    current_user_id = get_required_current_user_id()
    query = UserAdminListQuerySchema(**request.args.to_dict())
    service = get_admin_service()
    result = service.list_users(g.db, current_user_id=current_user_id, page=query.page, page_size=query.page_size)
    return success(data=result)


@bp.get("/users/<int:user_id>")
def get_user_detail(user_id: int):
    current_user_id = get_required_current_user_id()
    service = get_admin_service()
    result = service.get_user_detail(g.db, current_user_id=current_user_id, user_id=user_id)
    return success(data=result)


@bp.post("/users")
def create_user():
    current_user_id = get_required_current_user_id()
    data = UserAdminCreateSchema(**(request.get_json() or {}))
    service = get_admin_service()
    result = service.create_user(g.db, current_user_id=current_user_id, data=data)
    return success(data=result, status_code=201)


@bp.put("/users/<int:user_id>")
def update_user(user_id: int):
    current_user_id = get_required_current_user_id()
    data = UserAdminUpdateSchema(**(request.get_json() or {}))
    service = get_admin_service()
    result = service.update_user(g.db, current_user_id=current_user_id, user_id=user_id, data=data)
    return success(data=result)


@bp.patch("/users/<int:user_id>/status")
def update_user_status(user_id: int):
    current_user_id = get_required_current_user_id()
    data = UserAdminStatusSchema(**(request.get_json() or {}))
    service = get_admin_service()
    result = service.update_user_status(
        g.db,
        current_user_id=current_user_id,
        user_id=user_id,
        status=data.status,
    )
    return success(data=result)


@bp.get("/houses")
def list_houses():
    current_user_id = get_required_current_user_id()
    query = HouseAdminListQuerySchema(**request.args.to_dict())
    service = get_admin_service()
    result = service.list_houses(
        g.db,
        current_user_id=current_user_id,
        page=query.page,
        page_size=query.page_size,
        region=query.region,
        house_type=query.house_type,
        min_rent=query.min_rent,
        max_rent=query.max_rent,
        keyword=query.keyword,
        min_area=query.min_area,
        max_area=query.max_area,
    )
    return success(data=result)


@bp.get("/houses/<int:house_id>")
def get_house_detail(house_id: int):
    current_user_id = get_required_current_user_id()
    service = get_admin_service()
    result = service.get_house_detail(g.db, current_user_id=current_user_id, house_id=house_id)
    return success(data=result)


@bp.get("/complaints")
def list_complaints():
    current_user_id = get_required_current_user_id()
    query = ComplaintListQuerySchema(**request.args.to_dict())
    service = get_admin_service()
    result = service.list_complaints(
        g.db,
        current_user_id=current_user_id,
        page=query.page,
        page_size=query.page_size,
        status=query.status,
    )
    return success(data=result)


@bp.get("/complaints/<int:complaint_id>")
def get_complaint_detail(complaint_id: int):
    current_user_id = get_required_current_user_id()
    service = get_admin_service()
    result = service.get_complaint_detail(
        g.db,
        current_user_id=current_user_id,
        complaint_id=complaint_id,
    )
    return success(data=result)


@bp.patch("/complaints/<int:complaint_id>/process")
def process_complaint(complaint_id: int):
    current_user_id = get_required_current_user_id()
    service = get_admin_service()
    result = service.process_complaint(g.db, current_user_id=current_user_id, complaint_id=complaint_id)
    return success(data=result)


@bp.patch("/complaints/<int:complaint_id>/resolve")
def resolve_complaint(complaint_id: int):
    current_user_id = get_required_current_user_id()
    service = get_admin_service()
    result = service.resolve_complaint(g.db, current_user_id=current_user_id, complaint_id=complaint_id)
    return success(data=result)


@bp.patch("/complaints/<int:complaint_id>/reject")
def reject_complaint(complaint_id: int):
    current_user_id = get_required_current_user_id()
    service = get_admin_service()
    result = service.reject_complaint(g.db, current_user_id=current_user_id, complaint_id=complaint_id)
    return success(data=result)


@bp.patch("/complaints/<int:complaint_id>/close")
def close_complaint(complaint_id: int):
    current_user_id = get_required_current_user_id()
    service = get_admin_service()
    result = service.close_complaint(g.db, current_user_id=current_user_id, complaint_id=complaint_id)
    return success(data=result)


@bp.get("/repairs")
def list_repairs():
    current_user_id = get_required_current_user_id()
    query = RepairListQuerySchema(**request.args.to_dict())
    service = get_admin_service()
    result = service.list_repairs(
        g.db,
        current_user_id=current_user_id,
        page=query.page,
        page_size=query.page_size,
        status=query.status,
    )
    return success(data=result)


@bp.get("/repairs/<int:repair_id>")
def get_repair_detail(repair_id: int):
    current_user_id = get_required_current_user_id()
    service = get_admin_service()
    result = service.get_repair_detail(g.db, current_user_id=current_user_id, repair_id=repair_id)
    return success(data=result)


@bp.patch("/repairs/<int:repair_id>/process")
def process_repair(repair_id: int):
    current_user_id = get_required_current_user_id()
    service = get_admin_service()
    result = service.process_repair(g.db, current_user_id=current_user_id, repair_id=repair_id)
    return success(data=result)


@bp.patch("/repairs/<int:repair_id>/complete")
def complete_repair(repair_id: int):
    current_user_id = get_required_current_user_id()
    service = get_admin_service()
    result = service.complete_repair(g.db, current_user_id=current_user_id, repair_id=repair_id)
    return success(data=result)


@bp.patch("/repairs/<int:repair_id>/reject")
def reject_repair(repair_id: int):
    current_user_id = get_required_current_user_id()
    service = get_admin_service()
    result = service.reject_repair(g.db, current_user_id=current_user_id, repair_id=repair_id)
    return success(data=result)


@bp.patch("/repairs/<int:repair_id>/close")
def close_repair(repair_id: int):
    current_user_id = get_required_current_user_id()
    service = get_admin_service()
    result = service.close_repair(g.db, current_user_id=current_user_id, repair_id=repair_id)
    return success(data=result)


@bp.get("/contracts")
def list_contracts():
    current_user_id = get_required_current_user_id()
    query = ContractAdminListQuerySchema(**request.args.to_dict())
    service = get_admin_service()
    result = service.list_contracts(g.db, current_user_id=current_user_id, page=query.page, page_size=query.page_size)
    return success(data=result)


@bp.get("/contracts/<int:contract_id>")
def get_contract_detail(contract_id: int):
    current_user_id = get_required_current_user_id()
    service = get_admin_service()
    result = service.get_contract_detail(g.db, current_user_id=current_user_id, contract_id=contract_id)
    return success(data=result)


@bp.patch("/contracts/<int:contract_id>/status")
def update_contract_status(contract_id: int):
    current_user_id = get_required_current_user_id()
    data = ContractAdminStatusSchema(**(request.get_json() or {}))
    service = get_admin_service()
    result = service.update_contract_status(
        g.db,
        current_user_id=current_user_id,
        contract_id=contract_id,
        status=data.status,
    )
    return success(data=result)
