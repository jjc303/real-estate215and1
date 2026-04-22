from __future__ import annotations

from typing import Any

from flask import current_app
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException

from app.core.response import fail


SUCCESS_CODE = 0
BAD_REQUEST_CODE = 3001
BUSINESS_ERROR_CODE = 4000
UNAUTHORIZED_CODE = 1003
FORBIDDEN_CODE = 1004
NOT_FOUND_CODE = 4004
CONFLICT_CODE = 4009
INTERNAL_SERVER_ERROR_CODE = 5000


def _map_http_status_to_app_code(status_code: int) -> int:
    code_mapping = {
        400: BAD_REQUEST_CODE,
        401: UNAUTHORIZED_CODE,
        403: FORBIDDEN_CODE,
        404: NOT_FOUND_CODE,
        409: CONFLICT_CODE,
    }
    if status_code in code_mapping:
        return code_mapping[status_code]
    if 400 <= status_code < 500:
        return BAD_REQUEST_CODE
    return INTERNAL_SERVER_ERROR_CODE


class AppException(Exception):
    def __init__(
        self,
        message: str,
        code: int,
        status_code: int = 400,
        data: Any | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.data = data


class BusinessException(AppException):
    def __init__(
        self,
        message: str = "business error",
        code: int = BUSINESS_ERROR_CODE,
        status_code: int = 400,
        data: Any | None = None,
    ) -> None:
        super().__init__(message=message, code=code, status_code=status_code, data=data)


class BadRequestException(AppException):
    def __init__(self, message: str = "bad request", data: Any | None = None) -> None:
        super().__init__(
            message=message,
            code=BAD_REQUEST_CODE,
            status_code=400,
            data=data,
        )


class UnauthorizedException(AppException):
    def __init__(self, message: str = "unauthorized", data: Any | None = None) -> None:
        super().__init__(
            message=message,
            code=UNAUTHORIZED_CODE,
            status_code=401,
            data=data,
        )


class ForbiddenException(AppException):
    def __init__(self, message: str = "forbidden", data: Any | None = None) -> None:
        super().__init__(
            message=message,
            code=FORBIDDEN_CODE,
            status_code=403,
            data=data,
        )


class NotFoundException(AppException):
    def __init__(self, message: str = "resource not found", data: Any | None = None) -> None:
        super().__init__(
            message=message,
            code=NOT_FOUND_CODE,
            status_code=404,
            data=data,
        )


class ConflictException(AppException):
    def __init__(self, message: str = "resource conflict", data: Any | None = None) -> None:
        super().__init__(
            message=message,
            code=CONFLICT_CODE,
            status_code=409,
            data=data,
        )


class InternalServerException(AppException):
    def __init__(self, message: str = "internal server error", data: Any | None = None) -> None:
        super().__init__(
            message=message,
            code=INTERNAL_SERVER_ERROR_CODE,
            status_code=500,
            data=data,
        )


def register_error_handlers(app) -> None:
    @app.errorhandler(AppException)
    def handle_app_exception(exc: AppException):
        return fail(
            message=exc.message,
            code=exc.code,
            data=exc.data,
            status_code=exc.status_code,
        )

    @app.errorhandler(ValidationError)
    def handle_validation_error(exc: ValidationError):
        return fail(
            message="bad request",
            code=BAD_REQUEST_CODE,
            data=exc.errors(),
            status_code=400,
        )

    @app.errorhandler(HTTPException)
    def handle_http_exception(exc: HTTPException):
        status_code = exc.code or 500
        if status_code >= 500:
            current_app.logger.exception("HTTP exception occurred")

        return fail(
            message=exc.description or exc.name,
            code=_map_http_status_to_app_code(status_code),
            data=None,
            status_code=status_code,
        )

    @app.errorhandler(Exception)
    def handle_unexpected_exception(exc: Exception):
        current_app.logger.exception("Unhandled exception occurred")
        return fail(
            message="internal server error",
            code=INTERNAL_SERVER_ERROR_CODE,
            data=None,
            status_code=500,
        )
