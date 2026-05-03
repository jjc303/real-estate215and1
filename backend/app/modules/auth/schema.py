from __future__ import annotations

from typing import Literal

from pydantic import ConfigDict, EmailStr, Field, field_validator

from app.common.base_schema import BaseSchema


EmailBizType = Literal["register", "login"]
EmailRegisterRole = Literal["tenant", "landlord"]


class LoginSchema(BaseSchema):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=255)

    @field_validator("username", "password", mode="before")
    @classmethod
    def normalize_login_text(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        return value.strip()


class SendEmailCodeSchema(BaseSchema):
    email: EmailStr
    biz_type: EmailBizType


class EmailRegisterSchema(BaseSchema):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6)
    role: EmailRegisterRole = "tenant"
    password: str | None = Field(default=None, min_length=1, max_length=255)
    real_name: str | None = Field(default=None, max_length=50)
    phone: str | None = Field(default=None, max_length=20)
    avatar: str | None = Field(default=None, max_length=255)

    @field_validator("password", "real_name", "phone", "avatar", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        value = value.strip()
        if value == "":
            return None
        return value

    @field_validator("code", mode="before")
    @classmethod
    def normalize_code(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        return value.strip()

    @field_validator("code")
    @classmethod
    def validate_code(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("code must be 6 digits")
        return value


class EmailLoginSchema(BaseSchema):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6)

    @field_validator("code", mode="before")
    @classmethod
    def normalize_code(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        return value.strip()

    @field_validator("code")
    @classmethod
    def validate_code(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("code must be 6 digits")
        return value
