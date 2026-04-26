from __future__ import annotations

from app.modules.appointment.repository import AppointmentRepository
from app.modules.contract.repository import ContractRepository
from app.modules.conversation.repository import ConversationRepository, MessageRepository
from app.modules.favorite.repository import FavoriteRepository
from app.modules.house.repository import HouseRepository
from app.modules.user.repository import UserRepository


_user_repository = UserRepository()
_house_repository = HouseRepository()
_favorite_repository = FavoriteRepository()
_appointment_repository = AppointmentRepository()
_conversation_repository = ConversationRepository()
_message_repository = MessageRepository()
_contract_repository = ContractRepository()


def get_user_repository() -> UserRepository:
    return _user_repository


def get_house_repository() -> HouseRepository:
    return _house_repository


def get_favorite_repository() -> FavoriteRepository:
    return _favorite_repository


def get_appointment_repository() -> AppointmentRepository:
    return _appointment_repository


def get_conversation_repository() -> ConversationRepository:
    return _conversation_repository


def get_message_repository() -> MessageRepository:
    return _message_repository


def get_contract_repository() -> ContractRepository:
    return _contract_repository
