from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import sys

from flask import Flask
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from werkzeug.security import generate_password_hash

BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.core.database import Base
from app.core.exceptions import (
    BadRequestException,
    ForbiddenException,
    InternalServerException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from app.modules.auth.model import EmailVerificationCode
from app.modules.auth.repository import EmailVerificationCodeRepository
from app.modules.auth.service import AuthService
from app.modules.user.model import User
from app.modules.user.repository import UserRepository


@pytest.fixture
def app():
    flask_app = Flask(__name__)
    flask_app.config.update(
        JWT_SECRET_KEY="test-jwt-secret",
        JWT_ALGORITHM="HS256",
        JWT_EXPIRE_MINUTES=120,
        SMTP_SERVER="smtp.example.com",
        SMTP_PORT=465,
        SMTP_USER="noreply@example.com",
        SMTP_PASS="secret",
        SMTP_USE_SSL=True,
        SMTP_USE_TLS=False,
        EMAIL_CODE_EXPIRE_MINUTES=5,
        EMAIL_CODE_RESEND_SECONDS=60,
    )
    return flask_app


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    session: Session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def auth_service():
    return AuthService(UserRepository(), EmailVerificationCodeRepository())


def test_send_email_code_register_success(app, db_session, auth_service, monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[tuple[str, str], str] = {}

    def fake_send_verification_email(*, to_email: str, code: str, biz_type: str) -> None:
        captured[(to_email, biz_type)] = code

    monkeypatch.setattr("app.modules.auth.service.send_verification_email", fake_send_verification_email)

    with app.app_context():
        result = auth_service.send_email_code(
            db_session,
            email=" Alice@Example.com ",
            biz_type="register",
        )

    assert result == {"message": "email code sent"}
    assert ("alice@example.com", "register") in captured

    records = db_session.query(EmailVerificationCode).all()
    assert len(records) == 1
    assert records[0].email == "alice@example.com"
    assert records[0].is_used is False


def test_send_email_code_rejects_too_frequent_requests(
    app,
    db_session,
    auth_service,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sent_codes: dict[tuple[str, str], str] = {}

    def fake_send_verification_email(*, to_email: str, code: str, biz_type: str) -> None:
        sent_codes[(to_email, biz_type)] = code

    monkeypatch.setattr("app.modules.auth.service.send_verification_email", fake_send_verification_email)

    with app.app_context():
        auth_service.send_email_code(db_session, email="alice@example.com", biz_type="register")
        with pytest.raises(BadRequestException):
            auth_service.send_email_code(db_session, email="alice@example.com", biz_type="register")


def test_send_email_code_rolls_back_when_mail_send_fails(
    app,
    db_session,
    auth_service,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_send_verification_email(*, to_email: str, code: str, biz_type: str) -> None:
        raise RuntimeError("smtp failed")

    monkeypatch.setattr("app.modules.auth.service.send_verification_email", fake_send_verification_email)

    with app.app_context():
        with pytest.raises(InternalServerException):
            auth_service.send_email_code(db_session, email="alice@example.com", biz_type="register")

    assert db_session.query(EmailVerificationCode).count() == 0


def test_email_register_success_and_code_cannot_be_reused(
    app,
    db_session,
    auth_service,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sent_codes: dict[tuple[str, str], str] = {}

    def fake_send_verification_email(*, to_email: str, code: str, biz_type: str) -> None:
        sent_codes[(to_email, biz_type)] = code

    monkeypatch.setattr("app.modules.auth.service.send_verification_email", fake_send_verification_email)

    with app.app_context():
        auth_service.send_email_code(db_session, email="alice@example.com", biz_type="register")
        code = sent_codes[("alice@example.com", "register")]
        result = auth_service.email_register(
            db_session,
            email="alice@example.com",
            code=code,
            role="tenant",
            real_name="Alice",
        )

        assert result["token"]
        assert result["token_type"] == "Bearer"
        assert result["user"]["email"] == "alice@example.com"
        assert result["user"]["role"] == "tenant"
        assert result["user"]["username"].startswith("user_")

        with pytest.raises(BadRequestException):
            auth_service.email_register(
                db_session,
                email="alice@example.com",
                code=code,
                role="tenant",
            )


def test_email_register_rejects_existing_email(
    app,
    db_session,
    auth_service,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    existing_user = User(
        username="existing_user",
        password="hashed-password",
        role="tenant",
        email="alice@example.com",
        status="active",
    )
    db_session.add(existing_user)
    db_session.commit()

    sent_codes: dict[tuple[str, str], str] = {}

    def fake_send_verification_email(*, to_email: str, code: str, biz_type: str) -> None:
        sent_codes[(to_email, biz_type)] = code

    monkeypatch.setattr("app.modules.auth.service.send_verification_email", fake_send_verification_email)

    with app.app_context():
        with pytest.raises(UserAlreadyExistsException):
            auth_service.send_email_code(db_session, email="alice@example.com", biz_type="register")


def test_email_login_success_for_registered_user(
    app,
    db_session,
    auth_service,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user = User(
        username="user_login",
        password="hashed-password",
        role="tenant",
        email="alice@example.com",
        status="active",
    )
    db_session.add(user)
    db_session.commit()

    sent_codes: dict[tuple[str, str], str] = {}

    def fake_send_verification_email(*, to_email: str, code: str, biz_type: str) -> None:
        sent_codes[(to_email, biz_type)] = code

    monkeypatch.setattr("app.modules.auth.service.send_verification_email", fake_send_verification_email)

    with app.app_context():
        auth_service.send_email_code(db_session, email="alice@example.com", biz_type="login")
        code = sent_codes[("alice@example.com", "login")]
        result = auth_service.email_login(
            db_session,
            email="alice@example.com",
            code=code,
        )

    assert result["token"]
    assert result["token_type"] == "Bearer"
    assert result["user"]["id"] == user.id


def test_email_login_rejects_unregistered_email(
    app,
    db_session,
    auth_service,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_send_verification_email(*, to_email: str, code: str, biz_type: str) -> None:
        raise AssertionError("send_verification_email should not be called")

    monkeypatch.setattr("app.modules.auth.service.send_verification_email", fake_send_verification_email)

    with app.app_context():
        with pytest.raises(UserNotFoundException):
            auth_service.send_email_code(db_session, email="alice@example.com", biz_type="login")


def test_email_login_rejects_inactive_user(
    app,
    db_session,
    auth_service,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user = User(
        username="user_disabled",
        password="hashed-password",
        role="tenant",
        email="alice@example.com",
        status="disabled",
    )
    db_session.add(user)
    db_session.commit()

    def fake_send_verification_email(*, to_email: str, code: str, biz_type: str) -> None:
        raise AssertionError("send_verification_email should not be called")

    monkeypatch.setattr("app.modules.auth.service.send_verification_email", fake_send_verification_email)

    with app.app_context():
        with pytest.raises(ForbiddenException):
            auth_service.send_email_code(db_session, email="alice@example.com", biz_type="login")


def test_email_login_rejects_invalid_code(
    app,
    db_session,
    auth_service,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    user = User(
        username="user_login_bad_code",
        password="hashed-password",
        role="tenant",
        email="alice@example.com",
        status="active",
    )
    db_session.add(user)
    db_session.commit()

    sent_codes: dict[tuple[str, str], str] = {}

    def fake_send_verification_email(*, to_email: str, code: str, biz_type: str) -> None:
        sent_codes[(to_email, biz_type)] = code

    monkeypatch.setattr("app.modules.auth.service.send_verification_email", fake_send_verification_email)

    with app.app_context():
        auth_service.send_email_code(db_session, email="alice@example.com", biz_type="login")
        with pytest.raises(BadRequestException):
            auth_service.email_login(
                db_session,
                email="alice@example.com",
                code="000000",
            )


def test_email_login_rejects_expired_code(app, db_session, auth_service) -> None:
    user = User(
        username="user_login_expired",
        password="hashed-password",
        role="tenant",
        email="alice@example.com",
        status="active",
    )
    db_session.add(user)
    db_session.commit()

    expired_code = EmailVerificationCode(
        email="alice@example.com",
        code_hash=generate_password_hash("123456"),
        biz_type="login",
        expires_at=datetime.utcnow() - timedelta(minutes=1),
        is_used=False,
    )
    db_session.add(expired_code)
    db_session.commit()

    with app.app_context():
        with pytest.raises(BadRequestException):
            auth_service.email_login(db_session, email="alice@example.com", code="123456")
