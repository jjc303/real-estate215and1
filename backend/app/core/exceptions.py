from __future__ import annotations

import json
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
USER_NOT_FOUND_CODE = 1001
INVALID_CREDENTIALS_CODE = 1002
HOUSE_NOT_FOUND_CODE = 2001
FAVORITE_NOT_FOUND_CODE = 2101
APPOINTMENT_NOT_FOUND_CODE = 2201
INVALID_APPOINTMENT_STATUS_CODE = 2202
OWN_HOUSE_APPOINTMENT_FORBIDDEN_CODE = 2203
APPOINTMENT_TIME_INVALID_CODE = 2204
CONVERSATION_NOT_FOUND_CODE = 2301
OWN_HOUSE_CONVERSATION_FORBIDDEN_CODE = 2302
CONTRACT_NOT_FOUND_CODE = 2401
INVALID_CONTRACT_STATUS_CODE = 2402
OWN_HOUSE_CONTRACT_FORBIDDEN_CODE = 2403
CONTRACT_DATE_INVALID_CODE = 2404
HOUSE_ACTIVE_CONTRACT_CONFLICT_CODE = 2405
BILL_NOT_FOUND_CODE = 2501
INVALID_BILL_STATUS_CODE = 2502
CONTRACT_NOT_ACTIVE_FOR_BILL_CODE = 2503
BILL_AMOUNT_INVALID_CODE = 2504
PAYMENT_NOT_FOUND_CODE = 2601
PAYMENT_BILL_STATUS_INVALID_CODE = 2602
PAYMENT_AMOUNT_MISMATCH_CODE = 2603
BILL_ALREADY_PAID_CODE = 2604
REPAIR_NOT_FOUND_CODE = 2701
INVALID_REPAIR_STATUS_CODE = 2702
CONTRACT_NOT_ACTIVE_FOR_REPAIR_CODE = 2703
COMPLAINT_NOT_FOUND_CODE = 2801
INVALID_COMPLAINT_STATUS_CODE = 2802
CONTRACT_NOT_ACTIVE_FOR_COMPLAINT_CODE = 2803
NOTIFICATION_NOT_FOUND_CODE = 2901
INVALID_NOTIFICATION_STATUS_CODE = 2902


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


class UserNotFoundException(AppException):
    def __init__(self, message: str = "user not found", data: Any | None = None) -> None:
        super().__init__(
            message=message,
            code=USER_NOT_FOUND_CODE,
            status_code=404,
            data=data,
        )


class HouseNotFoundException(AppException):
    def __init__(self, message: str = "house not found", data: Any | None = None) -> None:
        super().__init__(
            message=message,
            code=HOUSE_NOT_FOUND_CODE,
            status_code=404,
            data=data,
        )


class FavoriteNotFoundException(AppException):
    def __init__(self, message: str = "收藏不存在", data: Any | None = None) -> None:
        super().__init__(
            message=message,
            code=FAVORITE_NOT_FOUND_CODE,
            status_code=404,
            data=data,
        )


class AppointmentNotFoundException(AppException):
    def __init__(self, message: str = "预约不存在", data: Any | None = None) -> None:
        super().__init__(
            message=message,
            code=APPOINTMENT_NOT_FOUND_CODE,
            status_code=404,
            data=data,
        )


class InvalidAppointmentStatusException(AppException):
    def __init__(self, message: str = "非法预约状态", data: Any | None = None) -> None:
        super().__init__(
            message=message,
            code=INVALID_APPOINTMENT_STATUS_CODE,
            status_code=400,
            data=data,
        )


class OwnHouseAppointmentForbiddenException(AppException):
    def __init__(self, message: str = "不能预约自己的房源", data: Any | None = None) -> None:
        super().__init__(
            message=message,
            code=OWN_HOUSE_APPOINTMENT_FORBIDDEN_CODE,
            status_code=400,
            data=data,
        )


class AppointmentTimeInvalidException(AppException):
    def __init__(self, message: str = "预约时间必须是未来时间", data: Any | None = None) -> None:
        super().__init__(
            message=message,
            code=APPOINTMENT_TIME_INVALID_CODE,
            status_code=400,
            data=data,
        )


class ConversationNotFoundException(AppException):
    def __init__(self, message: str = "会话不存在", data: Any | None = None) -> None:
        super().__init__(
            message=message,
            code=CONVERSATION_NOT_FOUND_CODE,
            status_code=404,
            data=data,
        )


class OwnHouseConversationForbiddenException(AppException):
    def __init__(self, message: str = "不能联系自己的房源", data: Any | None = None) -> None:
        super().__init__(
            message=message,
            code=OWN_HOUSE_CONVERSATION_FORBIDDEN_CODE,
            status_code=400,
            data=data,
        )


class ContractNotFoundException(AppException):
    def __init__(self, message: str = "合同不存在", data: Any | None = None) -> None:
        super().__init__(
            message=message,
            code=CONTRACT_NOT_FOUND_CODE,
            status_code=404,
            data=data,
        )


class InvalidContractStatusException(AppException):
    def __init__(self, message: str = "非法合同状态", data: Any | None = None) -> None:
        super().__init__(
            message=message,
            code=INVALID_CONTRACT_STATUS_CODE,
            status_code=400,
            data=data,
        )


class OwnHouseContractForbiddenException(AppException):
    def __init__(self, message: str = "不能和自己的房源签合同", data: Any | None = None) -> None:
        super().__init__(
            message=message,
            code=OWN_HOUSE_CONTRACT_FORBIDDEN_CODE,
            status_code=400,
            data=data,
        )


class ContractDateInvalidException(AppException):
    def __init__(self, message: str = "合同时间不合法", data: Any | None = None) -> None:
        super().__init__(
            message=message,
            code=CONTRACT_DATE_INVALID_CODE,
            status_code=400,
            data=data,
        )


class HouseActiveContractConflictException(AppException):
    def __init__(self, message: str = "房源已有生效合同", data: Any | None = None) -> None:
        super().__init__(
            message=message,
            code=HOUSE_ACTIVE_CONTRACT_CONFLICT_CODE,
            status_code=409,
            data=data,
        )


class BillNotFoundException(AppException):
    def __init__(self, message: str = "bill not found", data: Any | None = None) -> None:
        super().__init__(
            message=message,
            code=BILL_NOT_FOUND_CODE,
            status_code=404,
            data=data,
        )


class InvalidBillStatusException(AppException):
    def __init__(self, message: str = "invalid bill status", data: Any | None = None) -> None:
        super().__init__(
            message=message,
            code=INVALID_BILL_STATUS_CODE,
            status_code=400,
            data=data,
        )


class ContractNotActiveForBillException(AppException):
    def __init__(
        self,
        message: str = "contract is not active for bill creation",
        data: Any | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=CONTRACT_NOT_ACTIVE_FOR_BILL_CODE,
            status_code=400,
            data=data,
        )


class BillAmountInvalidException(AppException):
    def __init__(self, message: str = "bill amount is invalid", data: Any | None = None) -> None:
        super().__init__(
            message=message,
            code=BILL_AMOUNT_INVALID_CODE,
            status_code=400,
            data=data,
        )


class PaymentNotFoundException(AppException):
    def __init__(self, message: str = "payment not found", data: Any | None = None) -> None:
        super().__init__(
            message=message,
            code=PAYMENT_NOT_FOUND_CODE,
            status_code=404,
            data=data,
        )


class BillNotPayableException(AppException):
    def __init__(self, message: str = "bill status is not payable", data: Any | None = None) -> None:
        super().__init__(
            message=message,
            code=PAYMENT_BILL_STATUS_INVALID_CODE,
            status_code=400,
            data=data,
        )


class PaymentAmountMismatchException(AppException):
    def __init__(self, message: str = "payment amount mismatch", data: Any | None = None) -> None:
        super().__init__(
            message=message,
            code=PAYMENT_AMOUNT_MISMATCH_CODE,
            status_code=400,
            data=data,
        )


class BillAlreadyPaidException(AppException):
    def __init__(self, message: str = "bill already paid", data: Any | None = None) -> None:
        super().__init__(
            message=message,
            code=BILL_ALREADY_PAID_CODE,
            status_code=409,
            data=data,
        )


class RepairNotFoundException(AppException):
    def __init__(self, message: str = "repair not found", data: Any | None = None) -> None:
        super().__init__(
            message=message,
            code=REPAIR_NOT_FOUND_CODE,
            status_code=404,
            data=data,
        )


class InvalidRepairStatusException(AppException):
    def __init__(self, message: str = "invalid repair status", data: Any | None = None) -> None:
        super().__init__(
            message=message,
            code=INVALID_REPAIR_STATUS_CODE,
            status_code=400,
            data=data,
        )


class ContractNotActiveForRepairException(AppException):
    def __init__(
        self,
        message: str = "contract status is not allowed for repair",
        data: Any | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=CONTRACT_NOT_ACTIVE_FOR_REPAIR_CODE,
            status_code=400,
            data=data,
        )


class ComplaintNotFoundException(AppException):
    def __init__(self, message: str = "complaint not found", data: Any | None = None) -> None:
        super().__init__(
            message=message,
            code=COMPLAINT_NOT_FOUND_CODE,
            status_code=404,
            data=data,
        )


class InvalidComplaintStatusException(AppException):
    def __init__(self, message: str = "invalid complaint status", data: Any | None = None) -> None:
        super().__init__(
            message=message,
            code=INVALID_COMPLAINT_STATUS_CODE,
            status_code=400,
            data=data,
        )


class ContractNotActiveForComplaintException(AppException):
    def __init__(
        self,
        message: str = "contract status is not allowed for complaint",
        data: Any | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=CONTRACT_NOT_ACTIVE_FOR_COMPLAINT_CODE,
            status_code=400,
            data=data,
        )


class NotificationNotFoundException(AppException):
    def __init__(self, message: str = "notification not found", data: Any | None = None) -> None:
        super().__init__(
            message=message,
            code=NOTIFICATION_NOT_FOUND_CODE,
            status_code=404,
            data=data,
        )


class InvalidNotificationStatusException(AppException):
    def __init__(self, message: str = "invalid notification status", data: Any | None = None) -> None:
        super().__init__(
            message=message,
            code=INVALID_NOTIFICATION_STATUS_CODE,
            status_code=400,
            data=data,
        )


class InvalidCredentialsException(AppException):
    def __init__(
        self,
        message: str = "用户名或密码错误",
        data: Any | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code=INVALID_CREDENTIALS_CODE,
            status_code=401,
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
    def _build_validation_error_data(exc: ValidationError):
        # Pydantic v2 may include non-JSON-serializable objects such as
        # ValueError instances inside error context. Normalize them to strings
        # so the unified JSON error response can always be returned.
        return json.loads(json.dumps(exc.errors(), default=str, ensure_ascii=False))

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
            data=_build_validation_error_data(exc),
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
