from __future__ import annotations

# Run:
#   cd backend
#   pytest tests/api/test_notification_flow.py -q

from datetime import date, datetime, timedelta
from typing import Any

import requests


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
            f"expected HTTP {expected_status}, got HTTP {response.status_code}; "
            f"body={response.text!r}"
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


def create_active_contract(
    unique_suffix: str,
    api_request,
    auth_headers,
    landlord_token: str,
    tenant_token: str,
) -> dict[str, int]:
    house_response = api_request(
        "POST",
        "/api/v1/houses",
        step_name="create notification house",
        expected_status=201,
        headers=auth_headers(landlord_token),
        json={
            "title": f"Notification House {unique_suffix}",
            "address": f"Notification Address {unique_suffix}",
            "region": "Notification Region",
            "community": "Notification Community",
            "house_type": "1室1厅",
            "area": 66,
            "rent": 2600,
            "deposit": 2600,
            "decoration": "精装",
            "floor": "9/18",
            "orientation": "南",
            "description": "notification flow house",
        },
    )
    house_id = house_response["data"]["id"]

    api_request(
        "PATCH",
        f"/api/v1/houses/{house_id}/publish",
        step_name="publish notification house",
        expected_status=200,
        headers=auth_headers(landlord_token),
    )

    appointment_response = api_request(
        "POST",
        "/api/v1/appointments",
        step_name="create notification appointment",
        expected_status=201,
        headers=auth_headers(tenant_token),
        json={
            "house_id": house_id,
            "appointment_time": (datetime.now() + timedelta(days=1)).isoformat(),
            "remark": "notification appointment",
        },
    )
    appointment_id = appointment_response["data"]["id"]

    api_request(
        "PATCH",
        f"/api/v1/appointments/{appointment_id}/confirm",
        step_name="confirm notification appointment",
        expected_status=200,
        headers=auth_headers(landlord_token),
    )

    contract_response = api_request(
        "POST",
        "/api/v1/contracts",
        step_name="create notification contract",
        expected_status=201,
        headers=auth_headers(landlord_token),
        json={
            "appointment_id": appointment_id,
            "start_date": (date.today() + timedelta(days=7)).isoformat(),
            "end_date": (date.today() + timedelta(days=372)).isoformat(),
            "monthly_rent": 2600,
            "deposit": 2600,
            "remark": "notification contract",
        },
    )
    contract_id = contract_response["data"]["id"]

    confirm_response = api_request(
        "PATCH",
        f"/api/v1/contracts/{contract_id}/confirm",
        step_name="confirm notification contract",
        expected_status=200,
        headers=auth_headers(tenant_token),
    )

    return {
        "house_id": house_id,
        "appointment_id": appointment_id,
        "contract_id": contract_id,
        "tenant_id": confirm_response["data"]["tenant_id"],
        "landlord_id": confirm_response["data"]["landlord_id"],
    }


def create_notification(api_request, auth_headers, admin_token: str, payload: dict[str, object]) -> dict[str, Any]:
    return api_request(
        "POST",
        "/api/v1/notifications",
        step_name=f"create notification {payload['source_type']}",
        expected_status=201,
        headers=auth_headers(admin_token),
        json=payload,
    )


def list_notifications(api_request, auth_headers, token: str, *, status: str | None = None) -> list[dict[str, Any]]:
    params: dict[str, object] = {"page": 1, "page_size": 100}
    if status is not None:
        params["status"] = status
    response = api_request(
        "GET",
        "/api/v1/notifications",
        step_name=f"list notifications {status or 'all'}",
        expected_status=200,
        headers=auth_headers(token),
        params=params,
    )
    return response["data"]["list"]


def test_notification_manual_and_read_flow(
    unique_suffix: str,
    api_request,
    auth_headers,
    http: requests.Session,
    base_url: str,
) -> None:
    tenant_id, tenant_token = create_user_and_login(f"tenant_{unique_suffix}", "tenant", api_request)
    landlord_id, landlord_token = create_user_and_login(f"landlord_{unique_suffix}", "landlord", api_request)
    admin_id, admin_token = create_user_and_login(f"admin_{unique_suffix}", "admin", api_request)

    tenant_notification = create_notification(
        api_request,
        auth_headers,
        admin_token,
        {
            "user_id": tenant_id,
            "source_type": "repair",
            "source_id": 1,
            "title": "Repair update",
            "message": "Your repair has a new update.",
        },
    )["data"]
    landlord_notification = create_notification(
        api_request,
        auth_headers,
        admin_token,
        {
            "user_id": landlord_id,
            "source_type": "complaint",
            "source_id": 2,
            "title": "Complaint update",
            "message": "A complaint needs your attention.",
        },
    )["data"]
    admin_notification = create_notification(
        api_request,
        auth_headers,
        admin_token,
        {
            "user_id": admin_id,
            "source_type": "contract",
            "source_id": 3,
            "title": "Contract notice",
            "message": "Admin-only contract notice.",
        },
    )["data"]

    assert tenant_notification["status"] == "unread"
    assert landlord_notification["status"] == "unread"
    assert admin_notification["status"] == "unread"

    tenant_notifications = list_notifications(api_request, auth_headers, tenant_token)
    assert any(item["id"] == tenant_notification["id"] for item in tenant_notifications)
    assert all(item["user_id"] == tenant_id for item in tenant_notifications)

    unread_notifications = list_notifications(api_request, auth_headers, tenant_token, status="unread")
    assert any(item["id"] == tenant_notification["id"] for item in unread_notifications)

    detail = api_request(
        "GET",
        f"/api/v1/notifications/{tenant_notification['id']}",
        step_name="tenant get notification detail",
        expected_status=200,
        headers=auth_headers(tenant_token),
    )["data"]
    assert detail["id"] == tenant_notification["id"]

    read_response = api_request(
        "PATCH",
        f"/api/v1/notifications/{tenant_notification['id']}/read",
        step_name="tenant mark notification read",
        expected_status=200,
        headers=auth_headers(tenant_token),
    )["data"]
    assert read_response["status"] == "read"
    assert read_response["updated_at"] != tenant_notification["updated_at"]

    read_notifications = list_notifications(api_request, auth_headers, tenant_token, status="read")
    assert any(item["id"] == tenant_notification["id"] for item in read_notifications)

    mark_twice = request_payload(
        http,
        base_url,
        "PATCH",
        f"/api/v1/notifications/{tenant_notification['id']}/read",
        step_name="mark notification read twice",
        expected_status=400,
        headers=auth_headers(tenant_token),
    )
    assert mark_twice["code"] == 2902

    outsider_detail = request_payload(
        http,
        base_url,
        "GET",
        f"/api/v1/notifications/{landlord_notification['id']}",
        step_name="tenant get landlord notification",
        expected_status=404,
        headers=auth_headers(tenant_token),
    )
    assert outsider_detail["code"] == 2901

    outsider_read = request_payload(
        http,
        base_url,
        "PATCH",
        f"/api/v1/notifications/{landlord_notification['id']}/read",
        step_name="tenant read landlord notification",
        expected_status=404,
        headers=auth_headers(tenant_token),
    )
    assert outsider_read["code"] == 2901

    landlord_create = request_payload(
        http,
        base_url,
        "POST",
        "/api/v1/notifications",
        step_name="landlord create notification",
        expected_status=403,
        headers=auth_headers(landlord_token),
        json={
            "user_id": tenant_id,
            "source_type": "bill",
            "source_id": 4,
            "title": "not allowed",
            "message": "landlord should not create",
        },
    )
    assert landlord_create["code"] == 1004

    invalid_user = request_payload(
        http,
        base_url,
        "POST",
        "/api/v1/notifications",
        step_name="create notification for invalid user",
        expected_status=404,
        headers=auth_headers(admin_token),
        json={
            "user_id": 999999,
            "source_type": "bill",
            "source_id": 5,
            "title": "missing user",
            "message": "invalid target",
        },
    )
    assert invalid_user["code"] == 1001


def test_notification_auto_triggers(
    unique_suffix: str,
    api_request,
    auth_headers,
) -> None:
    _, landlord_token = create_user_and_login(f"auto_landlord_{unique_suffix}", "landlord", api_request)
    _, tenant_token = create_user_and_login(f"auto_tenant_{unique_suffix}", "tenant", api_request)

    contract_context = create_active_contract(
        unique_suffix,
        api_request,
        auth_headers,
        landlord_token,
        tenant_token,
    )
    contract_id = contract_context["contract_id"]

    tenant_notifications = list_notifications(api_request, auth_headers, tenant_token)
    assert any(
        item["source_type"] == "contract" and item["source_id"] == contract_id
        for item in tenant_notifications
    )

    landlord_notifications = list_notifications(api_request, auth_headers, landlord_token)
    assert any(
        item["source_type"] == "contract" and item["source_id"] == contract_id
        for item in landlord_notifications
    )

    repair = api_request(
        "POST",
        "/api/v1/repairs",
        step_name="create repair for auto notification",
        expected_status=201,
        headers=auth_headers(tenant_token),
        json={
            "contract_id": contract_id,
            "description": "auto notification repair",
        },
    )["data"]
    landlord_notifications = list_notifications(api_request, auth_headers, landlord_token)
    assert any(
        item["source_type"] == "repair" and item["source_id"] == repair["id"]
        for item in landlord_notifications
    )

    api_request(
        "PATCH",
        f"/api/v1/repairs/{repair['id']}/process",
        step_name="process repair auto notification",
        expected_status=200,
        headers=auth_headers(landlord_token),
    )
    tenant_notifications = list_notifications(api_request, auth_headers, tenant_token)
    assert any(
        item["source_type"] == "repair" and item["source_id"] == repair["id"]
        for item in tenant_notifications
    )

    complaint = api_request(
        "POST",
        "/api/v1/complaints",
        step_name="create complaint for auto notification",
        expected_status=201,
        headers=auth_headers(tenant_token),
        json={
            "contract_id": contract_id,
            "description": "auto notification complaint",
        },
    )["data"]
    landlord_notifications = list_notifications(api_request, auth_headers, landlord_token)
    assert any(
        item["source_type"] == "complaint" and item["source_id"] == complaint["id"]
        for item in landlord_notifications
    )

    api_request(
        "PATCH",
        f"/api/v1/complaints/{complaint['id']}/process",
        step_name="process complaint auto notification",
        expected_status=200,
        headers=auth_headers(landlord_token),
    )
    tenant_notifications = list_notifications(api_request, auth_headers, tenant_token)
    assert any(
        item["source_type"] == "complaint" and item["source_id"] == complaint["id"]
        for item in tenant_notifications
    )

    bill = api_request(
        "POST",
        "/api/v1/bills",
        step_name="create bill auto notification",
        expected_status=201,
        headers=auth_headers(landlord_token),
        json={
            "contract_id": contract_id,
            "bill_type": "rent",
            "amount": 2600,
            "due_date": (date.today() + timedelta(days=7)).isoformat(),
            "remark": "auto notification bill",
        },
    )["data"]
    tenant_notifications = list_notifications(api_request, auth_headers, tenant_token)
    assert any(
        item["source_type"] == "bill" and item["source_id"] == bill["id"]
        for item in tenant_notifications
    )

    api_request(
        "POST",
        "/api/v1/payments",
        step_name="pay bill auto notification",
        expected_status=201,
        headers=auth_headers(tenant_token),
        json={
            "bill_id": bill["id"],
            "amount": 2600,
            "payment_method": "mock",
            "remark": "auto notification payment",
        },
    )
    landlord_notifications = list_notifications(api_request, auth_headers, landlord_token)
    assert any(
        item["source_type"] == "bill" and item["source_id"] == bill["id"]
        for item in landlord_notifications
    )
