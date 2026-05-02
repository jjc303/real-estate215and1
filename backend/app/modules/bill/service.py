from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.common.enums import BillStatus, ContractStatus
from app.common.pagination import build_page_result, get_offset
from app.core.exceptions import (
    BillNotFoundException,
    ConflictException,
    ContractNotActiveForBillException,
    ContractNotFoundException,
    InvalidBillStatusException,
)
from app.modules.bill.model import Bill
from app.modules.bill.repository import BillRepository
from app.modules.bill.schema import BillReadSchema
from app.modules.contract.repository import ContractRepository
from app.modules.notification.service import NotificationService


class BillService:
    def __init__(
        self,
        bill_repository: BillRepository,
        contract_repository: ContractRepository,
        notification_service: NotificationService,
    ) -> None:
        self.bill_repository = bill_repository
        self.contract_repository = contract_repository
        self.notification_service = notification_service

    def create_bill(
        self,
        db: Session,
        current_user_id: int,
        contract_id: int,
        bill_type: str,
        amount: Decimal,
        due_date: date,
        remark: str | None = None,
    ) -> dict[str, object]:
        contract = self.contract_repository.get_by_id_and_landlord_id(db, contract_id, current_user_id)
        if contract is None:
            raise ContractNotFoundException()
        if contract.status != ContractStatus.ACTIVE:
            raise ContractNotActiveForBillException()

        bill = Bill(
            contract_id=contract.id,
            house_id=contract.house_id,
            tenant_id=contract.tenant_id,
            landlord_id=contract.landlord_id,
            bill_type=bill_type,
            amount=amount,
            due_date=due_date,
            status=BillStatus.UNPAID,
            remark=remark,
        )

        try:
            self.bill_repository.create(db, bill)
            db.flush()
            self._notify_tenant(
                db,
                bill,
                title="New bill created",
                message=f"Bill #{bill.id} has been created for your contract.",
            )
            db.commit()
            db.refresh(bill)
        except IntegrityError as exc:
            db.rollback()
            raise ConflictException(message="resource conflict") from exc
        except Exception:
            db.rollback()
            raise

        return self._serialize(bill)

    def list_bills(
        self,
        db: Session,
        current_user_id: int,
        page: int,
        page_size: int,
    ) -> dict[str, object]:
        offset = get_offset(page, page_size)
        bills = self.bill_repository.list_related_to_user(
            db,
            user_id=current_user_id,
            offset=offset,
            limit=page_size,
        )
        total = self.bill_repository.count_related_to_user(db, current_user_id)
        return build_page_result(
            items=[self._serialize(bill) for bill in bills],
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_bill_detail(
        self,
        db: Session,
        current_user_id: int,
        bill_id: int,
    ) -> dict[str, object]:
        bill = self.bill_repository.get_by_id_and_user_id(db, bill_id, current_user_id)
        if bill is None:
            raise BillNotFoundException()
        return self._serialize(bill)

    def cancel_bill(
        self,
        db: Session,
        current_user_id: int,
        bill_id: int,
    ) -> dict[str, object]:
        bill = self.bill_repository.get_by_id_and_landlord_id(db, bill_id, current_user_id)
        if bill is None:
            raise BillNotFoundException()
        if bill.status not in {BillStatus.UNPAID, BillStatus.OVERDUE}:
            raise InvalidBillStatusException()

        bill.status = BillStatus.CANCELLED
        try:
            self._notify_tenant(
                db,
                bill,
                title="Bill cancelled",
                message=f"Bill #{bill.id} has been cancelled by the landlord.",
            )
            db.commit()
            db.refresh(bill)
        except Exception:
            db.rollback()
            raise

        return self._serialize(bill)

    def mark_bill_overdue(
        self,
        db: Session,
        current_user_id: int,
        bill_id: int,
    ) -> dict[str, object]:
        bill = self.bill_repository.get_by_id_and_landlord_id(db, bill_id, current_user_id)
        if bill is None:
            raise BillNotFoundException()
        if bill.status != BillStatus.UNPAID:
            raise InvalidBillStatusException()
        if date.today() <= bill.due_date:
            raise InvalidBillStatusException()

        bill.status = BillStatus.OVERDUE
        try:
            self._notify_tenant(
                db,
                bill,
                title="Bill overdue",
                message=f"Bill #{bill.id} is now overdue.",
            )
            db.commit()
            db.refresh(bill)
        except Exception:
            db.rollback()
            raise

        return self._serialize(bill)

    def _serialize(self, bill: Bill) -> dict[str, object]:
        return BillReadSchema.model_validate(bill).model_dump(mode="json")

    def _notify_tenant(self, db: Session, bill: Bill, *, title: str, message: str) -> None:
        self.notification_service.create_notification(
            db,
            user_id=bill.tenant_id,
            source_type="bill",
            source_id=bill.id,
            title=title,
            message=message,
            auto_commit=False,
        )
