from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.common.base_repository import BaseRepository
from app.modules.operation_log.model import OperationLog


class OperationLogRepository(BaseRepository[OperationLog]):
    def __init__(self) -> None:
        super().__init__(OperationLog)

    def list_page_with_filters(
        self,
        db: Session,
        *,
        offset: int,
        limit: int,
        module: str | None = None,
        user_id: int | None = None,
    ) -> list[OperationLog]:
        stmt = select(OperationLog)
        stmt = self._apply_filters(stmt, module=module, user_id=user_id)
        stmt = stmt.order_by(OperationLog.created_at.desc(), OperationLog.id.desc()).offset(offset).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def count_with_filters(
        self,
        db: Session,
        *,
        module: str | None = None,
        user_id: int | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(OperationLog)
        stmt = self._apply_filters(stmt, module=module, user_id=user_id)
        return int(db.execute(stmt).scalar_one())

    def _apply_filters(self, stmt, *, module: str | None, user_id: int | None):
        if module is not None:
            stmt = stmt.where(OperationLog.module == module)
        if user_id is not None:
            stmt = stmt.where(OperationLog.user_id == user_id)
        return stmt
