from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field, field_validator, model_validator

from app.common.base_schema import BaseSchema
from app.common.enums import NewsStatus as NewsStatusValues


NewsStatus = Literal[
    NewsStatusValues.DRAFT,
    NewsStatusValues.PUBLISHED,
]


class NewsCreateSchema(BaseSchema):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=5000)
    status: NewsStatus = NewsStatusValues.DRAFT

    @field_validator("title", "content", mode="before")
    @classmethod
    def normalize_required_text(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        return value.strip()


class NewsUpdateSchema(BaseSchema):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    content: str | None = Field(default=None, min_length=1, max_length=5000)
    status: NewsStatus | None = None

    @field_validator("title", "content", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        value = value.strip()
        if value == "":
            return None
        return value

    @model_validator(mode="after")
    def validate_at_least_one_field(self) -> "NewsUpdateSchema":
        if self.title is None and self.content is None and self.status is None:
            raise ValueError("at least one field must be provided")
        return self


class NewsReadSchema(BaseSchema):
    id: int
    title: str
    content: str
    author_id: int
    status: NewsStatus
    created_at: datetime
    updated_at: datetime


class NewsListQuerySchema(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
    status: NewsStatus | None = None
