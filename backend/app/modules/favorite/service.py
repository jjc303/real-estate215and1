from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.common.enums import HouseStatus
from app.common.pagination import build_page_result, get_offset
from app.core.exceptions import ConflictException, FavoriteNotFoundException, HouseNotFoundException
from app.modules.favorite.model import Favorite
from app.modules.favorite.repository import FavoriteRepository
from app.modules.favorite.schema import FavoriteHouseSummarySchema, FavoriteReadSchema
from app.modules.house.model import House
from app.modules.house.repository import HouseRepository


class FavoriteService:
    def __init__(
        self,
        favorite_repository: FavoriteRepository,
        house_repository: HouseRepository,
    ) -> None:
        self.favorite_repository = favorite_repository
        self.house_repository = house_repository

    def add_favorite(self, db: Session, current_user_id: int, house_id: int) -> dict[str, object]:
        house = self.house_repository.get_by_id(db, house_id)
        if house is None or house.deleted_at is not None or house.status != HouseStatus.LISTED:
            raise HouseNotFoundException()

        if self.favorite_repository.get_by_user_id_and_house_id(db, current_user_id, house_id) is not None:
            raise ConflictException(message="favorite already exists")

        favorite = Favorite(user_id=current_user_id, house_id=house_id)
        try:
            self.favorite_repository.create(db, favorite)
            db.commit()
            db.refresh(favorite)
        except IntegrityError as exc:
            db.rollback()
            raise ConflictException(message="favorite already exists") from exc
        except Exception:
            db.rollback()
            raise

        return self._serialize(favorite, house)

    def list_favorites(self, db: Session, current_user_id: int, page: int, page_size: int) -> dict[str, object]:
        offset = get_offset(page, page_size)
        rows = self.favorite_repository.list_by_user_id(db, current_user_id, offset=offset, limit=page_size)
        total = self.favorite_repository.count_by_user_id(db, current_user_id)
        return build_page_result(
            items=[self._serialize(favorite, house) for favorite, house in rows],
            total=total,
            page=page,
            page_size=page_size,
        )

    def remove_favorite(self, db: Session, current_user_id: int, house_id: int) -> None:
        favorite = self.favorite_repository.get_by_user_id_and_house_id(db, current_user_id, house_id)
        if favorite is None:
            raise FavoriteNotFoundException()

        try:
            self.favorite_repository.delete(db, favorite)
            db.commit()
        except Exception:
            db.rollback()
            raise

    def _serialize(self, favorite: Favorite, house: House) -> dict[str, object]:
        house_data = FavoriteHouseSummarySchema.model_validate(house)
        return FavoriteReadSchema(
            house_id=favorite.house_id,
            favorite_created_at=favorite.created_at,
            house=house_data,
        ).model_dump(mode="json")
