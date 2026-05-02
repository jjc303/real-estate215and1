from __future__ import annotations

from flask import Flask

from app.core.config import load_config
from app.core.database import init_database
from app.core.exceptions import register_error_handlers
from app.core.logging import setup_logging
from app.modules.admin.router import bp as admin_bp
from app.modules.appointment.router import bp as appointment_bp
from app.modules.auth.router import bp as auth_bp
from app.modules.bill.router import bp as bill_bp
from app.modules.complaint.router import bp as complaint_bp
from app.modules.contract.router import bp as contract_bp
from app.modules.conversation.router import bp as conversation_bp
from app.modules.favorite.router import bp as favorite_bp
from app.modules.house.router import bp as house_bp
from app.modules.news.router import bp as news_bp
from app.modules.notification.router import bp as notification_bp
from app.modules.payment.router import bp as payment_bp
from app.modules.repair.router import bp as repair_bp
from app.modules.statistics.router import bp as statistics_bp
from app.modules.user.router import bp as user_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(user_bp, url_prefix="/api/v1/users")
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(house_bp, url_prefix="/api/v1/houses")
    app.register_blueprint(news_bp, url_prefix="/api/v1/news")
    app.register_blueprint(favorite_bp, url_prefix="/api/v1/favorites")
    app.register_blueprint(appointment_bp, url_prefix="/api/v1/appointments")
    app.register_blueprint(conversation_bp, url_prefix="/api/v1/conversations")
    app.register_blueprint(contract_bp, url_prefix="/api/v1/contracts")
    app.register_blueprint(bill_bp, url_prefix="/api/v1/bills")
    app.register_blueprint(payment_bp, url_prefix="/api/v1/payments")
    app.register_blueprint(repair_bp, url_prefix="/api/v1/repairs")
    app.register_blueprint(complaint_bp, url_prefix="/api/v1/complaints")
    app.register_blueprint(notification_bp, url_prefix="/api/v1/notifications")
    app.register_blueprint(statistics_bp, url_prefix="/api/v1/statistics")
    app.register_blueprint(admin_bp, url_prefix="/api/v1/admin")


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__)

    load_config(app, config_name=config_name)
    setup_logging(app)
    init_database(app)
    register_blueprints(app)
    register_error_handlers(app)

    return app
