from __future__ import annotations

from flask import Flask

from app.core.config import load_config
from app.core.database import init_database
from app.core.exceptions import register_error_handlers
from app.core.logging import setup_logging
from app.modules.auth.router import bp as auth_bp
from app.modules.user.router import bp as user_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(user_bp, url_prefix="/api/v1/users")
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__)

    load_config(app, config_name=config_name)
    setup_logging(app)
    init_database(app)
    register_blueprints(app)
    register_error_handlers(app)

    return app
