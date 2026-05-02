from __future__ import annotations

from sqlalchemy.orm import Session

from app.common.pagination import build_page_result, get_offset
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.modules.operation_log.model import OperationLog
from app.modules.operation_log.repository import OperationLogRepository
from app.modules.operation_log.schema import OperationLogReadSchema
from app.modules.user.model import User
from app.modules.user.repository import UserRepository


class OperationLogService:
    def __init__(
        self,
        operation_log_repository: OperationLogRepository,
        user_repository: UserRepository,
    ) -> None:
        self.operation_log_repository = operation_log_repository
        self.user_repository = user_repository

    def log_action(
        self,
        db: Session,
        *,
        current_user_id: int,
        module: str,
        record_id: int,
        action: str,
        before_status: str | None = None,
        after_status: str | None = None,
    ) -> None:
        log = OperationLog(
            user_id=current_user_id,
            module=module,
            record_id=record_id,
            action=action,
            before_status=before_status,
            after_status=after_status,
        )
        self.operation_log_repository.create(db, log)

    def list_logs(
        self,
        db: Session,
        *,
        current_user_id: int,
        page: int,
        page_size: int,
        module: str | None = None,
        user_id: int | None = None,
    ) -> dict[str, object]:
        self._require_admin(db, current_user_id)
        offset = get_offset(page, page_size)
        logs = self.operation_log_repository.list_page_with_filters(
            db,
            offset=offset,
            limit=page_size,
            module=module,
            user_id=user_id,
        )
        total = self.operation_log_repository.count_with_filters(
            db,
            module=module,
            user_id=user_id,
        )
        return build_page_result(
            items=[self._serialize(log) for log in logs],
            total=total,
            page=page,
            page_size=page_size,
        )

    def _require_admin(self, db: Session, current_user_id: int) -> User:
        user = self.user_repository.get_by_id(db, current_user_id)
        if user is None:
            raise UnauthorizedException(message="unauthorized")
        if user.role != "admin":
            raise ForbiddenException()
        return user

    def _serialize(self, log: OperationLog) -> dict[str, object]:
        return OperationLogReadSchema.model_validate(log).model_dump(mode="json")
