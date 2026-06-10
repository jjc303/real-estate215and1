from __future__ import annotations

from datetime import date, datetime

from sqlalchemy.orm import Session

from app.common.enums import ComplaintStatus, ContractStatus
from app.common.enums import OperationLogModule
from app.common.pagination import build_page_result, get_offset
from app.core.exceptions import (
    ComplaintNotFoundException,
    ContractNotActiveForComplaintException,
    ContractNotFoundException,
    ForbiddenException,
    InvalidComplaintStatusException,
    UnauthorizedException,
)
from app.modules.complaint.model import Complaint
from app.modules.complaint.repository import ComplaintRepository
from app.modules.complaint.schema import ComplaintReadSchema
from app.modules.contract.repository import ContractRepository
from app.modules.notification.service import NotificationService
from app.modules.operation_log.service import OperationLogService
from app.modules.user.model import User
from app.modules.user.repository import UserRepository


class ComplaintService:
    def __init__(
        self,
        complaint_repository: ComplaintRepository,
        contract_repository: ContractRepository,
        user_repository: UserRepository,
        notification_service: NotificationService,
        operation_log_service: OperationLogService,
    ) -> None:
        self.complaint_repository = complaint_repository
        self.contract_repository = contract_repository
        self.user_repository = user_repository
        self.notification_service = notification_service
        self.operation_log_service = operation_log_service

    def create_complaint(
        self,
        db: Session,
        current_user_id: int,
        contract_id: int,
        description: str,
    ) -> dict[str, object]:
        user = self._get_current_user(db, current_user_id)
        self._require_role(user, {"tenant"})

        contract = self.contract_repository.get_by_id_and_tenant_id(db, contract_id, current_user_id)
        if contract is None:
            raise ContractNotFoundException()
        if contract.status != ContractStatus.ACTIVE:
            raise ContractNotActiveForComplaintException()

        complaint = Complaint(
            contract_id=contract.id,
            house_id=contract.house_id,
            tenant_id=contract.tenant_id,
            landlord_id=contract.landlord_id,
            description=description,
            status=ComplaintStatus.PENDING,
        )

        try:
            self.complaint_repository.create(db, complaint)
            db.flush()
            self._notify_landlord(
                db,
                complaint,
                title="New complaint submitted",
                message=f"Complaint #{complaint.id} has been submitted by the tenant.",
            )
            self.operation_log_service.log_action(
                db,
                current_user_id=current_user_id,
                module=OperationLogModule.COMPLAINT,
                record_id=complaint.id,
                action="create",
                before_status=None,
                after_status=complaint.status,
            )
            db.commit()
            db.refresh(complaint)
        except Exception:
            db.rollback()
            raise

        return self._serialize(complaint)

    def list_complaints(
        self,
        db: Session,
        current_user_id: int,
        page: int,
        page_size: int,
        status: str | None = None,
        keyword: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> dict[str, object]:
        user = self._get_current_user(db, current_user_id)
        offset = get_offset(page, page_size)

        if user.role == "admin":
            complaints = self.complaint_repository.list_page_with_filters(
                db,
                offset=offset,
                limit=page_size,
                status=status,
                keyword=keyword,
                date_from=date_from,
                date_to=date_to,
            )
            total = self.complaint_repository.count_all_with_filters(
                db, status=status, keyword=keyword, date_from=date_from, date_to=date_to,
            )
        else:
            complaints = self.complaint_repository.list_related_to_user(
                db,
                user_id=current_user_id,
                offset=offset,
                limit=page_size,
                status=status,
            )
            total = self.complaint_repository.count_related_to_user(db, current_user_id, status=status)

        return build_page_result(
            items=[self._serialize(complaint) for complaint in complaints],
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_complaint_detail(
        self,
        db: Session,
        current_user_id: int,
        complaint_id: int,
    ) -> dict[str, object]:
        complaint = self._get_visible_complaint(db, current_user_id, complaint_id)
        return self._serialize(complaint)

    def process_complaint(self, db: Session, current_user_id: int, complaint_id: int) -> dict[str, object]:
        user = self._get_current_user(db, current_user_id)
        self._require_role(user, {"landlord", "admin"})
        complaint = self._get_operable_complaint(db, user, complaint_id)
        self._ensure_status(complaint, {ComplaintStatus.PENDING})
        before_status = complaint.status
        complaint.status = ComplaintStatus.PROCESSING
        complaint.processed_at = self._now()
        self._notify_tenant(
            db,
            complaint,
            title="Complaint is being processed",
            message=f"Complaint #{complaint.id} is now processing.",
        )
        self._log_status_change(db, current_user_id, complaint.id, "process", before_status, complaint.status)
        return self._commit_and_serialize(db, complaint)

    def resolve_complaint(self, db: Session, current_user_id: int, complaint_id: int) -> dict[str, object]:
        user = self._get_current_user(db, current_user_id)
        self._require_role(user, {"landlord", "admin"})
        complaint = self._get_operable_complaint(db, user, complaint_id)
        self._ensure_status(complaint, {ComplaintStatus.PROCESSING})
        before_status = complaint.status
        complaint.status = ComplaintStatus.RESOLVED
        complaint.resolved_at = self._now()
        self._notify_tenant(
            db,
            complaint,
            title="Complaint resolved",
            message=f"Complaint #{complaint.id} has been resolved.",
        )
        self._log_status_change(db, current_user_id, complaint.id, "resolve", before_status, complaint.status)
        return self._commit_and_serialize(db, complaint)

    def reject_complaint(self, db: Session, current_user_id: int, complaint_id: int) -> dict[str, object]:
        user = self._get_current_user(db, current_user_id)
        self._require_role(user, {"landlord", "admin"})
        complaint = self._get_operable_complaint(db, user, complaint_id)
        self._ensure_status(complaint, {ComplaintStatus.PENDING})
        before_status = complaint.status
        complaint.status = ComplaintStatus.REJECTED
        complaint.rejected_at = self._now()
        self._notify_tenant(
            db,
            complaint,
            title="Complaint rejected",
            message=f"Complaint #{complaint.id} has been rejected.",
        )
        self._log_status_change(db, current_user_id, complaint.id, "reject", before_status, complaint.status)
        return self._commit_and_serialize(db, complaint)

    def close_complaint(self, db: Session, current_user_id: int, complaint_id: int) -> dict[str, object]:
        user = self._get_current_user(db, current_user_id)
        self._require_role(user, {"tenant", "admin"})
        complaint = self._get_operable_complaint(db, user, complaint_id)
        self._ensure_status(complaint, {ComplaintStatus.RESOLVED})
        before_status = complaint.status
        complaint.status = ComplaintStatus.CLOSED
        complaint.closed_at = self._now()
        self._notify_landlord(
            db,
            complaint,
            title="Complaint closed",
            message=f"Complaint #{complaint.id} has been closed by the tenant.",
        )
        self._log_status_change(db, current_user_id, complaint.id, "close", before_status, complaint.status)
        return self._commit_and_serialize(db, complaint)

    def _commit_and_serialize(self, db: Session, complaint: Complaint) -> dict[str, object]:
        try:
            db.commit()
            db.refresh(complaint)
        except Exception:
            db.rollback()
            raise
        return self._serialize(complaint)

    def _get_current_user(self, db: Session, current_user_id: int) -> User:
        user = self.user_repository.get_by_id(db, current_user_id)
        if user is None:
            raise UnauthorizedException(message="unauthorized")
        return user

    def _require_role(self, user: User, allowed_roles: set[str]) -> None:
        if user.role not in allowed_roles:
            raise ForbiddenException()

    def _get_visible_complaint(self, db: Session, current_user_id: int, complaint_id: int) -> Complaint:
        user = self._get_current_user(db, current_user_id)
        if user.role == "admin":
            complaint = self.complaint_repository.get_by_id(db, complaint_id)
        else:
            complaint = self.complaint_repository.get_by_id_visible_to_user(db, complaint_id, current_user_id)
        if complaint is None:
            raise ComplaintNotFoundException()
        return complaint

    def _get_operable_complaint(self, db: Session, user: User, complaint_id: int) -> Complaint:
        if user.role == "admin":
            complaint = self.complaint_repository.get_by_id(db, complaint_id)
        elif user.role == "tenant":
            complaint = self.complaint_repository.get_by_id_and_tenant_id(db, complaint_id, user.id)
        elif user.role == "landlord":
            complaint = self.complaint_repository.get_by_id_and_landlord_id(db, complaint_id, user.id)
        else:
            raise ForbiddenException()
        if complaint is None:
            raise ComplaintNotFoundException()
        return complaint

    def _ensure_status(self, complaint: Complaint, allowed_statuses: set[str]) -> None:
        if complaint.status not in allowed_statuses:
            raise InvalidComplaintStatusException()

    def _serialize(self, complaint: Complaint) -> dict[str, object]:
        return ComplaintReadSchema.model_validate(complaint).model_dump(mode="json")

    def _now(self) -> datetime:
        return datetime.now()

    def _notify_tenant(self, db: Session, complaint: Complaint, *, title: str, message: str) -> None:
        self.notification_service.create_notification(
            db,
            user_ids=[complaint.tenant_id],
            source_type="complaint",
            source_id=complaint.id,
            title=title,
            message=message,
            auto_commit=False,
        )

    def _notify_landlord(self, db: Session, complaint: Complaint, *, title: str, message: str) -> None:
        self.notification_service.create_notification(
            db,
            user_ids=[complaint.landlord_id],
            source_type="complaint",
            source_id=complaint.id,
            title=title,
            message=message,
            auto_commit=False,
        )

    def _log_status_change(
        self,
        db: Session,
        current_user_id: int,
        complaint_id: int,
        action: str,
        before_status: str | None,
        after_status: str | None,
    ) -> None:
        self.operation_log_service.log_action(
            db,
            current_user_id=current_user_id,
            module=OperationLogModule.COMPLAINT,
            record_id=complaint_id,
            action=action,
            before_status=before_status,
            after_status=after_status,
        )
