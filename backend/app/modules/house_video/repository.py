from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.common.base_repository import BaseRepository
from app.modules.house_video.model import HouseVideo


class HouseVideoRepository(BaseRepository[HouseVideo]):
    def __init__(self) -> None:
        super().__init__(HouseVideo)

    def list_active_by_house_id(self, db: Session, house_id: int) -> list[HouseVideo]:
        stmt = (
            select(HouseVideo)
            .where(HouseVideo.house_id == house_id, HouseVideo.status == "active")
            .order_by(HouseVideo.id.asc())
        )
        return list(db.execute(stmt).scalars().all())

    def count_active_by_house_id(self, db: Session, house_id: int) -> int:
        stmt = select(func.count()).select_from(HouseVideo).where(
            HouseVideo.house_id == house_id,
            HouseVideo.status == "active",
        )
        return int(db.execute(stmt).scalar_one())

    def get_active_by_id_and_house_id(self, db: Session, video_id: int, house_id: int) -> HouseVideo | None:
        stmt = select(HouseVideo).where(
            HouseVideo.id == video_id,
            HouseVideo.house_id == house_id,
            HouseVideo.status == "active",
        )
        return db.execute(stmt).scalar_one_or_none()
