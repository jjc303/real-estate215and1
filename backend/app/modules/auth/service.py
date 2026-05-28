from __future__ import annotations

from datetime import datetime, timedelta
import secrets

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash, generate_password_hash

from app.common.email import normalize_email, send_verification_email
from app.core.exceptions import (
    AppException,
    BadRequestException,
    ForbiddenException,
    InternalServerException,
    InvalidCredentialsException,
    UnauthorizedException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from app.core.security import create_access_token, hash_password, verify_password
from app.modules.auth.model import EmailVerificationCode
from app.modules.auth.repository import EmailVerificationCodeRepository
from app.modules.user.model import User
from app.modules.user.repository import UserRepository
from app.modules.user.schema import UserReadSchema


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        email_verification_code_repository: EmailVerificationCodeRepository,
    ) -> None:
        self.user_repository = user_repository
        self.email_verification_code_repository = email_verification_code_repository

    def login(self, db: Session, username: str, password: str) -> dict[str, str]:
        user = self.user_repository.get_by_username(db, username)
        if user is None or not verify_password(password, user.password):
            raise InvalidCredentialsException(message="invalid credentials")

        return {
            "token": create_access_token(user.id),
            "token_type": "Bearer",
        }

    def get_current_user(self, db: Session, current_user_id: int) -> dict[str, object]:
        user = self.user_repository.get_by_id(db, current_user_id)
        if user is None:
            raise UnauthorizedException(message="unauthorized")

        return UserReadSchema.model_validate(user).model_dump(mode="json")

    def send_email_code(self, db: Session, *, email: str, biz_type: str) -> dict[str, str]:
        normalized_email = self._require_normalized_email(email)
        now = self._now()
        resend_seconds = int(self._config_value("EMAIL_CODE_RESEND_SECONDS", 60))
        expire_minutes = int(self._config_value("EMAIL_CODE_EXPIRE_MINUTES", 5))

        try:
            existing_user = self.user_repository.get_by_email(db, normalized_email)
            if biz_type == "register":
                if existing_user is not None:
                    raise UserAlreadyExistsException(message="email already exists")
            elif biz_type == "login":
                if existing_user is None:
                    raise UserNotFoundException()
                if existing_user.status != "active":
                    raise ForbiddenException(message="user status is not allowed")
            else:
                raise BadRequestException(message="bad request")

            latest_record = self.email_verification_code_repository.get_latest_by_email_and_biz_type(
                db,
                normalized_email,
                biz_type,
            )
            if latest_record is not None:
                delta_seconds = (now - latest_record.created_at).total_seconds()
                # MySQL server_default(now()) may use a different timezone than app runtime.
                # Only apply resend throttling when the delta is non-negative and within window.
                if 0 <= delta_seconds < resend_seconds:
                    raise BadRequestException(message="email code sent too frequently")

            code = self._generate_email_code()
            record = EmailVerificationCode(
                email=normalized_email,
                code_hash=generate_password_hash(code),
                biz_type=biz_type,
                expires_at=now + timedelta(minutes=expire_minutes),
                is_used=False,
            )
            self.email_verification_code_repository.create(db, record)
            db.flush()
            try:
                send_verification_email(to_email=normalized_email, code=code, biz_type=biz_type)
            except Exception as exc:
                raise InternalServerException(message="internal server error") from exc
            db.commit()
        except AppException:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise

        return {"message": "email code sent"}

    def email_register(
        self,
        db: Session,
        *,
        email: str,
        code: str,
        role: str,
        real_name: str | None = None,
        phone: str | None = None,
        password: str | None = None,
    ) -> dict[str, object]:
        normalized_email = self._require_normalized_email(email)
        now = self._now()

        try:
            record = self.email_verification_code_repository.get_latest_unexpired_unused(
                db,
                normalized_email,
                "register",
                now,
            )
            if record is None or not check_password_hash(record.code_hash, code):
                raise BadRequestException(message="invalid email verification code")

            if self.user_repository.get_by_email(db, normalized_email) is not None:
                raise UserAlreadyExistsException(message="email already exists")

            username = self._generate_unique_username(db)
            password_hash = hash_password(password) if password is not None else hash_password(secrets.token_urlsafe(24))
            user = User(
                username=username,
                password=password_hash,
                role=role,
                real_name=real_name,
                phone=phone,
                email=normalized_email,
                status="active",
            )
            self.user_repository.create(db, user)
            self.email_verification_code_repository.mark_used(record)
            db.flush()
            token = create_access_token(user.id)
            db.commit()
        except AppException:
            db.rollback()
            raise
        except IntegrityError as exc:
            db.rollback()
            raise UserAlreadyExistsException(message="user already exists") from exc
        except Exception:
            db.rollback()
            raise

        return {
            "token": token,
            "token_type": "Bearer",
            "user": self._serialize_auth_user(user),
        }

    def email_login(
        self,
        db: Session,
        *,
        email: str,
        code: str,
    ) -> dict[str, object]:
        normalized_email = self._require_normalized_email(email)
        now = self._now()

        try:
            user = self.user_repository.get_by_email(db, normalized_email)
            if user is None:
                raise UserNotFoundException()
            if user.status != "active":
                raise ForbiddenException(message="user status is not allowed")

            record = self.email_verification_code_repository.get_latest_unexpired_unused(
                db,
                normalized_email,
                "login",
                now,
            )
            if record is None or not check_password_hash(record.code_hash, code):
                raise BadRequestException(message="invalid email verification code")

            self.email_verification_code_repository.mark_used(record)
            db.flush()
            token = create_access_token(user.id)
            db.commit()
        except AppException:
            db.rollback()
            raise
        except Exception:
            db.rollback()
            raise

        return {
            "token": token,
            "token_type": "Bearer",
            "user": self._serialize_auth_user(user),
        }

    def _require_normalized_email(self, email: str | None) -> str:
        normalized_email = normalize_email(email)
        if normalized_email is None:
            raise BadRequestException(message="bad request")
        return normalized_email

    def _generate_unique_username(self, db: Session) -> str:
        for _ in range(5):
            username = f"user_{secrets.token_hex(4)}"
            if self.user_repository.get_by_username(db, username) is None:
                return username

        while True:
            username = f"user_{secrets.token_hex(8)}"
            if self.user_repository.get_by_username(db, username) is None:
                return username

    def _generate_email_code(self) -> str:
        return f"{secrets.randbelow(1_000_000):06d}"

    def _serialize_auth_user(self, user: User) -> dict[str, object]:
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "status": user.status,
        }

    def _config_value(self, key: str, default: object) -> object:
        from flask import current_app

        return current_app.config.get(key, default)

    def _now(self) -> datetime:
        return datetime.utcnow()
