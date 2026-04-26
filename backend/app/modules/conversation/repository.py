from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session

from app.modules.conversation.model import Conversation, Message
from app.modules.house.model import House


class ConversationRepository:
    def create(self, db: Session, conversation: Conversation) -> Conversation:
        db.add(conversation)
        return conversation

    def get_by_id(self, db: Session, conversation_id: int) -> Conversation | None:
        stmt = select(Conversation).where(Conversation.id == conversation_id)
        return db.execute(stmt).scalar_one_or_none()

    def get_by_participants_and_house(
        self,
        db: Session,
        tenant_id: int,
        landlord_id: int,
        house_id: int,
    ) -> Conversation | None:
        stmt = select(Conversation).where(
            Conversation.tenant_id == tenant_id,
            Conversation.landlord_id == landlord_id,
            Conversation.house_id == house_id,
        )
        return db.execute(stmt).scalar_one_or_none()

    def get_by_id_and_user_id(
        self,
        db: Session,
        conversation_id: int,
        user_id: int,
    ) -> Conversation | None:
        stmt = select(Conversation).where(
            Conversation.id == conversation_id,
            or_(
                Conversation.tenant_id == user_id,
                Conversation.landlord_id == user_id,
            ),
        )
        return db.execute(stmt).scalar_one_or_none()

    def list_related_to_user(
        self,
        db: Session,
        user_id: int,
        offset: int,
        limit: int,
    ) -> list[tuple[Conversation, House]]:
        stmt = (
            select(Conversation, House)
            .join(House, House.id == Conversation.house_id)
            .where(
                or_(
                    Conversation.tenant_id == user_id,
                    Conversation.landlord_id == user_id,
                )
            )
            .order_by(Conversation.updated_at.desc(), Conversation.id.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(db.execute(stmt).all())

    def count_related_to_user(self, db: Session, user_id: int) -> int:
        stmt = select(func.count()).select_from(Conversation).where(
            or_(
                Conversation.tenant_id == user_id,
                Conversation.landlord_id == user_id,
            )
        )
        return int(db.execute(stmt).scalar_one())


class MessageRepository:
    def create(self, db: Session, message: Message) -> Message:
        db.add(message)
        return message

    def list_by_conversation_id(
        self,
        db: Session,
        conversation_id: int,
        offset: int,
        limit: int,
    ) -> list[Message]:
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc(), Message.id.asc())
            .offset(offset)
            .limit(limit)
        )
        return list(db.execute(stmt).scalars().all())

    def count_by_conversation_id(self, db: Session, conversation_id: int) -> int:
        stmt = select(func.count()).select_from(Message).where(
            Message.conversation_id == conversation_id
        )
        return int(db.execute(stmt).scalar_one())

    def get_last_by_conversation_id(self, db: Session, conversation_id: int) -> Message | None:
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc(), Message.id.desc())
            .limit(1)
        )
        return db.execute(stmt).scalar_one_or_none()

    def count_unread_for_user_in_conversation(
        self,
        db: Session,
        conversation_id: int,
        current_user_id: int,
    ) -> int:
        stmt = select(func.count()).select_from(Message).where(
            Message.conversation_id == conversation_id,
            Message.sender_id != current_user_id,
            Message.read_at.is_(None),
        )
        return int(db.execute(stmt).scalar_one())

    def mark_read_for_user_in_conversation(
        self,
        db: Session,
        conversation_id: int,
        current_user_id: int,
        read_at: datetime,
    ) -> int:
        stmt = (
            update(Message)
            .where(
                Message.conversation_id == conversation_id,
                Message.sender_id != current_user_id,
                Message.read_at.is_(None),
            )
            .values(read_at=read_at)
        )
        result = db.execute(stmt)
        return int(result.rowcount or 0)
