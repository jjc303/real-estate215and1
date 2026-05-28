from __future__ import annotations

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.common.base_repository import BaseRepository
from app.modules.house_image.model import HouseImage


class HouseImageRepository(BaseRepository[HouseImage]):
    def __init__(self) -> None:
        super().__init__(HouseImage)

    def list_active_by_house_id(self, db: Session, house_id: int) -> list[HouseImage]:
        stmt = (
            select(HouseImage)
            .where(HouseImage.house_id == house_id, HouseImage.status == "active")
            .order_by(HouseImage.sort_order.asc(), HouseImage.id.asc())
        )
        return list(db.execute(stmt).scalars().all())

    def count_active_by_house_id(self, db: Session, house_id: int) -> int:
        stmt = select(func.count()).select_from(HouseImage).where(
            HouseImage.house_id == house_id,
            HouseImage.status == "active",
        )
        return int(db.execute(stmt).scalar_one())

    def get_active_by_id_and_house_id(self, db: Session, image_id: int, house_id: int) -> HouseImage | None:
        stmt = select(HouseImage).where(
            HouseImage.id == image_id,
            HouseImage.house_id == house_id,
            HouseImage.status == "active",
        )
        return db.execute(stmt).scalar_one_or_none()

    def clear_cover_flags(self, db: Session, house_id: int) -> None:
        stmt = (
            update(HouseImage)
            .where(HouseImage.house_id == house_id, HouseImage.status == "active", HouseImage.is_cover.is_(True))
            .values(is_cover=False)
        )
        db.execute(stmt)

