from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserReadSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: str
    real_name: str | None = None
    phone: str | None = None
    email: str | None = None
    avatar: str | None = None
    status: str
    created_at: datetime


class UserCreateSchema(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=6, max_length=255)
    role: str = Field(default="tenant", min_length=1, max_length=20)
    real_name: str | None = Field(default=None, max_length=50)
    phone: str | None = Field(default=None, max_length=20)
    email: str | None = Field(default=None, max_length=100)
    avatar: str | None = Field(default=None, max_length=255)
    status: str = Field(default="active", min_length=1, max_length=20)


class UserListQuerySchema(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
