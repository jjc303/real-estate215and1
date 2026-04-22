from __future__ import annotations

from typing import Any

from flask import jsonify


def _build_payload(code: int, message: str, data: Any) -> dict[str, Any]:
    return {
        "code": code,
        "message": message,
        "data": data,
    }


def success(data=None, message: str = "success", code: int = 0, status_code: int = 200):
    response = jsonify(_build_payload(code=code, message=message, data=data))
    response.status_code = status_code
    return response


def fail(message: str, code: int, data=None, status_code: int = 400):
    response = jsonify(_build_payload(code=code, message=message, data=data))
    response.status_code = status_code
    return response


def success_page(
    items,
    total: int,
    page: int,
    page_size: int,
    message: str = "success",
    code: int = 0,
    status_code: int = 200,
):
    page_data = {
        "list": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
    return success(data=page_data, message=message, code=code, status_code=status_code)
