from __future__ import annotations

from app.modules.admin.repository import AdminRepository
from app.modules.appointment.repository import AppointmentRepository
from app.modules.auth.repository import EmailVerificationCodeRepository
from app.modules.bill.repository import BillRepository
from app.modules.complaint.repository import ComplaintRepository
from app.modules.contract.repository import ContractRepository
from app.modules.conversation.repository import ConversationRepository, MessageRepository
from app.modules.favorite.repository import FavoriteRepository
from app.modules.house.repository import HouseRepository
from app.modules.house_image.repository import HouseImageRepository
from app.modules.house_video.repository import HouseVideoRepository
from app.modules.news.repository import NewsRepository
from app.modules.notification.repository import NotificationRepository
from app.modules.operation_log.repository import OperationLogRepository
from app.modules.payment.repository import PaymentRepository
from app.modules.repair.repository import RepairRepository
from app.modules.statistics.repository import StatisticsRepository
from app.modules.user.repository import UserRepository
from app.modules.user_avatar.repository import UserAvatarRepository


_user_repository = UserRepository()
_house_repository = HouseRepository()
_house_image_repository = HouseImageRepository()
_house_video_repository = HouseVideoRepository()
_favorite_repository = FavoriteRepository()
_appointment_repository = AppointmentRepository()
_email_verification_code_repository = EmailVerificationCodeRepository()
_conversation_repository = ConversationRepository()
_message_repository = MessageRepository()
_news_repository = NewsRepository()
_contract_repository = ContractRepository()
_bill_repository = BillRepository()
_payment_repository = PaymentRepository()
_repair_repository = RepairRepository()
_complaint_repository = ComplaintRepository()
_notification_repository = NotificationRepository()
_operation_log_repository = OperationLogRepository()
_statistics_repository = StatisticsRepository()
_admin_repository = AdminRepository()
_user_avatar_repository = UserAvatarRepository()


def get_user_repository() -> UserRepository:
    return _user_repository


def get_house_repository() -> HouseRepository:
    return _house_repository


def get_house_image_repository() -> HouseImageRepository:
    return _house_image_repository


def get_house_video_repository() -> HouseVideoRepository:
    return _house_video_repository


def get_favorite_repository() -> FavoriteRepository:
    return _favorite_repository


def get_appointment_repository() -> AppointmentRepository:
    return _appointment_repository


def get_email_verification_code_repository() -> EmailVerificationCodeRepository:
    return _email_verification_code_repository


def get_conversation_repository() -> ConversationRepository:
    return _conversation_repository


def get_message_repository() -> MessageRepository:
    return _message_repository


def get_news_repository() -> NewsRepository:
    return _news_repository


def get_contract_repository() -> ContractRepository:
    return _contract_repository


def get_bill_repository() -> BillRepository:
    return _bill_repository


def get_payment_repository() -> PaymentRepository:
    return _payment_repository


def get_repair_repository() -> RepairRepository:
    return _repair_repository


def get_complaint_repository() -> ComplaintRepository:
    return _complaint_repository


def get_notification_repository() -> NotificationRepository:
    return _notification_repository


def get_operation_log_repository() -> OperationLogRepository:
    return _operation_log_repository


def get_statistics_repository() -> StatisticsRepository:
    return _statistics_repository


def get_admin_repository() -> AdminRepository:
    return _admin_repository


def get_user_avatar_repository() -> UserAvatarRepository:
    return _user_avatar_repository
