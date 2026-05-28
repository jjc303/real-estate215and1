from __future__ import annotations

from flask import current_app
from sqlalchemy.orm import Session

from app.common.enums import HouseStatus
from app.common.file_upload import save_image_file
from app.core.exceptions import BadRequestException, ForbiddenException, HouseNotFoundException, NotFoundException
from app.modules.house.repository import HouseRepository
from app.modules.house_image.model import HouseImage
from app.modules.house_image.repository import HouseImageRepository
from app.modules.house_image.schema import HouseImageReadSchema, HouseImageUpdateSchema


class HouseImageService:
    def __init__(self, house_repository: HouseRepository, house_image_repository: HouseImageRepository) -> None:
        self.house_repository = house_repository
        self.house_image_repository = house_image_repository

    def upload_image(
        self,
        db: Session,
        *,
        current_user_id: int,
        house_id: int,
        file,
        sort_order: int | None,
        is_cover: bool | None,
    ) -> dict[str, object]:
        house = self.house_repository.get_by_id_and_landlord_id(db, house_id=house_id, landlord_id=current_user_id)
        if house is None:
            raise HouseNotFoundException()

        current_count = self.house_image_repository.count_active_by_house_id(db, house_id)
        max_count = int(current_app.config["HOUSE_IMAGE_MAX_COUNT"])
        if current_count >= max_count:
            raise BadRequestException(message="house image count limit exceeded")

        url, object_key, size_bytes = save_image_file(
            file,
            upload_root=str(current_app.config["UPLOAD_DIR"]),
            relative_dir=f"houses/{house_id}",
            url_prefix=str(current_app.config["UPLOAD_URL_PREFIX"]),
            max_bytes=int(current_app.config["IMAGE_MAX_BYTES"]),
            allowed_extensions=set(current_app.config["ALLOWED_IMAGE_EXTENSIONS"]),
        )

        set_cover = bool(is_cover) if is_cover is not None else current_count == 0
        image = HouseImage(
            house_id=house_id,
            url=url,
            object_key=object_key,
            mime_type=file.mimetype or "application/octet-stream",
            size_bytes=size_bytes,
            width=None,
            height=None,
            sort_order=sort_order if sort_order is not None else current_count,
            is_cover=set_cover,
            status="active",
        )
        try:
            if set_cover:
                self.house_image_repository.clear_cover_flags(db, house_id)
            self.house_image_repository.create(db, image)
            db.commit()
            db.refresh(image)
        except Exception:
            db.rollback()
            raise
        return HouseImageReadSchema.model_validate(image).model_dump(mode="json")

    def list_images(self, db: Session, *, house_id: int, current_user_id: int | None) -> list[dict[str, object]]:
        self._ensure_house_visible(db, house_id=house_id, current_user_id=current_user_id)
        images = self.house_image_repository.list_active_by_house_id(db, house_id=house_id)
        return [HouseImageReadSchema.model_validate(image).model_dump(mode="json") for image in images]

    def update_image(
        self,
        db: Session,
        *,
        current_user_id: int,
        house_id: int,
        image_id: int,
        data: HouseImageUpdateSchema,
    ) -> dict[str, object]:
        house = self.house_repository.get_by_id_and_landlord_id(db, house_id=house_id, landlord_id=current_user_id)
        if house is None:
            raise HouseNotFoundException()

        image = self.house_image_repository.get_active_by_id_and_house_id(db, image_id=image_id, house_id=house_id)
        if image is None:
            raise NotFoundException(message="house image not found")

        if data.sort_order is not None:
            image.sort_order = data.sort_order
        if data.is_cover is True:
            self.house_image_repository.clear_cover_flags(db, house_id)
            image.is_cover = True
        elif data.is_cover is False:
            image.is_cover = False

        try:
            db.commit()
            db.refresh(image)
        except Exception:
            db.rollback()
            raise
        return HouseImageReadSchema.model_validate(image).model_dump(mode="json")

    def delete_image(self, db: Session, *, current_user_id: int, house_id: int, image_id: int) -> None:
        house = self.house_repository.get_by_id_and_landlord_id(db, house_id=house_id, landlord_id=current_user_id)
        if house is None:
            raise HouseNotFoundException()

        image = self.house_image_repository.get_active_by_id_and_house_id(db, image_id=image_id, house_id=house_id)
        if image is None:
            raise NotFoundException(message="house image not found")

        was_cover = image.is_cover
        image.status = "deleted"
        image.is_cover = False
        try:
            if was_cover:
                remaining = self.house_image_repository.list_active_by_house_id(db, house_id=house_id)
                remaining = [item for item in remaining if item.id != image.id]
                if remaining:
                    remaining[0].is_cover = True
            db.commit()
        except Exception:
            db.rollback()
            raise

    def _ensure_house_visible(self, db: Session, *, house_id: int, current_user_id: int | None) -> None:
        if current_user_id is not None:
            owned = self.house_repository.get_by_id_and_landlord_id(db, house_id=house_id, landlord_id=current_user_id)
            if owned is not None:
                return

        house = self.house_repository.get_by_id(db, house_id)
        if house is None or house.deleted_at is not None:
            raise HouseNotFoundException()
        if house.status != HouseStatus.LISTED:
            raise ForbiddenException()
