from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.common.base_repository import BaseRepository
from app.common.enums import ContractStatus
from app.modules.contract.model import Contract
from app.modules.house.model import House


class ContractRepository(BaseRepository[Contract]):
    def __init__(self) -> None:
        super().__init__(Contract)

    def get_by_id_and_user_id(
        self,
        db: Session,
        contract_id: int,
        user_id: int,
    ) -> Contract | None:
        stmt = select(Contract).where(
            Contract.id == contract_id,
            or_(
                Contract.tenant_id == user_id,
                Contract.landlord_id == user_id,
            ),
        )
        return db.execute(stmt).scalar_one_or_none()

    def get_by_id_and_tenant_id(
        self,
        db: Session,
        contract_id: int,
        tenant_id: int,
    ) -> Contract | None:
        stmt = select(Contract).where(
            Contract.id == contract_id,
            Contract.tenant_id == tenant_id,
        )
        return db.execute(stmt).scalar_one_or_none()

    def get_by_id_and_landlord_id(
        self,
        db: Session,
        contract_id: int,
        landlord_id: int,
    ) -> Contract | None:
        stmt = select(Contract).where(
            Contract.id == contract_id,
            Contract.landlord_id == landlord_id,
        )
        return db.execute(stmt).scalar_one_or_none()

    def list_related_to_user(
        self,
        db: Session,
        user_id: int,
        offset: int,
        limit: int,
    ) -> list[tuple[Contract, House]]:
        stmt = (
            select(Contract, House)
            .join(House, House.id == Contract.house_id)
            .where(
                or_(
                    Contract.tenant_id == user_id,
                    Contract.landlord_id == user_id,
                )
            )
            .order_by(Contract.created_at.desc(), Contract.id.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(db.execute(stmt).all())

    def count_related_to_user(self, db: Session, user_id: int) -> int:
        stmt = select(func.count()).select_from(Contract).where(
            or_(
                Contract.tenant_id == user_id,
                Contract.landlord_id == user_id,
            )
        )
        return int(db.execute(stmt).scalar_one())

    def count_pending_by_appointment_id(self, db: Session, appointment_id: int) -> int:
        stmt = select(func.count()).select_from(Contract).where(
            Contract.appointment_id == appointment_id,
            Contract.status == ContractStatus.PENDING,
        )
        return int(db.execute(stmt).scalar_one())

    def count_active_by_house_id(self, db: Session, house_id: int) -> int:
        stmt = select(func.count()).select_from(Contract).where(
            Contract.house_id == house_id,
            Contract.status == ContractStatus.ACTIVE,
        )
        return int(db.execute(stmt).scalar_one())

    def count_active_by_house_id_excluding_contract(
        self,
        db: Session,
        house_id: int,
        excluded_contract_id: int,
    ) -> int:
        stmt = select(func.count()).select_from(Contract).where(
            Contract.house_id == house_id,
            Contract.status == ContractStatus.ACTIVE,
            Contract.id != excluded_contract_id,
        )
        return int(db.execute(stmt).scalar_one())
