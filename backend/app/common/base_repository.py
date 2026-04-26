from __future__ import annotations

from typing import Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import Base


ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    def __init__(self, model: type[ModelT]) -> None:
        self.model = model

    def create(self, db: Session, obj: ModelT) -> ModelT:
        db.add(obj)
        return obj

    def get_by_id(self, db: Session, obj_id: int) -> ModelT | None:
        stmt = select(self.model).where(self.model.id == obj_id)
        return db.execute(stmt).scalar_one_or_none()

    def delete(self, db: Session, obj: ModelT) -> None:
        db.delete(obj)

    def count_all(self, db: Session) -> int:
        stmt = select(func.count()).select_from(self.model)
        return int(db.execute(stmt).scalar_one())

    def list_page(self, db: Session, offset: int, limit: int) -> list[ModelT]:
        stmt = select(self.model).offset(offset).limit(limit)
        return list(db.execute(stmt).scalars().all())
