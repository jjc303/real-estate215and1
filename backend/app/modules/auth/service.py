from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import InvalidCredentialsException, UnauthorizedException
from app.core.security import create_access_token, verify_password
from app.modules.user.repository import UserRepository
from app.modules.user.schema import UserReadSchema


class AuthService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def login(self, db: Session, username: str, password: str) -> dict[str, str]:
        user = self.user_repository.get_by_username(db, username)
        if user is None or not verify_password(password, user.password):
            raise InvalidCredentialsException()

        return {
            "token": create_access_token(user.id),
            "token_type": "Bearer",
        }

    def get_current_user(self, db: Session, current_user_id: int) -> dict[str, object]:
        user = self.user_repository.get_by_id(db, current_user_id)
        if user is None:
            raise UnauthorizedException(message="未登录")

        return UserReadSchema.model_validate(user).model_dump(mode="json")
