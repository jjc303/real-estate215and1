from __future__ import annotations

from flask import Blueprint, g, request

from app.common.dependencies import get_required_current_user_id
from app.container.services import get_bill_service
from app.core.response import success
from app.modules.bill.schema import BillCreateSchema, BillListQuerySchema


bp = Blueprint("bill", __name__)


@bp.post("")
def create_bill():
    current_user_id = get_required_current_user_id()
    data = BillCreateSchema(**(request.get_json() or {}))
    service = get_bill_service()
    result = service.create_bill(
        g.db,
        current_user_id=current_user_id,
        contract_id=data.contract_id,
        bill_type=data.bill_type,
        amount=data.amount,
        due_date=data.due_date,
        remark=data.remark,
    )
    return success(data=result, status_code=201)


@bp.get("")
def list_bills():
    current_user_id = get_required_current_user_id()
    query = BillListQuerySchema(**request.args.to_dict())
    service = get_bill_service()
    result = service.list_bills(
        g.db,
        current_user_id=current_user_id,
        page=query.page,
        page_size=query.page_size,
    )
    return success(data=result)


@bp.get("/<int:bill_id>")
def get_bill_detail(bill_id: int):
    current_user_id = get_required_current_user_id()
    service = get_bill_service()
    result = service.get_bill_detail(g.db, current_user_id=current_user_id, bill_id=bill_id)
    return success(data=result)


@bp.patch("/<int:bill_id>/cancel")
def cancel_bill(bill_id: int):
    current_user_id = get_required_current_user_id()
    service = get_bill_service()
    result = service.cancel_bill(g.db, current_user_id=current_user_id, bill_id=bill_id)
    return success(data=result)


@bp.patch("/<int:bill_id>/mark-overdue")
def mark_bill_overdue(bill_id: int):
    current_user_id = get_required_current_user_id()
    service = get_bill_service()
    result = service.mark_bill_overdue(g.db, current_user_id=current_user_id, bill_id=bill_id)
    return success(data=result)


@bp.get("/landlord/summary")
def landlord_income_summary():
    current_user_id = get_required_current_user_id()
    service = get_bill_service()
    result = service.get_landlord_income_summary(g.db, landlord_id=current_user_id)
    return success(data=result)


@bp.post("/check-overdue")
def check_overdue():
    current_user_id = get_required_current_user_id()
    service = get_bill_service()
    count = service.check_overdue_bills(g.db)
    return success(data={"processed": count})
