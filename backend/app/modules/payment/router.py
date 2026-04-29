from __future__ import annotations

from flask import Blueprint, g, request

from app.common.dependencies import get_required_current_user_id
from app.container.services import get_payment_service
from app.core.response import success
from app.modules.payment.schema import PaymentCreateSchema, PaymentListQuerySchema


bp = Blueprint("payment", __name__)


@bp.post("")
def create_payment():
    current_user_id = get_required_current_user_id()
    data = PaymentCreateSchema(**(request.get_json() or {}))
    service = get_payment_service()
    result = service.create_payment(
        g.db,
        current_user_id=current_user_id,
        bill_id=data.bill_id,
        amount=data.amount,
        payment_method=data.payment_method,
        remark=data.remark,
    )
    return success(data=result, status_code=201)


@bp.get("")
def list_payments():
    current_user_id = get_required_current_user_id()
    query = PaymentListQuerySchema(**request.args.to_dict())
    service = get_payment_service()
    result = service.list_payments(
        g.db,
        current_user_id=current_user_id,
        page=query.page,
        page_size=query.page_size,
    )
    return success(data=result)


@bp.get("/<int:payment_id>")
def get_payment_detail(payment_id: int):
    current_user_id = get_required_current_user_id()
    service = get_payment_service()
    result = service.get_payment_detail(
        g.db,
        current_user_id=current_user_id,
        payment_id=payment_id,
    )
    return success(data=result)
