from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.common.base_repository import BaseRepository
from app.modules.news.model import News


class NewsRepository(BaseRepository[News]):
    def __init__(self) -> None:
        super().__init__(News)

    def list_all(
        self,
        db: Session,
        offset: int,
        limit: int,
        status: str | None = None,
    ) -> list[News]:
        stmt = select(News)
        if status is not None:
            stmt = stmt.where(News.status == status)
        stmt = stmt.order_by(News.created_at.desc(), News.id.desc()).offset(offset).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def count_all(self, db: Session, status: str | None = None) -> int:
        stmt = select(func.count()).select_from(News)
        if status is not None:
            stmt = stmt.where(News.status == status)
        return int(db.execute(stmt).scalar_one())

    def list_published(self, db: Session, offset: int, limit: int) -> list[News]:
        stmt = (
            select(News)
            .where(News.status == "published")
            .order_by(News.created_at.desc(), News.id.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(db.execute(stmt).scalars().all())

    def count_published(self, db: Session) -> int:
        stmt = select(func.count()).select_from(News).where(News.status == "published")
        return int(db.execute(stmt).scalar_one())
