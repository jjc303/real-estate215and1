from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.common.enums import BillStatus, ContractStatus
from app.common.enums import OperationLogModule
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
from app.modules.bill.schema import BillReadSchema, LandlordIncomeSummarySchema, MonthlyIncomeItem
from app.modules.contract.repository import ContractRepository
from app.modules.house.model import House
from app.modules.notification.service import NotificationService
from app.modules.operation_log.service import OperationLogService

from app.common.pdf_generator import build_bill_pdf


class BillService:
    def __init__(
        self,
        bill_repository: BillRepository,
        contract_repository: ContractRepository,
        notification_service: NotificationService,
        operation_log_service: OperationLogService,
    ) -> None:
        self.bill_repository = bill_repository
        self.contract_repository = contract_repository
        self.notification_service = notification_service
        self.operation_log_service = operation_log_service

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
            self.operation_log_service.log_action(
                db,
                current_user_id=current_user_id,
                module=OperationLogModule.BILL,
                record_id=bill.id,
                action="create",
                before_status=None,
                after_status=bill.status,
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

        before_status = bill.status
        bill.status = BillStatus.CANCELLED
        try:
            self._notify_tenant(
                db,
                bill,
                title="Bill cancelled",
                message=f"Bill #{bill.id} has been cancelled by the landlord.",
            )
            self.operation_log_service.log_action(
                db,
                current_user_id=current_user_id,
                module=OperationLogModule.BILL,
                record_id=bill.id,
                action="cancel",
                before_status=before_status,
                after_status=bill.status,
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

        before_status = bill.status
        bill.status = BillStatus.OVERDUE
        try:
            self._notify_tenant(
                db,
                bill,
                title="Bill overdue",
                message=f"Bill #{bill.id} is now overdue.",
            )
            self.operation_log_service.log_action(
                db,
                current_user_id=current_user_id,
                module=OperationLogModule.BILL,
                record_id=bill.id,
                action="mark_overdue",
                before_status=before_status,
                after_status=bill.status,
            )
            db.commit()
            db.refresh(bill)
        except Exception:
            db.rollback()
            raise

        return self._serialize(bill)

    def get_landlord_income_summary(
        self,
        db: Session,
        landlord_id: int,
    ) -> dict[str, object]:
        total_income = self.bill_repository.sum_paid_by_landlord(db, landlord_id)
        pending_amount = self.bill_repository.sum_unpaid_by_landlord(db, landlord_id)
        overdue_amount = self.bill_repository.sum_overdue_by_landlord(db, landlord_id)
        count_by_status = self.bill_repository.count_by_status(db, landlord_id)
        monthly = self.bill_repository.list_monthly_income_by_landlord(db, landlord_id)

        return LandlordIncomeSummarySchema(
            total_income=total_income,
            pending_amount=pending_amount,
            overdue_amount=overdue_amount,
            unpaid_count=count_by_status.get("unpaid", 0),
            monthly_income=[
                MonthlyIncomeItem(month=m, amount=a) for m, a in monthly
            ],
        ).model_dump(mode="json")

    def check_overdue_bills(self, db: Session, landlord_id: int | None = None) -> int:
        overdue_bills = self.bill_repository.list_overdue_unpaid(db, landlord_id=landlord_id)
        now = date.today()
        for bill in overdue_bills:
            if bill.due_date >= now:
                continue
            bill.status = BillStatus.OVERDUE
            self._notify_tenant(
                db,
                bill,
                title="账单逾期",
                message=f"账单 #{bill.id} 已逾期，请尽快支付 ¥{bill.amount}。",
            )
            self.notification_service.create_notification(
                db,
                user_ids=[bill.landlord_id],
                source_type="bill",
                source_id=bill.id,
                title="租客逾期提醒",
                message=f"租客 #{bill.tenant_id} 的账单 #{bill.id} 已逾期，金额 ¥{bill.amount}。",
                auto_commit=False,
            )
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
        return len(overdue_bills)

    def download_bill(self, db: Session, current_user_id: int, bill_id: int) -> bytes:
        bill = self.bill_repository.get_by_id_and_user_id(db, bill_id, current_user_id)
        if bill is None:
            raise BillNotFoundException()

        house = db.get(House, bill.house_id)
        bill_type_label = {"rent": "租金", "deposit": "押金", "other": "其他"}.get(bill.bill_type, bill.bill_type)

        return build_bill_pdf(
            bill.id,
            house_title=house.title if house else "—",
            bill_type=bill_type_label,
            amount=bill.amount,
            due_date=bill.due_date,
            status=bill.status,
            created_at=str(bill.created_at) if bill.created_at else "—",
        )

    def _serialize(self, bill: Bill) -> dict[str, object]:
        return BillReadSchema.model_validate(bill).model_dump(mode="json")

    def _notify_tenant(self, db: Session, bill: Bill, *, title: str, message: str) -> None:
        self.notification_service.create_notification(
            db,
            user_ids=[bill.tenant_id],
            source_type="bill",
            source_id=bill.id,
            title=title,
            message=message,
            auto_commit=False,
        )
