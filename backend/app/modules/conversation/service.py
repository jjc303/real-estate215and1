from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.common.enums import HouseStatus
from app.common.pagination import build_page_result, get_offset
from app.core.exceptions import (
    BadRequestException,
    ConversationNotFoundException,
    HouseNotFoundException,
    OwnHouseConversationForbiddenException,
)
from app.modules.conversation.model import Conversation, Message
from app.modules.conversation.repository import ConversationRepository, MessageRepository
from app.modules.conversation.schema import (
    ConversationHouseSummarySchema,
    ConversationReadSchema,
    LastMessageSchema,
    MessageReadSchema,
)
from app.modules.house.model import House
from app.modules.house.repository import HouseRepository


class ConversationService:
    def __init__(
        self,
        conversation_repository: ConversationRepository,
        message_repository: MessageRepository,
        house_repository: HouseRepository,
    ) -> None:
        self.conversation_repository = conversation_repository
        self.message_repository = message_repository
        self.house_repository = house_repository

    def create_conversation(
        self,
        db: Session,
        current_user_id: int,
        house_id: int,
    ) -> tuple[dict[str, object], bool]:
        house = self._get_available_house(db, house_id)
        if house.landlord_id == current_user_id:
            raise OwnHouseConversationForbiddenException()

        existing = self.conversation_repository.get_by_participants_and_house(
            db,
            tenant_id=current_user_id,
            landlord_id=house.landlord_id,
            house_id=house.id,
        )
        if existing is not None:
            return self._serialize_conversation(db, existing, house, current_user_id), False

        conversation = Conversation(
            house_id=house.id,
            tenant_id=current_user_id,
            landlord_id=house.landlord_id,
        )
        try:
            self.conversation_repository.create(db, conversation)
            db.commit()
            db.refresh(conversation)
        except Exception:
            db.rollback()
            raise

        return self._serialize_conversation(db, conversation, house, current_user_id), True

    def list_conversations(
        self,
        db: Session,
        current_user_id: int,
        page: int,
        page_size: int,
    ) -> dict[str, object]:
        offset = get_offset(page, page_size)
        rows = self.conversation_repository.list_related_to_user(
            db,
            user_id=current_user_id,
            offset=offset,
            limit=page_size,
        )
        total = self.conversation_repository.count_related_to_user(db, current_user_id)
        items = [
            self._serialize_conversation(db, conversation, house, current_user_id)
            for conversation, house in rows
        ]
        return build_page_result(items=items, total=total, page=page, page_size=page_size)

    def list_messages(
        self,
        db: Session,
        current_user_id: int,
        conversation_id: int,
        page: int,
        page_size: int,
    ) -> dict[str, object]:
        conversation = self._get_user_conversation_or_not_found(
            db,
            conversation_id=conversation_id,
            current_user_id=current_user_id,
        )
        offset = get_offset(page, page_size)
        messages = self.message_repository.list_by_conversation_id(
            db,
            conversation_id=conversation.id,
            offset=offset,
            limit=page_size,
        )
        total = self.message_repository.count_by_conversation_id(db, conversation.id)
        items = [self._serialize_message(message) for message in messages]
        return build_page_result(items=items, total=total, page=page, page_size=page_size)

    def send_message(
        self,
        db: Session,
        current_user_id: int,
        conversation_id: int,
        content: str,
    ) -> dict[str, object]:
        conversation = self._get_user_conversation_or_not_found(
            db,
            conversation_id=conversation_id,
            current_user_id=current_user_id,
        )
        normalized_content = content.strip()
        if normalized_content == "":
            raise BadRequestException(message="bad request")

        sent_at = datetime.utcnow()
        message = Message(
            conversation_id=conversation.id,
            sender_id=current_user_id,
            content=normalized_content,
            created_at=sent_at,
        )
        conversation.updated_at = sent_at

        try:
            self.message_repository.create(db, message)
            db.commit()
            db.refresh(message)
        except Exception:
            db.rollback()
            raise

        return self._serialize_message(message)

    def mark_conversation_read(
        self,
        db: Session,
        current_user_id: int,
        conversation_id: int,
    ) -> dict[str, int]:
        conversation = self._get_user_conversation_or_not_found(
            db,
            conversation_id=conversation_id,
            current_user_id=current_user_id,
        )
        read_at = datetime.utcnow()

        try:
            updated = self.message_repository.mark_read_for_user_in_conversation(
                db,
                conversation_id=conversation.id,
                current_user_id=current_user_id,
                read_at=read_at,
            )
            db.commit()
        except Exception:
            db.rollback()
            raise

        return {"updated": updated}

    def _get_available_house(self, db: Session, house_id: int) -> House:
        house = self.house_repository.get_by_id(db, house_id)
        if house is None or house.deleted_at is not None or house.status != HouseStatus.LISTED:
            raise HouseNotFoundException()
        return house

    def _get_user_conversation_or_not_found(
        self,
        db: Session,
        conversation_id: int,
        current_user_id: int,
    ) -> Conversation:
        conversation = self.conversation_repository.get_by_id_and_user_id(
            db,
            conversation_id=conversation_id,
            user_id=current_user_id,
        )
        if conversation is None:
            raise ConversationNotFoundException()
        return conversation

    def _serialize_conversation(
        self,
        db: Session,
        conversation: Conversation,
        house: House,
        current_user_id: int,
    ) -> dict[str, object]:
        last_message = self.message_repository.get_last_by_conversation_id(db, conversation.id)
        unread_count = self.message_repository.count_unread_for_user_in_conversation(
            db,
            conversation.id,
            current_user_id,
        )
        house_data = ConversationHouseSummarySchema.model_validate(house)
        last_message_data = None
        last_message_at = None
        if last_message is not None:
            last_message_data = LastMessageSchema.model_validate(last_message)
            last_message_at = last_message.created_at

        return ConversationReadSchema(
            id=conversation.id,
            house_id=conversation.house_id,
            tenant_id=conversation.tenant_id,
            landlord_id=conversation.landlord_id,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            house=house_data,
            last_message=last_message_data,
            last_message_at=last_message_at,
            unread_count=unread_count,
        ).model_dump(mode="json")

    def _serialize_message(self, message: Message) -> dict[str, object]:
        return MessageReadSchema.model_validate(message).model_dump(mode="json")
