from __future__ import annotations

from app.container.repositories import (
    get_admin_repository,
    get_appointment_repository,
    get_bill_repository,
    get_complaint_repository,
    get_contract_repository,
    get_conversation_repository,
    get_favorite_repository,
    get_house_repository,
    get_message_repository,
    get_news_repository,
    get_notification_repository,
    get_operation_log_repository,
    get_payment_repository,
    get_repair_repository,
    get_statistics_repository,
    get_user_repository,
)
from app.modules.admin.service import AdminService
from app.modules.appointment.service import AppointmentService
from app.modules.auth.service import AuthService
from app.modules.bill.service import BillService
from app.modules.complaint.service import ComplaintService
from app.modules.contract.service import ContractService
from app.modules.conversation.service import ConversationService
from app.modules.favorite.service import FavoriteService
from app.modules.house.service import HouseService
from app.modules.news.service import NewsService
from app.modules.notification.service import NotificationService
from app.modules.operation_log.service import OperationLogService
from app.modules.payment.service import PaymentService
from app.modules.repair.service import RepairService
from app.modules.statistics.service import StatisticsService
from app.modules.user.service import UserService


_user_service = UserService(get_user_repository())
_auth_service = AuthService(get_user_repository())
_house_service = HouseService(get_house_repository())
_favorite_service = FavoriteService(get_favorite_repository(), get_house_repository())
_appointment_service = AppointmentService(get_appointment_repository(), get_house_repository())
_conversation_service = ConversationService(
    get_conversation_repository(),
    get_message_repository(),
    get_house_repository(),
)
_notification_service = NotificationService(
    get_notification_repository(),
    get_user_repository(),
)
_operation_log_service = OperationLogService(
    get_operation_log_repository(),
    get_user_repository(),
)
_news_service = NewsService(
    get_news_repository(),
    get_user_repository(),
    _notification_service,
    _operation_log_service,
)
_contract_service = ContractService(
    get_contract_repository(),
    get_appointment_repository(),
    get_house_repository(),
    _notification_service,
    _operation_log_service,
)
_bill_service = BillService(
    get_bill_repository(),
    get_contract_repository(),
    _notification_service,
    _operation_log_service,
)
_payment_service = PaymentService(
    get_payment_repository(),
    get_bill_repository(),
    _notification_service,
    _operation_log_service,
)
_repair_service = RepairService(
    get_repair_repository(),
    get_contract_repository(),
    get_user_repository(),
    _notification_service,
    _operation_log_service,
)
_complaint_service = ComplaintService(
    get_complaint_repository(),
    get_contract_repository(),
    get_user_repository(),
    _notification_service,
    _operation_log_service,
)
_statistics_service = StatisticsService(
    get_statistics_repository(),
    get_user_repository(),
)
_admin_service = AdminService(
    get_admin_repository(),
    get_user_repository(),
    _repair_service,
    _complaint_service,
    _notification_service,
    _operation_log_service,
)


def get_user_service() -> UserService:
    return _user_service


def get_auth_service() -> AuthService:
    return _auth_service


def get_house_service() -> HouseService:
    return _house_service


def get_favorite_service() -> FavoriteService:
    return _favorite_service


def get_appointment_service() -> AppointmentService:
    return _appointment_service


def get_conversation_service() -> ConversationService:
    return _conversation_service


def get_news_service() -> NewsService:
    return _news_service


def get_contract_service() -> ContractService:
    return _contract_service


def get_bill_service() -> BillService:
    return _bill_service


def get_payment_service() -> PaymentService:
    return _payment_service


def get_repair_service() -> RepairService:
    return _repair_service


def get_complaint_service() -> ComplaintService:
    return _complaint_service


def get_notification_service() -> NotificationService:
    return _notification_service


def get_operation_log_service() -> OperationLogService:
    return _operation_log_service


def get_statistics_service() -> StatisticsService:
    return _statistics_service


def get_admin_service() -> AdminService:
    return _admin_service
