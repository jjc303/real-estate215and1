from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.common.enums import BillStatus, PaymentStatus
from app.common.pagination import build_page_result, get_offset
from app.core.exceptions import (
    BillAlreadyPaidException,
    BillNotFoundException,
    BillNotPayableException,
    PaymentAmountMismatchException,
    PaymentNotFoundException,
)
from app.modules.bill.repository import BillRepository
from app.modules.payment.model import Payment
from app.modules.payment.repository import PaymentRepository
from app.modules.payment.schema import PaymentReadSchema


class PaymentService:
    def __init__(
        self,
        payment_repository: PaymentRepository,
        bill_repository: BillRepository,
    ) -> None:
        self.payment_repository = payment_repository
        self.bill_repository = bill_repository

    def create_payment(
        self,
        db: Session,
        current_user_id: int,
        bill_id: int,
        amount: Decimal,
        payment_method: str,
        remark: str | None = None,
    ) -> dict[str, object]:
        bill = self.bill_repository.get_by_id(db, bill_id)
        if bill is None or bill.tenant_id != current_user_id:
            raise BillNotFoundException()
        if bill.status == BillStatus.PAID:
            raise BillAlreadyPaidException()
        if bill.status not in {BillStatus.UNPAID, BillStatus.OVERDUE}:
            raise BillNotPayableException()
        if amount != bill.amount:
            raise PaymentAmountMismatchException()

        payment = Payment(
            bill_id=bill.id,
            contract_id=bill.contract_id,
            house_id=bill.house_id,
            tenant_id=bill.tenant_id,
            landlord_id=bill.landlord_id,
            amount=bill.amount,
            payment_method=payment_method,
            status=PaymentStatus.SUCCESS,
            paid_at=datetime.now(),
            remark=remark,
        )

        try:
            self.payment_repository.create(db, payment)
            db.flush()
            bill.status = BillStatus.PAID
            db.commit()
            db.refresh(payment)
        except IntegrityError as exc:
            db.rollback()
            raise BillAlreadyPaidException() from exc
        except Exception:
            db.rollback()
            raise

        return self._serialize(payment)

    def list_payments(
        self,
        db: Session,
        current_user_id: int,
        page: int,
        page_size: int,
    ) -> dict[str, object]:
        offset = get_offset(page, page_size)
        payments = self.payment_repository.list_related_to_user(
            db,
            user_id=current_user_id,
            offset=offset,
            limit=page_size,
        )
        total = self.payment_repository.count_related_to_user(db, current_user_id)
        return build_page_result(
            items=[self._serialize(payment) for payment in payments],
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_payment_detail(
        self,
        db: Session,
        current_user_id: int,
        payment_id: int,
    ) -> dict[str, object]:
        payment = self.payment_repository.get_by_id_and_user_id(db, payment_id, current_user_id)
        if payment is None:
            raise PaymentNotFoundException()
        return self._serialize(payment)

    def _serialize(self, payment: Payment) -> dict[str, object]:
        return PaymentReadSchema.model_validate(payment).model_dump(mode="json")
