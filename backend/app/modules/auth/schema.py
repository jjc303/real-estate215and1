from __future__ import annotations

from pydantic import BaseModel, Field


class LoginSchema(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=255)
