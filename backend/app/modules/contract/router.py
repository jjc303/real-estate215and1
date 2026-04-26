from __future__ import annotations

from flask import Blueprint, g, request

from app.common.dependencies import get_required_current_user_id
from app.container.services import get_contract_service
from app.core.response import success
from app.modules.contract.schema import ContractCreateSchema, ContractListQuerySchema


bp = Blueprint("contract", __name__)


@bp.post("")
def create_contract():
    current_user_id = get_required_current_user_id()
    data = ContractCreateSchema(**(request.get_json() or {}))
    service = get_contract_service()
    result = service.create_contract(
        g.db,
        current_user_id=current_user_id,
        appointment_id=data.appointment_id,
        start_date=data.start_date,
        end_date=data.end_date,
        monthly_rent=data.monthly_rent,
        deposit=data.deposit,
        remark=data.remark,
    )
    return success(data=result, status_code=201)


@bp.get("")
def list_contracts():
    current_user_id = get_required_current_user_id()
    query = ContractListQuerySchema(**request.args.to_dict())
    service = get_contract_service()
    result = service.list_contracts(
        g.db,
        current_user_id=current_user_id,
        page=query.page,
        page_size=query.page_size,
    )
    return success(data=result)


@bp.get("/<int:contract_id>")
def get_contract_detail(contract_id: int):
    current_user_id = get_required_current_user_id()
    service = get_contract_service()
    result = service.get_contract_detail(g.db, current_user_id=current_user_id, contract_id=contract_id)
    return success(data=result)


@bp.patch("/<int:contract_id>/confirm")
def confirm_contract(contract_id: int):
    current_user_id = get_required_current_user_id()
    service = get_contract_service()
    result = service.confirm_contract(g.db, current_user_id=current_user_id, contract_id=contract_id)
    return success(data=result)


@bp.patch("/<int:contract_id>/reject")
def reject_contract(contract_id: int):
    current_user_id = get_required_current_user_id()
    service = get_contract_service()
    result = service.reject_contract(g.db, current_user_id=current_user_id, contract_id=contract_id)
    return success(data=result)


@bp.patch("/<int:contract_id>/cancel")
def cancel_contract(contract_id: int):
    current_user_id = get_required_current_user_id()
    service = get_contract_service()
    result = service.cancel_contract(g.db, current_user_id=current_user_id, contract_id=contract_id)
    return success(data=result)


@bp.patch("/<int:contract_id>/terminate")
def terminate_contract(contract_id: int):
    current_user_id = get_required_current_user_id()
    service = get_contract_service()
    result = service.terminate_contract(g.db, current_user_id=current_user_id, contract_id=contract_id)
    return success(data=result)
