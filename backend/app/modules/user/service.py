from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.common.pagination import build_page_result, get_offset
from app.core.exceptions import ConflictException, UserNotFoundException
from app.core.security import hash_password
from app.modules.user.model import User
from app.modules.user.repository import UserRepository
from app.modules.user.schema import UserCreateSchema, UserReadSchema


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def get_user_by_id(self, db: Session, user_id: int) -> dict[str, object]:
        user = self.user_repository.get_by_id(db, user_id)
        if user is None:
            raise UserNotFoundException()

        schema = UserReadSchema.model_validate(user)
        return schema.model_dump(mode="json")

    def create_user(self, db: Session, data: UserCreateSchema) -> dict[str, object]:
        if self.user_repository.get_by_username(db, data.username) is not None:
            raise ConflictException(message="username already exists")

        user = User(
            username=data.username,
            password=hash_password(data.password),
            role=data.role,
            real_name=data.real_name,
            phone=data.phone,
            email=data.email,
            avatar=data.avatar,
            status=data.status,
        )

        try:
            self.user_repository.create(db, user)
            db.commit()
            db.refresh(user)
        except IntegrityError as exc:
            db.rollback()
            raise ConflictException(message="username already exists") from exc
        except Exception:
            db.rollback()
            raise

        schema = UserReadSchema.model_validate(user)
        return schema.model_dump(mode="json")

    def list_users(self, db: Session, page: int, page_size: int) -> dict[str, object]:
        offset = get_offset(page, page_size)
        users = self.user_repository.list_users(db, offset=offset, limit=page_size)
        total = self.user_repository.count_users(db)
        items = [UserReadSchema.model_validate(user).model_dump(mode="json") for user in users]
        return build_page_result(items=items, total=total, page=page, page_size=page_size)
