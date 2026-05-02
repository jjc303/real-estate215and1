from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.modules.statistics.repository import StatisticsRepository
from app.modules.statistics.schema import (
    ActiveUsersSchema,
    ComplaintRepairCountSchema,
    HouseUtilizationSchema,
    RentIncomeItemSchema,
    RentIncomeSchema,
)
from app.modules.user.model import User
from app.modules.user.repository import UserRepository


class StatisticsService:
    def __init__(
        self,
        statistics_repository: StatisticsRepository,
        user_repository: UserRepository,
    ) -> None:
        self.statistics_repository = statistics_repository
        self.user_repository = user_repository

    def get_house_utilization(self, db: Session, current_user_id: int) -> dict[str, object]:
        self._require_admin(db, current_user_id)
        total_houses = self.statistics_repository.count_total_houses(db)
        occupied_houses = self.statistics_repository.count_occupied_houses(db)
        utilization_rate = 0.0 if total_houses == 0 else occupied_houses / total_houses
        return HouseUtilizationSchema(
            total_houses=total_houses,
            occupied_houses=occupied_houses,
            utilization_rate=utilization_rate,
        ).model_dump(mode="json")

    def get_rent_income(self, db: Session, current_user_id: int) -> dict[str, object]:
        self._require_admin(db, current_user_id)
        total_income = float(self.statistics_repository.sum_total_rent_income(db) or 0)
        monthly_income = [
            RentIncomeItemSchema(
                month=f"{year:04d}-{month:02d}",
                amount=float(amount or 0),
            )
            for year, month, amount in self.statistics_repository.list_monthly_rent_income(db)
        ]
        return RentIncomeSchema(
            total_income=total_income,
            monthly_income=monthly_income,
        ).model_dump(mode="json")

    def get_active_users(self, db: Session, current_user_id: int) -> dict[str, object]:
        self._require_admin(db, current_user_id)
        active_user_count = self.statistics_repository.count_active_users(db)
        return ActiveUsersSchema(active_user_count=active_user_count).model_dump(mode="json")

    def get_complaint_repair_count(self, db: Session, current_user_id: int) -> dict[str, object]:
        self._require_admin(db, current_user_id)
        repair_count = self.statistics_repository.count_repairs(db)
        complaint_count = self.statistics_repository.count_complaints(db)
        return ComplaintRepairCountSchema(
            repair_count=repair_count,
            complaint_count=complaint_count,
        ).model_dump(mode="json")

    def _require_admin(self, db: Session, current_user_id: int) -> User:
        user = self.user_repository.get_by_id(db, current_user_id)
        if user is None:
            raise UnauthorizedException(message="unauthorized")
        if user.role != "admin":
            raise ForbiddenException()
        return user
