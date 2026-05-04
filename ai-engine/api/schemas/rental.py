"""Schemas for rental AI routes."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator


class RentalUserContext(BaseModel):
    id: int | None = None
    role: str | None = None


class RentalHouseContext(BaseModel):
    id: int
    title: str | None = None
    region: str | None = None
    address: str | None = None
    community: str | None = None
    house_type: str | None = None
    area: float | int | None = None
    rent: float | int | None = None
    deposit: float | int | None = None
    decoration: str | None = None
    floor: str | None = None
    orientation: str | None = None
    description: str | None = None
    status: str | None = None


class RentalPlatformContext(BaseModel):
    domain: str | None = None
    source: str | None = None


class RentalHouseChatRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=100)
    session_id: str = Field(..., min_length=1, max_length=100)
    message: str = Field(..., min_length=1, max_length=2000)
    user_context: RentalUserContext | None = None
    house_context: RentalHouseContext
    platform_context: RentalPlatformContext | None = None

    @field_validator("user_id", "session_id", "message", mode="before")
    @classmethod
    def _strip_required_string(cls, value: Any):
        if isinstance(value, str):
            value = value.strip()
        return value


class RentalChatRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=100)
    session_id: str = Field(..., min_length=1, max_length=100)
    message: str = Field(..., min_length=1, max_length=2000)
    user_context: RentalUserContext | None = None
    platform_context: RentalPlatformContext | None = None

    @field_validator("user_id", "session_id", "message", mode="before")
    @classmethod
    def _strip_required_string(cls, value: Any):
        if isinstance(value, str):
            value = value.strip()
        return value


class RentalChatResponse(BaseModel):
    answer: str
    session_id: str
    sources: list[dict[str, Any]] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
