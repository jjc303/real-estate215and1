from __future__ import annotations

# Run:
#   cd backend
#   pytest tests/api/test_operation_log_flow.py -q

from datetime import date, datetime, timedelta
from typing import Any

import requests


FORBIDDEN_CODE = 1004


def request_payload(
    http: requests.Session,
    base_url: str,
    method: str,
    path: str,
    *,
    step_name: str,
    expected_status: int,
    headers: dict[str, str] | None = None,
    json: dict[str, object] | None = None,
    params: dict[str, object] | None = None,
) -> dict[str, Any]:
    response = http.request(
        method=method,
        url=f"{base_url}{path}",
        headers=headers,
        json=json,
        params=params,
        timeout=20,
    )
    try:
        payload = response.json()
    except ValueError as exc:
        raise AssertionError(
            f"{step_name} failed: {method} {base_url}{path} returned non-JSON response; "
            f"expected HTTP {expected_status}, got HTTP {response.status_code}; body={response.text!r}"
        ) from exc

    if response.status_code != expected_status:
        raise AssertionError(
            f"{step_name} failed: {method} {base_url}{path} expected HTTP {expected_status}, "
            f"got HTTP {response.status_code}; response={payload!r}"
        )
    return payload


def create_user_and_login(unique_suffix: str, role: str, api_request) -> tuple[int, str]:
    username = f"{role}_{unique_suffix}"
    password = "Password123!"
    created = api_request(
        "POST",
        "/api/v1/users",
        step_name=f"register {role}",
        expected_status=201,
        json={
            "username": username,
            "password": password,
            "role": role,
            "email": f"{username}@example.com",
        },
    )
    login = api_request(
        "POST",
        "/api/v1/auth/login",
        step_name=f"{role} login",
        expected_status=200,
        json={"username": username, "password": password},
    )
    return created["data"]["id"], login["data"]["token"]


def test_admin_can_query_operation_logs(
    unique_suffix: str,
    api_request,
    auth_headers,
    http: requests.Session,
    base_url: str,
) -> None:
    admin_id, admin_token = create_user_and_login(f"admin_log_{unique_suffix}", "admin", api_request)
    _, landlord_token = create_user_and_login(f"landlord_log_{unique_suffix}", "landlord", api_request)
    tenant_id, tenant_token = create_user_and_login(f"tenant_log_{unique_suffix}", "tenant", api_request)

    news = api_request(
        "POST",
        "/api/v1/news",
        step_name="create log news",
        expected_status=201,
        headers=auth_headers(admin_token),
        json={
            "title": f"Log news {unique_suffix}",
            "content": "Operation log content",
            "status": "published",
        },
    )["data"]

    house = api_request(
        "POST",
        "/api/v1/houses",
        step_name="create payment log house",
        expected_status=201,
        headers=auth_headers(landlord_token),
        json={
            "title": f"Payment Log House {unique_suffix}",
            "address": f"Payment Log Address {unique_suffix}",
            "region": "Payment Log Region",
            "community": "Payment Log Community",
            "house_type": "1居室",
            "area": 60,
            "rent": 2600,
            "deposit": 2600,
            "decoration": "精装",
            "floor": "8/18",
            "orientation": "南",
            "description": "payment log flow house",
        },
    )["data"]

    api_request(
        "PATCH",
        f"/api/v1/houses/{house['id']}/publish",
        step_name="publish payment log house",
        expected_status=200,
        headers=auth_headers(landlord_token),
    )

    appointment = api_request(
        "POST",
        "/api/v1/appointments",
        step_name="create payment log appointment",
        expected_status=201,
        headers=auth_headers(tenant_token),
        json={
            "house_id": house["id"],
            "appointment_time": (datetime.now() + timedelta(days=1)).isoformat(),
            "remark": "operation log appointment",
        },
    )["data"]

    api_request(
        "PATCH",
        f"/api/v1/appointments/{appointment['id']}/confirm",
        step_name="confirm payment log appointment",
        expected_status=200,
        headers=auth_headers(landlord_token),
    )

    contract = api_request(
        "POST",
        "/api/v1/contracts",
        step_name="create payment log contract",
        expected_status=201,
        headers=auth_headers(landlord_token),
        json={
            "appointment_id": appointment["id"],
            "start_date": (date.today() + timedelta(days=7)).isoformat(),
            "end_date": (date.today() + timedelta(days=372)).isoformat(),
            "monthly_rent": 2600,
            "deposit": 2600,
            "remark": "operation log contract",
        },
    )["data"]

    api_request(
        "PATCH",
        f"/api/v1/contracts/{contract['id']}/confirm",
        step_name="confirm payment log contract",
        expected_status=200,
        headers=auth_headers(tenant_token),
    )

    bill = api_request(
        "POST",
        "/api/v1/bills",
        step_name="create payment log bill",
        expected_status=201,
        headers=auth_headers(landlord_token),
        json={
            "contract_id": contract["id"],
            "bill_type": "rent",
            "amount": 2600,
            "due_date": (date.today() + timedelta(days=10)).isoformat(),
            "remark": "operation log bill",
        },
    )["data"]

    payment = api_request(
        "POST",
        "/api/v1/payments",
        step_name="create payment log payment",
        expected_status=201,
        headers=auth_headers(tenant_token),
        json={
            "bill_id": bill["id"],
            "amount": 2600,
            "payment_method": "mock",
            "remark": "operation log payment",
        },
    )["data"]

    all_logs = api_request(
        "GET",
        "/api/v1/admin/logs",
        step_name="admin list logs",
        expected_status=200,
        headers=auth_headers(admin_token),
        params={"page": 1, "page_size": 100},
    )["data"]["list"]
    news_log = next((item for item in all_logs if item["module"] == "news" and item["record_id"] == news["id"]), None)
    payment_log = next(
        (item for item in all_logs if item["module"] == "payment" and item["record_id"] == payment["id"]),
        None,
    )
    assert news_log is not None, f"news operation log missing: {all_logs!r}"
    assert payment_log is not None, f"payment operation log missing: {all_logs!r}"
    assert news_log["action"] == "create"
    assert payment_log["action"] == "pay"
    assert payment_log["before_status"] == "unpaid"
    assert payment_log["after_status"] == "paid"

    payment_logs = api_request(
        "GET",
        "/api/v1/admin/logs",
        step_name="admin list payment logs",
        expected_status=200,
        headers=auth_headers(admin_token),
        params={"page": 1, "page_size": 100, "module": "payment", "user_id": tenant_id},
    )["data"]["list"]
    assert any(item["record_id"] == payment["id"] for item in payment_logs)
    assert all(item["module"] == "payment" for item in payment_logs)
    assert all(item["user_id"] == tenant_id for item in payment_logs)

    tenant_forbidden = request_payload(
        http,
        base_url,
        "GET",
        "/api/v1/admin/logs",
        step_name="tenant cannot list logs",
        expected_status=403,
        headers=auth_headers(tenant_token),
        params={"page": 1, "page_size": 10},
    )
    assert tenant_forbidden["code"] == FORBIDDEN_CODE

    invalid_module = request_payload(
        http,
        base_url,
        "GET",
        "/api/v1/admin/logs",
        step_name="invalid log module query",
        expected_status=400,
        headers=auth_headers(admin_token),
        params={"page": 1, "page_size": 10, "module": "invalid"},
    )
    assert invalid_module["code"] == 3001
