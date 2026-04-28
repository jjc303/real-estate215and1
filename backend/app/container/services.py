from __future__ import annotations

from app.container.repositories import (
    get_appointment_repository,
    get_bill_repository,
    get_contract_repository,
    get_conversation_repository,
    get_favorite_repository,
    get_house_repository,
    get_message_repository,
    get_user_repository,
)
from app.modules.appointment.service import AppointmentService
from app.modules.auth.service import AuthService
from app.modules.bill.service import BillService
from app.modules.contract.service import ContractService
from app.modules.conversation.service import ConversationService
from app.modules.favorite.service import FavoriteService
from app.modules.house.service import HouseService
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
_contract_service = ContractService(
    get_contract_repository(),
    get_appointment_repository(),
    get_house_repository(),
)
_bill_service = BillService(
    get_bill_repository(),
    get_contract_repository(),
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


def get_contract_service() -> ContractService:
    return _contract_service


def get_bill_service() -> BillService:
    return _bill_service
