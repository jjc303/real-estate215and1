from __future__ import annotations

from datetime import date, datetime

from sqlalchemy.orm import Session

from app.common.enums import ContractStatus, RepairStatus
from app.common.enums import OperationLogModule
from app.common.pagination import build_page_result, get_offset
from app.core.exceptions import (
    ContractNotActiveForRepairException,
    ContractNotFoundException,
    ForbiddenException,
    InvalidRepairStatusException,
    RepairNotFoundException,
    UnauthorizedException,
)
from app.modules.contract.repository import ContractRepository
from app.modules.repair.model import Repair
from app.modules.repair.repository import RepairRepository
from app.modules.repair.schema import RepairReadSchema
from app.modules.user.model import User
from app.modules.user.repository import UserRepository
from app.modules.notification.service import NotificationService
from app.modules.operation_log.service import OperationLogService


class RepairService:
    def __init__(
        self,
        repair_repository: RepairRepository,
        contract_repository: ContractRepository,
        user_repository: UserRepository,
        notification_service: NotificationService,
        operation_log_service: OperationLogService,
    ) -> None:
        self.repair_repository = repair_repository
        self.contract_repository = contract_repository
        self.user_repository = user_repository
        self.notification_service = notification_service
        self.operation_log_service = operation_log_service

    def create_repair(
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
            raise ContractNotActiveForRepairException()

        repair = Repair(
            contract_id=contract.id,
            house_id=contract.house_id,
            tenant_id=contract.tenant_id,
            landlord_id=contract.landlord_id,
            description=description,
            status=RepairStatus.PENDING,
        )

        try:
            self.repair_repository.create(db, repair)
            db.flush()
            self._notify_landlord(
                db,
                repair,
                title="新报修申请",
                message=f"报修 #{repair.id} 已提交。",
            )
            self.operation_log_service.log_action(
                db,
                current_user_id=current_user_id,
                module=OperationLogModule.REPAIR,
                record_id=repair.id,
                action="create",
                before_status=None,
                after_status=repair.status,
            )
            db.commit()
            db.refresh(repair)
        except Exception:
            db.rollback()
            raise

        return self._serialize(repair)

    def list_repairs(
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
            repairs = self.repair_repository.list_page_with_filters(
                db,
                offset=offset,
                limit=page_size,
                status=status,
                keyword=keyword,
                date_from=date_from,
                date_to=date_to,
            )
            total = self.repair_repository.count_all_with_filters(
                db, status=status, keyword=keyword, date_from=date_from, date_to=date_to,
            )
        else:
            repairs = self.repair_repository.list_related_to_user(
                db,
                user_id=current_user_id,
                offset=offset,
                limit=page_size,
                status=status,
            )
            total = self.repair_repository.count_related_to_user(db, current_user_id, status=status)

        return build_page_result(
            items=[self._serialize(repair) for repair in repairs],
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_repair_detail(self, db: Session, current_user_id: int, repair_id: int) -> dict[str, object]:
        repair = self._get_visible_repair(db, current_user_id, repair_id)
        return self._serialize(repair)

    def process_repair(self, db: Session, current_user_id: int, repair_id: int) -> dict[str, object]:
        user = self._get_current_user(db, current_user_id)
        self._require_role(user, {"landlord", "admin"})
        repair = self._get_operable_repair(db, user, repair_id)
        self._ensure_status(repair, {RepairStatus.PENDING, RepairStatus.REOPENED})
        before_status = repair.status
        repair.status = RepairStatus.PROCESSING
        repair.processed_at = self._now()
        self._notify_tenant(
            db,
            repair,
            title="报修处理中",
            message=f"报修 #{repair.id} 正在处理中。",
        )
        self._log_status_change(db, current_user_id, repair.id, "process", before_status, repair.status)
        return self._commit_and_serialize(db, repair)

    def complete_repair(self, db: Session, current_user_id: int, repair_id: int) -> dict[str, object]:
        user = self._get_current_user(db, current_user_id)
        self._require_role(user, {"landlord", "admin"})
        repair = self._get_operable_repair(db, user, repair_id)
        self._ensure_status(repair, {RepairStatus.PROCESSING})
        before_status = repair.status
        repair.status = RepairStatus.COMPLETED
        repair.completed_at = self._now()
        self._notify_tenant(
            db,
            repair,
            title="报修已完成",
            message=f"报修 #{repair.id} 已完成。",
        )
        self._log_status_change(db, current_user_id, repair.id, "complete", before_status, repair.status)
        return self._commit_and_serialize(db, repair)

    def reject_repair(self, db: Session, current_user_id: int, repair_id: int) -> dict[str, object]:
        user = self._get_current_user(db, current_user_id)
        self._require_role(user, {"landlord", "admin"})
        repair = self._get_operable_repair(db, user, repair_id)
        self._ensure_status(repair, {RepairStatus.PENDING, RepairStatus.REOPENED})
        before_status = repair.status
        repair.status = RepairStatus.REJECTED
        repair.rejected_at = self._now()
        self._notify_tenant(
            db,
            repair,
            title="报修已驳回",
            message=f"报修 #{repair.id} 已被驳回。",
        )
        self._log_status_change(db, current_user_id, repair.id, "reject", before_status, repair.status)
        return self._commit_and_serialize(db, repair)

    def close_repair(self, db: Session, current_user_id: int, repair_id: int) -> dict[str, object]:
        user = self._get_current_user(db, current_user_id)
        self._require_role(user, {"tenant", "admin"})
        repair = self._get_operable_repair(db, user, repair_id)
        self._ensure_status(repair, {RepairStatus.COMPLETED})
        before_status = repair.status
        repair.status = RepairStatus.CLOSED
        repair.closed_at = self._now()
        self._notify_landlord(
            db,
            repair,
            title="报修已关闭",
            message=f"Repair #{repair.id} has been closed by the tenant.",
        )
        self._log_status_change(db, current_user_id, repair.id, "close", before_status, repair.status)
        return self._commit_and_serialize(db, repair)

    def reopen_repair(self, db: Session, current_user_id: int, repair_id: int) -> dict[str, object]:
        user = self._get_current_user(db, current_user_id)
        self._require_role(user, {"tenant", "admin"})
        repair = self._get_operable_repair(db, user, repair_id)
        self._ensure_status(repair, {RepairStatus.COMPLETED, RepairStatus.CLOSED})
        before_status = repair.status
        repair.status = RepairStatus.REOPENED
        repair.reopened_at = self._now()
        self._notify_landlord(
            db,
            repair,
            title="报修已重新开启",
            message=f"Repair #{repair.id} has been reopened by the tenant.",
        )
        self._log_status_change(db, current_user_id, repair.id, "reopen", before_status, repair.status)
        return self._commit_and_serialize(db, repair)

    def _commit_and_serialize(self, db: Session, repair: Repair) -> dict[str, object]:
        try:
            db.commit()
            db.refresh(repair)
        except Exception:
            db.rollback()
            raise
        return self._serialize(repair)

    def _get_current_user(self, db: Session, current_user_id: int) -> User:
        user = self.user_repository.get_by_id(db, current_user_id)
        if user is None:
            raise UnauthorizedException(message="unauthorized")
        return user

    def _require_role(self, user: User, allowed_roles: set[str]) -> None:
        if user.role not in allowed_roles:
            raise ForbiddenException()

    def _get_visible_repair(self, db: Session, current_user_id: int, repair_id: int) -> Repair:
        user = self._get_current_user(db, current_user_id)
        if user.role == "admin":
            repair = self.repair_repository.get_by_id(db, repair_id)
        else:
            repair = self.repair_repository.get_by_id_visible_to_user(db, repair_id, current_user_id)
        if repair is None:
            raise RepairNotFoundException()
        return repair

    def _get_operable_repair(self, db: Session, user: User, repair_id: int) -> Repair:
        if user.role == "admin":
            repair = self.repair_repository.get_by_id(db, repair_id)
        elif user.role == "tenant":
            repair = self.repair_repository.get_by_id_and_tenant_id(db, repair_id, user.id)
        elif user.role == "landlord":
            repair = self.repair_repository.get_by_id_and_landlord_id(db, repair_id, user.id)
        else:
            raise ForbiddenException()
        if repair is None:
            raise RepairNotFoundException()
        return repair

    def _ensure_status(self, repair: Repair, allowed_statuses: set[str]) -> None:
        if repair.status not in allowed_statuses:
            raise InvalidRepairStatusException()

    def _serialize(self, repair: Repair) -> dict[str, object]:
        return RepairReadSchema.model_validate(repair).model_dump(mode="json")

    def _now(self) -> datetime:
        return datetime.now()

    def _notify_tenant(self, db: Session, repair: Repair, *, title: str, message: str) -> None:
        self.notification_service.create_notification(
            db,
            user_ids=[repair.tenant_id],
            source_type="repair",
            source_id=repair.id,
            title=title,
            message=message,
            auto_commit=False,
        )

    def _notify_landlord(self, db: Session, repair: Repair, *, title: str, message: str) -> None:
        self.notification_service.create_notification(
            db,
            user_ids=[repair.landlord_id],
            source_type="repair",
            source_id=repair.id,
            title=title,
            message=message,
            auto_commit=False,
        )

    def _log_status_change(
        self,
        db: Session,
        current_user_id: int,
        repair_id: int,
        action: str,
        before_status: str | None,
        after_status: str | None,
    ) -> None:
        self.operation_log_service.log_action(
            db,
            current_user_id=current_user_id,
            module=OperationLogModule.REPAIR,
            record_id=repair_id,
            action=action,
            before_status=before_status,
            after_status=after_status,
        )
