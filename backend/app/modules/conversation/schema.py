from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import Field, field_validator

from app.common.base_schema import BaseSchema
from app.modules.house.schema import HouseStatus


class ConversationCreateSchema(BaseSchema):
    house_id: int = Field(ge=1)


class ConversationListQuerySchema(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)


class ConversationMessageListQuerySchema(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)


class MessageCreateSchema(BaseSchema):
    content: str = Field(min_length=1, max_length=1000)

    @field_validator("content", mode="before")
    @classmethod
    def normalize_content(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        return value.strip()


class ConversationHouseSummarySchema(BaseSchema):
    id: int
    title: str
    region: str
    address: str
    house_type: str
    area: Decimal
    rent: Decimal
    deposit: Decimal
    status: HouseStatus


class LastMessageSchema(BaseSchema):
    id: int
    sender_id: int
    content: str
    created_at: datetime
    read_at: datetime | None = None


class ConversationReadSchema(BaseSchema):
    id: int
    house_id: int
    tenant_id: int
    landlord_id: int
    created_at: datetime
    updated_at: datetime
    house: ConversationHouseSummarySchema
    last_message: LastMessageSchema | None = None
    last_message_at: datetime | None = None
    unread_count: int


class MessageReadSchema(BaseSchema):
    id: int
    conversation_id: int
    sender_id: int
    content: str
    created_at: datetime
    read_at: datetime | None = None
