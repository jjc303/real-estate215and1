from __future__ import annotations

from pydantic import Field, field_validator

from app.common.base_schema import BaseSchema


class HouseChatSchema(BaseSchema):
    house_id: int = Field(ge=1)
    message: str = Field(min_length=1, max_length=2000)
    session_id: str | None = Field(default=None, max_length=100)

    @field_validator("message", "session_id", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        value = value.strip()
        if value == "":
            return None
        return value


class ChatSchema(BaseSchema):
    message: str = Field(min_length=1, max_length=2000)
    session_id: str | None = Field(default=None, max_length=100)

    @field_validator("message", "session_id", mode="before")
    @classmethod
    def normalize_text(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        value = value.strip()
        if value == "":
            return None
        return value
