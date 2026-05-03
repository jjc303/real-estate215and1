from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from app.common.base_schema import BaseSchema
from app.common.enums import OperationLogModule as OperationLogModuleValues


OperationLogModule = Literal[
    OperationLogModuleValues.REPAIR,
    OperationLogModuleValues.COMPLAINT,
    OperationLogModuleValues.CONTRACT,
    OperationLogModuleValues.BILL,
    OperationLogModuleValues.PAYMENT,
    OperationLogModuleValues.NEWS,
]


class OperationLogReadSchema(BaseSchema):
    id: int
    user_id: int
    module: OperationLogModule
    record_id: int
    action: str
    before_status: str | None = None
    after_status: str | None = None
    created_at: datetime
    updated_at: datetime


class OperationLogListQuerySchema(BaseSchema):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)
    module: OperationLogModule | None = None
    user_id: int | None = Field(default=None, ge=1)
