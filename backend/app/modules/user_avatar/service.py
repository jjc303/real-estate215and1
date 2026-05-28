from __future__ import annotations

from flask import current_app
from sqlalchemy.orm import Session

from app.common.file_upload import save_image_file
from app.common.pagination import build_page_result, get_offset
from app.core.exceptions import BadRequestException, UserNotFoundException
from app.modules.user.repository import UserRepository
from app.modules.user_avatar.model import UserAvatar
from app.modules.user_avatar.repository import UserAvatarRepository
from app.modules.user_avatar.schema import UserAvatarReadSchema


class UserAvatarService:
    def __init__(self, user_repository: UserRepository, user_avatar_repository: UserAvatarRepository) -> None:
        self.user_repository = user_repository
        self.user_avatar_repository = user_avatar_repository

    def upload_avatar(self, db: Session, *, current_user_id: int, file) -> dict[str, object]:
        user = self.user_repository.get_by_id(db, current_user_id)
        if user is None:
            raise UserNotFoundException()

        current_count = self.user_avatar_repository.count_active_by_user_id(db, current_user_id)
        max_count = int(current_app.config["USER_AVATAR_MAX_COUNT"])
        if current_count >= max_count:
            raise BadRequestException(message="avatar count limit exceeded")

        url, object_key, size_bytes = save_image_file(
            file,
            upload_root=str(current_app.config["UPLOAD_DIR"]),
            relative_dir=f"avatars/{current_user_id}",
            url_prefix=str(current_app.config["UPLOAD_URL_PREFIX"]),
            max_bytes=int(current_app.config["IMAGE_MAX_BYTES"]),
            allowed_extensions=set(current_app.config["ALLOWED_IMAGE_EXTENSIONS"]),
        )
        avatar = UserAvatar(
            user_id=current_user_id,
            url=url,
            object_key=object_key,
            mime_type=file.mimetype or "application/octet-stream",
            size_bytes=size_bytes,
            width=None,
            height=None,
            is_current=True,
            status="active",
        )
        try:
            self.user_avatar_repository.clear_current_flags(db, current_user_id)
            self.user_avatar_repository.create(db, avatar)
            db.commit()
            db.refresh(avatar)
        except Exception:
            db.rollback()
            raise
        return UserAvatarReadSchema.model_validate(avatar).model_dump(mode="json")

    def get_current_avatar(self, db: Session, *, current_user_id: int) -> dict[str, object] | None:
        user = self.user_repository.get_by_id(db, current_user_id)
        if user is None:
            raise UserNotFoundException()
        avatar = self.user_avatar_repository.get_current_by_user_id(db, current_user_id)
        if avatar is None:
            return None
        return UserAvatarReadSchema.model_validate(avatar).model_dump(mode="json")

    def list_avatars(self, db: Session, *, current_user_id: int, page: int, page_size: int) -> dict[str, object]:
        user = self.user_repository.get_by_id(db, current_user_id)
        if user is None:
            raise UserNotFoundException()
        offset = get_offset(page, page_size)
        items = self.user_avatar_repository.list_active_by_user_id(db, current_user_id, offset=offset, limit=page_size)
        total = self.user_avatar_repository.count_active_by_user_id(db, current_user_id)
        serialized = [UserAvatarReadSchema.model_validate(item).model_dump(mode="json") for item in items]
        return build_page_result(items=serialized, total=total, page=page, page_size=page_size)

