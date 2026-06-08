from __future__ import annotations

from flask import current_app
from sqlalchemy.orm import Session

from app.common.file_upload import save_video_file
from app.core.exceptions import BadRequestException, ForbiddenException, HouseNotFoundException, NotFoundException
from app.modules.house.repository import HouseRepository
from app.modules.house_video.model import HouseVideo
from app.modules.house_video.repository import HouseVideoRepository
from app.modules.house_video.schema import HouseVideoReadSchema


class HouseVideoService:
    def __init__(self, house_repository: HouseRepository, house_video_repository: HouseVideoRepository) -> None:
        self.house_repository = house_repository
        self.house_video_repository = house_video_repository

    def upload_video(
        self,
        db: Session,
        *,
        current_user_id: int,
        house_id: int,
        file,
        duration: int | None,
    ) -> dict[str, object]:
        house = self.house_repository.get_by_id_and_landlord_id(db, house_id=house_id, landlord_id=current_user_id)
        if house is None:
            raise HouseNotFoundException()

        current_count = self.house_video_repository.count_active_by_house_id(db, house_id)
        max_count = int(current_app.config["HOUSE_VIDEO_MAX_COUNT"])
        if current_count >= max_count:
            raise BadRequestException(message="house video count limit exceeded")

        url, object_key, size_bytes = save_video_file(
            file,
            upload_root=str(current_app.config["UPLOAD_DIR"]),
            relative_dir=f"houses/{house_id}/videos",
            url_prefix=str(current_app.config["UPLOAD_URL_PREFIX"]),
            max_bytes=int(current_app.config["HOUSE_VIDEO_MAX_BYTES"]),
            allowed_extensions=set(current_app.config["ALLOWED_VIDEO_EXTENSIONS"]),
        )

        video = HouseVideo(
            house_id=house_id,
            url=url,
            object_key=object_key,
            mime_type=file.mimetype or "application/octet-stream",
            size_bytes=size_bytes,
            duration=duration,
            status="active",
        )
        try:
            self.house_video_repository.create(db, video)
            db.commit()
            db.refresh(video)
        except Exception:
            db.rollback()
            raise
        return HouseVideoReadSchema.model_validate(video).model_dump(mode="json")

    def list_videos(self, db: Session, *, house_id: int, current_user_id: int | None) -> list[dict[str, object]]:
        self._ensure_house_visible(db, house_id=house_id, current_user_id=current_user_id)
        videos = self.house_video_repository.list_active_by_house_id(db, house_id=house_id)
        return [HouseVideoReadSchema.model_validate(v).model_dump(mode="json") for v in videos]

    def delete_video(self, db: Session, *, current_user_id: int, house_id: int, video_id: int) -> None:
        house = self.house_repository.get_by_id_and_landlord_id(db, house_id=house_id, landlord_id=current_user_id)
        if house is None:
            raise HouseNotFoundException()

        video = self.house_video_repository.get_active_by_id_and_house_id(db, video_id=video_id, house_id=house_id)
        if video is None:
            raise NotFoundException(message="house video not found")

        video.status = "deleted"
        try:
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
        if house.status not in {"listed", "rented", "maintenance"}:
            raise ForbiddenException()
