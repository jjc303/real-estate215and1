from __future__ import annotations

import os
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = BACKEND_DIR.parent
DEFAULT_DATABASE_URI = (
    "mysql+pymysql://rent_user:rent_pass@mysql:3306/rent_db?charset=utf8mb4"
)
DEFAULT_LOG_FILE_PATH = BACKEND_DIR / "logs" / "app.log"
ALLOWED_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_path(name: str, default: Path) -> str:
    value = os.getenv(name)
    if not value:
        return str(default)

    candidate = Path(value)
    if candidate.is_absolute():
        return str(candidate)
    return str(BACKEND_DIR / candidate)


def _get_upload_path(name: str, default: Path) -> str:
    value = os.getenv(name)
    if not value:
        return str(default)

    candidate = Path(value)
    if candidate.is_absolute():
        return str(candidate)
    return str(PROJECT_ROOT / candidate)


def _get_log_level(name: str, default: str) -> str:
    value = os.getenv(name, default).strip().upper()
    if value not in ALLOWED_LOG_LEVELS:
        raise ValueError(
            f"Invalid {name}: {value}. Allowed values: {', '.join(sorted(ALLOWED_LOG_LEVELS))}"
        )
    return value


class BaseConfig:
    APP_NAME = "real-estate215and1"
    ENV = "base"
    DEBUG = False
    TESTING = False
    SECRET_KEY = "dev-secret-key"
    JWT_SECRET_KEY = "dev-jwt-secret-key"
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRE_MINUTES = 120
    DATABASE_URI = DEFAULT_DATABASE_URI
    DB_ECHO = False
    JSON_AS_ASCII = False
    LOG_LEVEL = "INFO"
    LOG_FILE_PATH = str(DEFAULT_LOG_FILE_PATH)
    SMTP_SERVER = ""
    SMTP_PORT = 465
    SMTP_USER = ""
    SMTP_PASS = ""
    SMTP_USE_SSL = False
    SMTP_USE_TLS = False
    EMAIL_CODE_EXPIRE_MINUTES = 5
    EMAIL_CODE_RESEND_SECONDS = 60
    AI_ENGINE_BASE_URL = ""
    AI_ENGINE_API_KEY = ""
    AI_ENGINE_TIMEOUT_SECONDS = 20
    UPLOAD_DIR = str(PROJECT_ROOT / "uploads")
    UPLOAD_URL_PREFIX = "/uploads"
    IMAGE_MAX_BYTES = 5 * 1024 * 1024
    ALLOWED_IMAGE_EXTENSIONS = ("jpg", "jpeg", "png", "webp")
    HOUSE_IMAGE_MAX_COUNT = 9
    USER_AVATAR_MAX_COUNT = 5
    HOUSE_VIDEO_MAX_COUNT = 5
    HOUSE_VIDEO_MAX_BYTES = 200 * 1024 * 1024
    ALLOWED_VIDEO_EXTENSIONS = ("mp4",)

    @classmethod
    def to_mapping(cls) -> dict[str, object]:
        return {
            "APP_NAME": os.getenv("APP_NAME", cls.APP_NAME),
            "ENV": cls.ENV,
            "DEBUG": _get_bool("DEBUG", cls.DEBUG),
            "TESTING": _get_bool("TESTING", cls.TESTING),
            "SECRET_KEY": os.getenv("SECRET_KEY", cls.SECRET_KEY),
            "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY", cls.JWT_SECRET_KEY),
            "JWT_ALGORITHM": os.getenv("JWT_ALGORITHM", cls.JWT_ALGORITHM),
            "JWT_EXPIRE_MINUTES": int(
                os.getenv("JWT_EXPIRE_MINUTES", str(cls.JWT_EXPIRE_MINUTES))
            ),
            "DATABASE_URI": os.getenv("DATABASE_URI", cls.DATABASE_URI),
            "DB_ECHO": _get_bool("DB_ECHO", cls.DB_ECHO),
            "JSON_AS_ASCII": _get_bool("JSON_AS_ASCII", cls.JSON_AS_ASCII),
            "LOG_LEVEL": _get_log_level("LOG_LEVEL", cls.LOG_LEVEL),
            "LOG_FILE_PATH": _get_path("LOG_FILE_PATH", Path(cls.LOG_FILE_PATH)),
            "SMTP_SERVER": os.getenv("SMTP_SERVER", cls.SMTP_SERVER),
            "SMTP_PORT": int(os.getenv("SMTP_PORT", str(cls.SMTP_PORT))),
            "SMTP_USER": os.getenv("SMTP_USER", cls.SMTP_USER),
            "SMTP_PASS": os.getenv("SMTP_PASS", cls.SMTP_PASS),
            "SMTP_USE_SSL": _get_bool("SMTP_USE_SSL", cls.SMTP_USE_SSL),
            "SMTP_USE_TLS": _get_bool("SMTP_USE_TLS", cls.SMTP_USE_TLS),
            "EMAIL_CODE_EXPIRE_MINUTES": int(
                os.getenv("EMAIL_CODE_EXPIRE_MINUTES", str(cls.EMAIL_CODE_EXPIRE_MINUTES))
            ),
            "EMAIL_CODE_RESEND_SECONDS": int(
                os.getenv("EMAIL_CODE_RESEND_SECONDS", str(cls.EMAIL_CODE_RESEND_SECONDS))
            ),
            "AI_ENGINE_BASE_URL": os.getenv("AI_ENGINE_BASE_URL", cls.AI_ENGINE_BASE_URL),
            "AI_ENGINE_API_KEY": os.getenv("AI_ENGINE_API_KEY", cls.AI_ENGINE_API_KEY),
            "AI_ENGINE_TIMEOUT_SECONDS": int(
                os.getenv("AI_ENGINE_TIMEOUT_SECONDS", str(cls.AI_ENGINE_TIMEOUT_SECONDS))
            ),
            "UPLOAD_DIR": _get_upload_path("UPLOAD_DIR", Path(cls.UPLOAD_DIR)),
            "UPLOAD_URL_PREFIX": os.getenv("UPLOAD_URL_PREFIX", cls.UPLOAD_URL_PREFIX),
            "IMAGE_MAX_BYTES": int(os.getenv("IMAGE_MAX_BYTES", str(cls.IMAGE_MAX_BYTES))),
            "ALLOWED_IMAGE_EXTENSIONS": tuple(
                item.strip().lower()
                for item in os.getenv(
                    "ALLOWED_IMAGE_EXTENSIONS",
                    ",".join(cls.ALLOWED_IMAGE_EXTENSIONS),
                ).split(",")
                if item.strip()
            ),
            "HOUSE_IMAGE_MAX_COUNT": int(os.getenv("HOUSE_IMAGE_MAX_COUNT", str(cls.HOUSE_IMAGE_MAX_COUNT))),
            "USER_AVATAR_MAX_COUNT": int(os.getenv("USER_AVATAR_MAX_COUNT", str(cls.USER_AVATAR_MAX_COUNT))),
            "HOUSE_VIDEO_MAX_COUNT": int(os.getenv("HOUSE_VIDEO_MAX_COUNT", str(cls.HOUSE_VIDEO_MAX_COUNT))),
            "HOUSE_VIDEO_MAX_BYTES": int(os.getenv("HOUSE_VIDEO_MAX_BYTES", str(cls.HOUSE_VIDEO_MAX_BYTES))),
            "ALLOWED_VIDEO_EXTENSIONS": tuple(
                item.strip().lower()
                for item in os.getenv(
                    "ALLOWED_VIDEO_EXTENSIONS",
                    ",".join(cls.ALLOWED_VIDEO_EXTENSIONS),
                ).split(",")
                if item.strip()
            ),
        }


class DevelopmentConfig(BaseConfig):
    ENV = "development"
    DEBUG = True


class TestingConfig(BaseConfig):
    ENV = "testing"
    TESTING = True
    LOG_LEVEL = "WARNING"


class ProductionConfig(BaseConfig):
    ENV = "production"


CONFIG_MAP: dict[str, type[BaseConfig]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def load_config(app, config_name: str | None = None) -> None:
    selected = (config_name or os.getenv("APP_ENV") or "development").lower()
    config_class = CONFIG_MAP.get(selected)
    if config_class is None:
        raise ValueError(f"Unsupported config name: {selected}")

    app.config.update(config_class.to_mapping())

    if hasattr(app, "json") and app.json is not None:
        app.json.ensure_ascii = app.config["JSON_AS_ASCII"]
