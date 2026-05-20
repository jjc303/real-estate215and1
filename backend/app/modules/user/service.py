from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.common.email import normalize_email
from app.common.pagination import build_page_result, get_offset
from app.core.exceptions import UserAlreadyExistsException, UserNotFoundException
from app.core.security import hash_password
from app.modules.user.model import User
from app.modules.user.repository import UserRepository
from app.modules.user.schema import UserCreateSchema, UserReadSchema, UserUpdateSchema


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
            raise UserAlreadyExistsException(message="username already exists")

        normalized_email = normalize_email(data.email)
        if normalized_email is not None and self.user_repository.get_by_email(db, normalized_email) is not None:
            raise UserAlreadyExistsException(message="email already exists")

        user = User(
            username=data.username,
            password=hash_password(data.password),
            role=data.role,
            real_name=data.real_name,
            phone=data.phone,
            email=normalized_email,
            avatar=data.avatar,
            status=data.status,
        )

        try:
            self.user_repository.create(db, user)
            db.commit()
            db.refresh(user)
        except IntegrityError as exc:
            db.rollback()
            raise UserAlreadyExistsException(message="user already exists") from exc
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

    def update_user(self, db: Session, current_user_id: int, data: UserUpdateSchema) -> dict[str, object]:
        user = self.user_repository.get_by_id(db, current_user_id)
        if user is None:
            raise UserNotFoundException()

        normalized_email = normalize_email(data.email)
        if normalized_email is not None:
            existing_email_user = self.user_repository.get_by_email(db, normalized_email)
            if existing_email_user is not None and existing_email_user.id != user.id:
                raise UserAlreadyExistsException(message="email already exists")

        if data.real_name is not None:
            user.real_name = data.real_name
        if data.phone is not None:
            user.phone = data.phone
        if data.email is not None:
            user.email = normalized_email
        if data.avatar is not None:
            user.avatar = data.avatar
        if data.password is not None:
            user.password = hash_password(data.password)

        try:
            db.commit()
            db.refresh(user)
        except IntegrityError as exc:
            db.rollback()
            raise UserAlreadyExistsException(message="user already exists") from exc
        except Exception:
            db.rollback()
            raise

        schema = UserReadSchema.model_validate(user)
        return schema.model_dump(mode="json")
