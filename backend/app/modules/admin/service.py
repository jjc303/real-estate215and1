from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.common.email import normalize_email
from app.common.base_schema import BaseSchema
from app.common.enums import ContractStatus
from app.common.pagination import build_page_result, get_offset
from app.common.enums import OperationLogModule
from app.core.exceptions import (
    ContractNotFoundException,
    ForbiddenException,
    HouseNotFoundException,
    InvalidContractStatusException,
    UnauthorizedException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from app.core.security import hash_password
from app.modules.admin.repository import AdminRepository
from app.modules.admin.schema import (
    ContractAdminSchema,
    HouseAdminSchema,
    UserAdminSchema,
)
from app.modules.complaint.schema import ComplaintReadSchema
from app.modules.complaint.service import ComplaintService
from app.modules.contract.model import Contract
from app.modules.contract.schema import ContractHouseSummarySchema
from app.modules.house.model import House
from app.modules.notification.service import NotificationService
from app.modules.operation_log.service import OperationLogService
from app.modules.repair.schema import RepairReadSchema
from app.modules.repair.service import RepairService
from app.modules.user.model import User
from app.modules.user.repository import UserRepository


class AdminService:
    def __init__(
        self,
        admin_repository: AdminRepository,
        user_repository: UserRepository,
        repair_service: RepairService,
        complaint_service: ComplaintService,
        notification_service: NotificationService,
        operation_log_service: OperationLogService,
    ) -> None:
        self.admin_repository = admin_repository
        self.user_repository = user_repository
        self.repair_service = repair_service
        self.complaint_service = complaint_service
        self.notification_service = notification_service
        self.operation_log_service = operation_log_service

    def list_users(
        self, db: Session, current_user_id: int, page: int, page_size: int,
        keyword: str | None = None,
        role: str | None = None,
    ) -> dict[str, object]:
        self._require_admin(db, current_user_id)
        offset = get_offset(page, page_size)
        users = self.admin_repository.list_all_users(db, offset=offset, limit=page_size, keyword=keyword, role=role)
        total = self.admin_repository.count_all_users(db, keyword=keyword, role=role)
        items = [self._serialize_user(user) for user in users]
        return build_page_result(items=items, total=total, page=page, page_size=page_size)

    def get_user_detail(self, db: Session, current_user_id: int, user_id: int) -> dict[str, object]:
        self._require_admin(db, current_user_id)
        user = self.user_repository.get_by_id(db, user_id)
        if user is None:
            raise UserNotFoundException()
        return self._serialize_user(user)

    def create_user(self, db: Session, current_user_id: int, data: BaseSchema) -> dict[str, object]:
        self._require_admin(db, current_user_id)
        if self.user_repository.get_by_username(db, data.username) is not None:
            raise UserAlreadyExistsException(message="username already exists")
        normalized_email = normalize_email(data.email)
        if normalized_email is not None and self.user_repository.get_by_email(db, normalized_email) is not None:
            raise UserAlreadyExistsException(message="email already exists")

        user = User(
            username=data.username,
            password=hash_password(data.password),
            role=data.role,
            real_name=data.real_name,
            phone=data.phone,
            email=normalized_email,
            status=data.status,
        )
        try:
            self.user_repository.create(db, user)
            db.commit()
            db.refresh(user)
        except IntegrityError as exc:
            db.rollback()
            raise UserAlreadyExistsException(message="user already exists") from exc
        except Exception:
            db.rollback()
            raise
        return self._serialize_user(user)

    def update_user(self, db: Session, current_user_id: int, user_id: int, data: BaseSchema) -> dict[str, object]:
        self._require_admin(db, current_user_id)
        user = self.user_repository.get_by_id(db, user_id)
        if user is None:
            raise UserNotFoundException()

        existing_user = self.user_repository.get_by_username(db, data.username)
        if existing_user is not None and existing_user.id != user.id:
            raise UserAlreadyExistsException(message="username already exists")
        normalized_email = normalize_email(data.email)
        if normalized_email is not None:
            existing_email_user = self.user_repository.get_by_email(db, normalized_email)
            if existing_email_user is not None and existing_email_user.id != user.id:
                raise UserAlreadyExistsException(message="email already exists")

        user.username = data.username
        if data.password is not None:
            user.password = hash_password(data.password)
        user.role = data.role
        user.real_name = data.real_name
        user.phone = data.phone
        user.email = normalized_email

        try:
            db.commit()
            db.refresh(user)
        except IntegrityError as exc:
            db.rollback()
            raise UserAlreadyExistsException(message="user already exists") from exc
        except Exception:
            db.rollback()
            raise
        return self._serialize_user(user)

    def update_user_status(self, db: Session, current_user_id: int, user_id: int, status: str) -> dict[str, object]:
        self._require_admin(db, current_user_id)
        user = self.user_repository.get_by_id(db, user_id)
        if user is None:
            raise UserNotFoundException()
        user.status = status
        try:
            db.commit()
            db.refresh(user)
        except Exception:
            db.rollback()
            raise
        return self._serialize_user(user)

    def list_houses(
        self,
        db: Session,
        current_user_id: int,
        page: int,
        page_size: int,
        *,
        region: str | None = None,
        house_type: str | None = None,
        min_rent: object | None = None,
        max_rent: object | None = None,
        keyword: str | None = None,
        min_area: object | None = None,
        max_area: object | None = None,
        status: str | None = None,
    ) -> dict[str, object]:
        self._require_admin(db, current_user_id)
        offset = get_offset(page, page_size)
        houses = self.admin_repository.list_all_houses(
            db,
            offset=offset,
            limit=page_size,
            region=region,
            house_type=house_type,
            min_rent=min_rent,
            max_rent=max_rent,
            keyword=keyword,
            min_area=min_area,
            max_area=max_area,
            status=status,
        )
        total = self.admin_repository.count_all_houses(
            db,
            region=region,
            house_type=house_type,
            min_rent=min_rent,
            max_rent=max_rent,
            keyword=keyword,
            min_area=min_area,
            max_area=max_area,
            status=status,
        )
        items = [HouseAdminSchema.model_validate(house).model_dump(mode="json") for house in houses]
        return build_page_result(items=items, total=total, page=page, page_size=page_size)

    def get_house_detail(self, db: Session, current_user_id: int, house_id: int) -> dict[str, object]:
        self._require_admin(db, current_user_id)
        house = self.admin_repository.get_house_by_id_admin(db, house_id)
        if house is None:
            raise HouseNotFoundException()
        return HouseAdminSchema.model_validate(house).model_dump(mode="json")

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
        self._require_admin(db, current_user_id)
        return self.complaint_service.list_complaints(
            db,
            current_user_id=current_user_id,
            page=page,
            page_size=page_size,
            status=status,
            keyword=keyword,
            date_from=date_from,
            date_to=date_to,
        )

    def get_complaint_detail(self, db: Session, current_user_id: int, complaint_id: int) -> dict[str, object]:
        self._require_admin(db, current_user_id)
        result = self.complaint_service.get_complaint_detail(
            db,
            current_user_id=current_user_id,
            complaint_id=complaint_id,
        )
        return ComplaintReadSchema(**result).model_dump(mode="json")

    def process_complaint(self, db: Session, current_user_id: int, complaint_id: int) -> dict[str, object]:
        self._require_admin(db, current_user_id)
        return self.complaint_service.process_complaint(db, current_user_id=current_user_id, complaint_id=complaint_id)

    def resolve_complaint(self, db: Session, current_user_id: int, complaint_id: int) -> dict[str, object]:
        self._require_admin(db, current_user_id)
        return self.complaint_service.resolve_complaint(db, current_user_id=current_user_id, complaint_id=complaint_id)

    def reject_complaint(self, db: Session, current_user_id: int, complaint_id: int) -> dict[str, object]:
        self._require_admin(db, current_user_id)
        return self.complaint_service.reject_complaint(db, current_user_id=current_user_id, complaint_id=complaint_id)

    def close_complaint(self, db: Session, current_user_id: int, complaint_id: int) -> dict[str, object]:
        self._require_admin(db, current_user_id)
        return self.complaint_service.close_complaint(db, current_user_id=current_user_id, complaint_id=complaint_id)

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
        self._require_admin(db, current_user_id)
        return self.repair_service.list_repairs(
            db,
            current_user_id=current_user_id,
            page=page,
            page_size=page_size,
            status=status,
            keyword=keyword,
            date_from=date_from,
            date_to=date_to,
        )

    def get_repair_detail(self, db: Session, current_user_id: int, repair_id: int) -> dict[str, object]:
        self._require_admin(db, current_user_id)
        result = self.repair_service.get_repair_detail(db, current_user_id=current_user_id, repair_id=repair_id)
        return RepairReadSchema(**result).model_dump(mode="json")

    def process_repair(self, db: Session, current_user_id: int, repair_id: int) -> dict[str, object]:
        self._require_admin(db, current_user_id)
        return self.repair_service.process_repair(db, current_user_id=current_user_id, repair_id=repair_id)

    def complete_repair(self, db: Session, current_user_id: int, repair_id: int) -> dict[str, object]:
        self._require_admin(db, current_user_id)
        return self.repair_service.complete_repair(db, current_user_id=current_user_id, repair_id=repair_id)

    def reject_repair(self, db: Session, current_user_id: int, repair_id: int) -> dict[str, object]:
        self._require_admin(db, current_user_id)
        return self.repair_service.reject_repair(db, current_user_id=current_user_id, repair_id=repair_id)

    def close_repair(self, db: Session, current_user_id: int, repair_id: int) -> dict[str, object]:
        self._require_admin(db, current_user_id)
        return self.repair_service.close_repair(db, current_user_id=current_user_id, repair_id=repair_id)

    def list_contracts(
        self,
        db: Session,
        current_user_id: int,
        page: int,
        page_size: int,
        keyword: str | None = None,
        status: str | None = None,
    ) -> dict[str, object]:
        self._require_admin(db, current_user_id)
        offset = get_offset(page, page_size)
        rows = self.admin_repository.list_all_contracts(db, offset=offset, limit=page_size, keyword=keyword, status=status)
        total = self.admin_repository.count_all_contracts(db, keyword=keyword, status=status)
        items = [self._serialize_contract(contract, house) for contract, house in rows]
        return build_page_result(items=items, total=total, page=page, page_size=page_size)

    def list_bills(
        self,
        db: Session,
        current_user_id: int,
        page: int,
        page_size: int,
        keyword: str | None = None,
        status: str | None = None,
        bill_type: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> dict[str, object]:
        self._require_admin(db, current_user_id)
        offset = get_offset(page, page_size)
        items = self.admin_repository.list_all_bills(
            db, offset=offset, limit=page_size,
            keyword=keyword, status=status, bill_type=bill_type,
            date_from=date_from, date_to=date_to,
        )
        total = self.admin_repository.count_all_bills(
            db,
            keyword=keyword, status=status, bill_type=bill_type,
            date_from=date_from, date_to=date_to,
        )
        from app.modules.bill.schema import BillReadSchema
        serialized = [BillReadSchema.model_validate(b).model_dump(mode="json") for b in items]
        return build_page_result(items=serialized, total=total, page=page, page_size=page_size)

    def list_logs(
        self,
        db: Session,
        current_user_id: int,
        page: int,
        page_size: int,
        module: str | None = None,
        user_id: int | None = None,
    ) -> dict[str, object]:
        self._require_admin(db, current_user_id)
        return self.operation_log_service.list_logs(
            db,
            current_user_id=current_user_id,
            page=page,
            page_size=page_size,
            module=module,
            user_id=user_id,
        )

    def get_contract_detail(self, db: Session, current_user_id: int, contract_id: int) -> dict[str, object]:
        self._require_admin(db, current_user_id)
        row = self.admin_repository.get_contract_by_id_admin(db, contract_id)
        if row is None:
            raise ContractNotFoundException()
        contract, house = row
        return self._serialize_contract(contract, house)

    def update_contract_status(
        self,
        db: Session,
        current_user_id: int,
        contract_id: int,
        status: str,
    ) -> dict[str, object]:
        self._require_admin(db, current_user_id)
        row = self.admin_repository.get_contract_by_id_admin(db, contract_id)
        if row is None:
            raise ContractNotFoundException()
        contract, house = row
        before_status = contract.status

        if status == ContractStatus.ACTIVE and contract.status == ContractStatus.PENDING:
            contract.status = ContractStatus.ACTIVE
            self._notify_contract_parties(
                db,
                contract,
                title="Contract activated by admin",
                tenant_message=f"Contract #{contract.id} has been activated by admin.",
                landlord_message=f"Contract #{contract.id} has been activated by admin.",
            )
        elif status == ContractStatus.CANCELLED and contract.status == ContractStatus.PENDING:
            contract.status = ContractStatus.CANCELLED
            self._notify_contract_parties(
                db,
                contract,
                title="Contract cancelled by admin",
                tenant_message=f"Contract #{contract.id} has been cancelled by admin.",
                landlord_message=f"Contract #{contract.id} has been cancelled by admin.",
            )
        elif status == ContractStatus.TERMINATED and contract.status == ContractStatus.ACTIVE:
            contract.status = ContractStatus.TERMINATED
            self._notify_contract_parties(
                db,
                contract,
                title="Contract terminated by admin",
                tenant_message=f"Contract #{contract.id} has been terminated by admin.",
                landlord_message=f"Contract #{contract.id} has been terminated by admin.",
            )
        else:
            raise InvalidContractStatusException()

        try:
            self.operation_log_service.log_action(
                db,
                current_user_id=current_user_id,
                module=OperationLogModule.CONTRACT,
                record_id=contract.id,
                action="admin_status_update",
                before_status=before_status,
                after_status=contract.status,
            )
            db.commit()
            db.refresh(contract)
        except Exception:
            db.rollback()
            raise
        return self._serialize_contract(contract, house)

    def _require_admin(self, db: Session, current_user_id: int) -> User:
        user = self.user_repository.get_by_id(db, current_user_id)
        if user is None:
            raise UnauthorizedException(message="unauthorized")
        if user.role != "admin":
            raise ForbiddenException()
        return user

    def _serialize_user(self, user: User) -> dict[str, object]:
        return UserAdminSchema.model_validate(user).model_dump(mode="json")

    def _serialize_contract(self, contract: Contract, house: House) -> dict[str, object]:
        house_data = ContractHouseSummarySchema.model_validate(house)
        return ContractAdminSchema(
            id=contract.id,
            house_id=contract.house_id,
            tenant_id=contract.tenant_id,
            landlord_id=contract.landlord_id,
            appointment_id=contract.appointment_id,
            start_date=contract.start_date,
            end_date=contract.end_date,
            monthly_rent=contract.monthly_rent,
            deposit=contract.deposit,
            status=contract.status,
            remark=contract.remark,
            created_at=contract.created_at,
            updated_at=contract.updated_at,
            house=house_data,
        ).model_dump(mode="json")

    def _notify_contract_parties(
        self,
        db: Session,
        contract: Contract,
        *,
        title: str,
        tenant_message: str,
        landlord_message: str,
    ) -> None:
        self.notification_service.create_notification(
            db,
            user_ids=[contract.tenant_id],
            source_type="contract",
            source_id=contract.id,
            title=title,
            message=tenant_message,
            auto_commit=False,
        )
        self.notification_service.create_notification(
            db,
            user_ids=[contract.landlord_id],
            source_type="contract",
            source_id=contract.id,
            title=title,
            message=landlord_message,
            auto_commit=False,
        )
