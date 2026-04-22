from __future__ import annotations

import os
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[2]
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
    DATABASE_URI = DEFAULT_DATABASE_URI
    DB_ECHO = False
    JSON_AS_ASCII = False
    LOG_LEVEL = "INFO"
    LOG_FILE_PATH = str(DEFAULT_LOG_FILE_PATH)

    @classmethod
    def to_mapping(cls) -> dict[str, object]:
        return {
            "APP_NAME": os.getenv("APP_NAME", cls.APP_NAME),
            "ENV": cls.ENV,
            "DEBUG": _get_bool("DEBUG", cls.DEBUG),
            "TESTING": _get_bool("TESTING", cls.TESTING),
            "SECRET_KEY": os.getenv("SECRET_KEY", cls.SECRET_KEY),
            "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY", cls.JWT_SECRET_KEY),
            "DATABASE_URI": os.getenv("DATABASE_URI", cls.DATABASE_URI),
            "DB_ECHO": _get_bool("DB_ECHO", cls.DB_ECHO),
            "JSON_AS_ASCII": _get_bool("JSON_AS_ASCII", cls.JSON_AS_ASCII),
            "LOG_LEVEL": _get_log_level("LOG_LEVEL", cls.LOG_LEVEL),
            "LOG_FILE_PATH": _get_path("LOG_FILE_PATH", Path(cls.LOG_FILE_PATH)),
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
