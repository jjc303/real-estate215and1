from __future__ import annotations

from pydantic import ConfigDict, Field

from app.common.base_schema import BaseSchema


class LoginSchema(BaseSchema):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=255)
