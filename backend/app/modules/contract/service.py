from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.common.enums import AppointmentStatus, ContractStatus, HouseStatus
from app.common.enums import OperationLogModule
from app.common.pagination import build_page_result, get_offset
from app.core.exceptions import (
    AppointmentNotFoundException,
    ConflictException,
    ContractDateInvalidException,
    ContractNotFoundException,
    HouseActiveContractConflictException,
    HouseNotFoundException,
    InvalidContractStatusException,
    OwnHouseContractForbiddenException,
)
from app.modules.appointment.repository import AppointmentRepository
from app.modules.contract.model import Contract
from app.modules.contract.repository import ContractRepository
from app.modules.contract.schema import ContractHouseSummarySchema, ContractReadSchema
from app.modules.house.model import House
from app.modules.house.repository import HouseRepository
from app.modules.notification.service import NotificationService
from app.modules.operation_log.service import OperationLogService


class ContractService:
    def __init__(
        self,
        contract_repository: ContractRepository,
        appointment_repository: AppointmentRepository,
        house_repository: HouseRepository,
        notification_service: NotificationService,
        operation_log_service: OperationLogService,
    ) -> None:
        self.contract_repository = contract_repository
        self.appointment_repository = appointment_repository
        self.house_repository = house_repository
        self.notification_service = notification_service
        self.operation_log_service = operation_log_service

    def create_contract(
        self,
        db: Session,
        current_user_id: int,
        appointment_id: int,
        start_date: date,
        end_date: date,
        monthly_rent: Decimal,
        deposit: Decimal,
        remark: str | None = None,
    ) -> dict[str, object]:
        appointment = self.appointment_repository.get_by_id_and_landlord_id(
            db,
            appointment_id=appointment_id,
            landlord_id=current_user_id,
        )
        if appointment is None:
            raise AppointmentNotFoundException()
        if appointment.status != AppointmentStatus.CONFIRMED:
            raise InvalidContractStatusException()

        house = self.house_repository.get_by_id(db, appointment.house_id)
        if house is None or house.deleted_at is not None:
            raise HouseNotFoundException()
        if appointment.tenant_id == appointment.landlord_id:
            raise OwnHouseContractForbiddenException()
        if start_date >= end_date:
            raise ContractDateInvalidException()
        if self.contract_repository.count_pending_by_appointment_id(db, appointment.id) > 0:
            raise ConflictException(message="pending contract already exists")
        if self.contract_repository.count_active_by_house_id(db, appointment.house_id) > 0:
            raise HouseActiveContractConflictException()

        contract = Contract(
            house_id=appointment.house_id,
            tenant_id=appointment.tenant_id,
            landlord_id=appointment.landlord_id,
            appointment_id=appointment.id,
            start_date=start_date,
            end_date=end_date,
            monthly_rent=monthly_rent,
            deposit=deposit,
            status=ContractStatus.PENDING,
            remark=remark,
        )

        try:
            self.contract_repository.create(db, contract)
            db.flush()
            self._notify_tenant(
                db,
                contract,
                title="New contract created",
                message=f"Contract #{contract.id} is waiting for your confirmation.",
            )
            self.operation_log_service.log_action(
                db,
                current_user_id=current_user_id,
                module=OperationLogModule.CONTRACT,
                record_id=contract.id,
                action="create",
                before_status=None,
                after_status=contract.status,
            )
            db.commit()
            db.refresh(contract)
        except IntegrityError as exc:
            db.rollback()
            raise ConflictException(message="resource conflict") from exc
        except Exception:
            db.rollback()
            raise

        return self._serialize(contract, house)

    def list_contracts(
        self,
        db: Session,
        current_user_id: int,
        page: int,
        page_size: int,
    ) -> dict[str, object]:
        offset = get_offset(page, page_size)
        rows = self.contract_repository.list_related_to_user(
            db,
            user_id=current_user_id,
            offset=offset,
            limit=page_size,
        )
        total = self.contract_repository.count_related_to_user(db, current_user_id)
        return build_page_result(
            items=[self._serialize(contract, house) for contract, house in rows],
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_contract_detail(
        self,
        db: Session,
        current_user_id: int,
        contract_id: int,
    ) -> dict[str, object]:
        contract = self.contract_repository.get_by_id_and_user_id(db, contract_id, current_user_id)
        if contract is None:
            raise ContractNotFoundException()
        house = self._get_house_or_not_found(db, contract.house_id)
        return self._serialize(contract, house)

    def confirm_contract(
        self,
        db: Session,
        current_user_id: int,
        contract_id: int,
    ) -> dict[str, object]:
        contract = self.contract_repository.get_by_id_and_tenant_id(db, contract_id, current_user_id)
        if contract is None:
            raise ContractNotFoundException()
        if contract.status != ContractStatus.PENDING:
            raise InvalidContractStatusException()
        if self.contract_repository.count_active_by_house_id_excluding_contract(
            db,
            house_id=contract.house_id,
            excluded_contract_id=contract.id,
        ) > 0:
            raise HouseActiveContractConflictException()

        before_status = contract.status
        contract.status = ContractStatus.ACTIVE

        house = self._get_house_or_not_found(db, contract.house_id)
        house.status = HouseStatus.RENTED
        try:
            self._notify_landlord(
                db,
                contract,
                title="Contract confirmed",
                message=f"Contract #{contract.id} has been confirmed by the tenant.",
            )
            self.operation_log_service.log_action(
                db,
                current_user_id=current_user_id,
                module=OperationLogModule.CONTRACT,
                record_id=contract.id,
                action="confirm",
                before_status=before_status,
                after_status=contract.status,
            )
            db.commit()
            db.refresh(contract)
        except Exception:
            db.rollback()
            raise

        return self._serialize(contract, house)

    def reject_contract(
        self,
        db: Session,
        current_user_id: int,
        contract_id: int,
    ) -> dict[str, object]:
        contract = self.contract_repository.get_by_id_and_tenant_id(db, contract_id, current_user_id)
        if contract is None:
            raise ContractNotFoundException()
        if contract.status != ContractStatus.PENDING:
            raise InvalidContractStatusException()

        before_status = contract.status
        contract.status = ContractStatus.REJECTED
        try:
            self._notify_landlord(
                db,
                contract,
                title="Contract rejected",
                message=f"Contract #{contract.id} has been rejected by the tenant.",
            )
            self.operation_log_service.log_action(
                db,
                current_user_id=current_user_id,
                module=OperationLogModule.CONTRACT,
                record_id=contract.id,
                action="reject",
                before_status=before_status,
                after_status=contract.status,
            )
            db.commit()
            db.refresh(contract)
        except Exception:
            db.rollback()
            raise

        house = self._get_house_or_not_found(db, contract.house_id)
        return self._serialize(contract, house)

    def cancel_contract(
        self,
        db: Session,
        current_user_id: int,
        contract_id: int,
    ) -> dict[str, object]:
        contract = self.contract_repository.get_by_id_and_landlord_id(db, contract_id, current_user_id)
        if contract is None:
            raise ContractNotFoundException()
        if contract.status != ContractStatus.PENDING:
            raise InvalidContractStatusException()

        before_status = contract.status
        contract.status = ContractStatus.CANCELLED
        try:
            self._notify_tenant(
                db,
                contract,
                title="Contract cancelled",
                message=f"Contract #{contract.id} has been cancelled by the landlord.",
            )
            self.operation_log_service.log_action(
                db,
                current_user_id=current_user_id,
                module=OperationLogModule.CONTRACT,
                record_id=contract.id,
                action="cancel",
                before_status=before_status,
                after_status=contract.status,
            )
            db.commit()
            db.refresh(contract)
        except Exception:
            db.rollback()
            raise

        house = self._get_house_or_not_found(db, contract.house_id)
        return self._serialize(contract, house)

    def terminate_contract(
        self,
        db: Session,
        current_user_id: int,
        contract_id: int,
    ) -> dict[str, object]:
        contract = self.contract_repository.get_by_id_and_landlord_id(db, contract_id, current_user_id)
        if contract is None:
            raise ContractNotFoundException()
        if contract.status != ContractStatus.ACTIVE:
            raise InvalidContractStatusException()

        before_status = contract.status
        contract.status = ContractStatus.TERMINATED
        try:
            house = self._get_house_or_not_found(db, contract.house_id)
            house.status = HouseStatus.LISTED
            self._notify_tenant(
                db,
                contract,
                title="Contract terminated",
                message=f"Contract #{contract.id} has been terminated by the landlord.",
            )
            self.operation_log_service.log_action(
                db,
                current_user_id=current_user_id,
                module=OperationLogModule.CONTRACT,
                record_id=contract.id,
                action="terminate",
                before_status=before_status,
                after_status=contract.status,
            )
            db.commit()
            db.refresh(contract)
        except Exception:
            db.rollback()
            raise

        return self._serialize(contract, house)

    def _get_house_or_not_found(self, db: Session, house_id: int) -> House:
        house = self.house_repository.get_by_id(db, house_id)
        if house is None:
            raise HouseNotFoundException()
        return house

    def _serialize(self, contract: Contract, house: House) -> dict[str, object]:
        house_data = ContractHouseSummarySchema.model_validate(house)
        return ContractReadSchema(
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

    def _notify_tenant(self, db: Session, contract: Contract, *, title: str, message: str) -> None:
        self.notification_service.create_notification(
            db,
            user_ids=[contract.tenant_id],
            source_type="contract",
            source_id=contract.id,
            title=title,
            message=message,
            auto_commit=False,
        )

    def _notify_landlord(self, db: Session, contract: Contract, *, title: str, message: str) -> None:
        self.notification_service.create_notification(
            db,
            user_ids=[contract.landlord_id],
            source_type="contract",
            source_id=contract.id,
            title=title,
            message=message,
            auto_commit=False,
        )
