from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestException, HouseNotFoundException
from app.modules.house.model import House
from app.modules.house.repository import HouseRepository
from app.modules.house.schema import HouseCreateSchema, HouseReadSchema, HouseUpdateSchema


class HouseService:
    def __init__(self, house_repository: HouseRepository) -> None:
        self.house_repository = house_repository

    def create_house(
        self,
        db: Session,
        landlord_id: int,
        data: HouseCreateSchema,
    ) -> dict[str, object]:
        house = House(
            landlord_id=landlord_id,
            title=data.title,
            address=data.address,
            region=data.region,
            community=data.community,
            house_type=data.house_type,
            area=data.area,
            rent=data.rent,
            deposit=data.deposit,
            decoration=data.decoration,
            floor=data.floor,
            orientation=data.orientation,
            description=data.description,
            status="draft",
        )

        try:
            self.house_repository.create(db, house)
            db.commit()
            db.refresh(house)
        except Exception:
            db.rollback()
            raise

        return self._serialize(house)

    def list_houses(
        self,
        db: Session,
        page: int,
        page_size: int,
        mine: bool = False,
        landlord_id: int | None = None,
        region: str | None = None,
        house_type: str | None = None,
        min_rent: Decimal | None = None,
        max_rent: Decimal | None = None,
        keyword: str | None = None,
        min_area: Decimal | None = None,
        max_area: Decimal | None = None,
    ) -> dict[str, object]:
        offset = (page - 1) * page_size

        if mine:
            if landlord_id is None:
                raise BadRequestException(message="mine=true requires current user")
            houses = self.house_repository.list_by_landlord(
                db,
                landlord_id=landlord_id,
                offset=offset,
                limit=page_size,
                region=region,
                house_type=house_type,
                min_rent=min_rent,
                max_rent=max_rent,
                keyword=keyword,
                min_area=min_area,
                max_area=max_area,
            )
            total = self.house_repository.count_by_landlord(
                db,
                landlord_id=landlord_id,
                region=region,
                house_type=house_type,
                min_rent=min_rent,
                max_rent=max_rent,
                keyword=keyword,
                min_area=min_area,
                max_area=max_area,
            )
        else:
            houses = self.house_repository.list_public(
                db,
                offset=offset,
                limit=page_size,
                region=region,
                house_type=house_type,
                min_rent=min_rent,
                max_rent=max_rent,
                keyword=keyword,
                min_area=min_area,
                max_area=max_area,
            )
            total = self.house_repository.count_public(
                db,
                region=region,
                house_type=house_type,
                min_rent=min_rent,
                max_rent=max_rent,
                keyword=keyword,
                min_area=min_area,
                max_area=max_area,
            )

        return {
            "list": [self._serialize(house) for house in houses],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def get_house_detail(
        self,
        db: Session,
        house_id: int,
        current_user_id: int | None = None,
    ) -> dict[str, object]:
        if current_user_id is not None:
            owned_house = self.house_repository.get_by_id_and_landlord_id(
                db,
                house_id=house_id,
                landlord_id=current_user_id,
            )
            if owned_house is not None:
                return self._serialize(owned_house)

        house = self.house_repository.get_by_id(db, house_id)
        if house is None or house.deleted_at is not None or house.status != "listed":
            raise HouseNotFoundException()
        return self._serialize(house)

    def update_house(
        self,
        db: Session,
        house_id: int,
        landlord_id: int,
        data: HouseUpdateSchema,
    ) -> dict[str, object]:
        house = self.house_repository.get_by_id_and_landlord_id(
            db,
            house_id=house_id,
            landlord_id=landlord_id,
        )
        if house is None:
            raise HouseNotFoundException()

        house.title = data.title
        house.address = data.address
        house.region = data.region
        house.community = data.community
        house.house_type = data.house_type
        house.area = data.area
        house.rent = data.rent
        house.deposit = data.deposit
        house.decoration = data.decoration
        house.floor = data.floor
        house.orientation = data.orientation
        house.description = data.description

        try:
            db.commit()
            db.refresh(house)
        except Exception:
            db.rollback()
            raise

        return self._serialize(house)

    def publish_house(self, db: Session, house_id: int, landlord_id: int) -> dict[str, object]:
        house = self.house_repository.get_by_id_and_landlord_id(
            db,
            house_id=house_id,
            landlord_id=landlord_id,
        )
        if house is None:
            raise HouseNotFoundException()
        if house.status not in {"draft", "offline"}:
            raise BadRequestException(message="invalid house status transition")

        house.status = "listed"
        try:
            db.commit()
            db.refresh(house)
        except Exception:
            db.rollback()
            raise
        return self._serialize(house)

    def offline_house(self, db: Session, house_id: int, landlord_id: int) -> dict[str, object]:
        house = self.house_repository.get_by_id_and_landlord_id(
            db,
            house_id=house_id,
            landlord_id=landlord_id,
        )
        if house is None:
            raise HouseNotFoundException()
        if house.status not in {"listed", "draft"}:
            raise BadRequestException(message="invalid house status transition")

        house.status = "offline"
        try:
            db.commit()
            db.refresh(house)
        except Exception:
            db.rollback()
            raise
        return self._serialize(house)

    def delete_house(self, db: Session, house_id: int, landlord_id: int) -> None:
        house = self.house_repository.get_by_id_and_landlord_id(
            db,
            house_id=house_id,
            landlord_id=landlord_id,
        )
        if house is None:
            raise HouseNotFoundException()

        house.status = "offline"
        house.deleted_at = datetime.utcnow()

        try:
            db.commit()
        except Exception:
            db.rollback()
            raise

    def _serialize(self, house: House) -> dict[str, object]:
        return HouseReadSchema.model_validate(house).model_dump(mode="json")
