from __future__ import annotations

from app.common.enums import HouseStatus
from app.common.base_repository import BaseRepository
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.favorite.model import Favorite
from app.modules.house.model import House


class FavoriteRepository(BaseRepository[Favorite]):
    def __init__(self) -> None:
        super().__init__(Favorite)

    def get_by_user_id_and_house_id(
        self,
        db: Session,
        user_id: int,
        house_id: int,
    ) -> Favorite | None:
        stmt = select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.house_id == house_id,
        )
        return db.execute(stmt).scalar_one_or_none()

    def list_by_user_id(self, db: Session, user_id: int, offset: int, limit: int) -> list[tuple[Favorite, House]]:
        stmt = (
            select(Favorite, House)
            .join(House, House.id == Favorite.house_id)
            .where(
                Favorite.user_id == user_id,
                House.deleted_at.is_(None),
                House.status == HouseStatus.LISTED,
            )
            .order_by(Favorite.created_at.desc(), Favorite.id.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(db.execute(stmt).all())

    def count_by_user_id(self, db: Session, user_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(Favorite)
            .join(House, House.id == Favorite.house_id)
            .where(
                Favorite.user_id == user_id,
                House.deleted_at.is_(None),
                House.status == HouseStatus.LISTED,
            )
        )
        return int(db.execute(stmt).scalar_one())
