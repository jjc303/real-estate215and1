from __future__ import annotations

# Run:
#   cd backend
#   pytest tests/api/test_admin_flow.py -q

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


def create_house_and_confirmed_appointment(
    unique_suffix: str,
    api_request,
    auth_headers,
    landlord_token: str,
    tenant_token: str,
) -> tuple[int, int]:
    house = api_request(
        "POST",
        "/api/v1/houses",
        step_name="admin create house",
        expected_status=201,
        headers=auth_headers(landlord_token),
        json={
            "title": f"Admin House {unique_suffix}",
            "address": f"Admin Address {unique_suffix}",
            "region": "Admin Region",
            "community": "Admin Community",
            "house_type": "1室1厅",
            "area": 66,
            "rent": 2600,
            "deposit": 2600,
            "decoration": "精装",
            "floor": "9/18",
            "orientation": "南",
            "description": "admin flow house",
        },
    )["data"]
    house_id = house["id"]

    api_request(
        "PATCH",
        f"/api/v1/houses/{house_id}/publish",
        step_name="admin publish house",
        expected_status=200,
        headers=auth_headers(landlord_token),
    )

    appointment = api_request(
        "POST",
        "/api/v1/appointments",
        step_name="admin create appointment",
        expected_status=201,
        headers=auth_headers(tenant_token),
        json={
            "house_id": house_id,
            "appointment_time": (datetime.now() + timedelta(days=1)).isoformat(),
            "remark": "admin appointment",
        },
    )["data"]

    api_request(
        "PATCH",
        f"/api/v1/appointments/{appointment['id']}/confirm",
        step_name="admin confirm appointment",
        expected_status=200,
        headers=auth_headers(landlord_token),
    )
    return house_id, appointment["id"]


def create_pending_contract(
    unique_suffix: str,
    api_request,
    auth_headers,
    landlord_token: str,
    tenant_token: str,
) -> dict[str, int]:
    house_id, appointment_id = create_house_and_confirmed_appointment(
        unique_suffix,
        api_request,
        auth_headers,
        landlord_token,
        tenant_token,
    )
    contract = api_request(
        "POST",
        "/api/v1/contracts",
        step_name="admin create contract",
        expected_status=201,
        headers=auth_headers(landlord_token),
        json={
            "appointment_id": appointment_id,
            "start_date": (date.today() + timedelta(days=7)).isoformat(),
            "end_date": (date.today() + timedelta(days=372)).isoformat(),
            "monthly_rent": 2600,
            "deposit": 2600,
            "remark": "admin contract",
        },
    )["data"]
    return {
        "house_id": house_id,
        "contract_id": contract["id"],
    }


def create_active_contract(
    unique_suffix: str,
    api_request,
    auth_headers,
    landlord_token: str,
    tenant_token: str,
) -> dict[str, int]:
    context = create_pending_contract(
        unique_suffix,
        api_request,
        auth_headers,
        landlord_token,
        tenant_token,
    )
    confirmed = api_request(
        "PATCH",
        f"/api/v1/contracts/{context['contract_id']}/confirm",
        step_name="tenant confirm contract",
        expected_status=200,
        headers=auth_headers(tenant_token),
    )["data"]
    return {
        "house_id": context["house_id"],
        "contract_id": context["contract_id"],
        "tenant_id": confirmed["tenant_id"],
        "landlord_id": confirmed["landlord_id"],
    }


def test_admin_user_house_and_permissions(
    unique_suffix: str,
    api_request,
    auth_headers,
    http: requests.Session,
    base_url: str,
) -> None:
    _, admin_token = create_user_and_login(f"admin_{unique_suffix}", "admin", api_request)
    _, tenant_token = create_user_and_login(f"tenant_{unique_suffix}", "tenant", api_request)
    _, landlord_token = create_user_and_login(f"landlord_{unique_suffix}", "landlord", api_request)

    created_user = api_request(
        "POST",
        "/api/v1/admin/users",
        step_name="admin create user",
        expected_status=201,
        headers=auth_headers(admin_token),
        json={
            "username": f"managed_user_{unique_suffix}",
            "password": "Password123!",
            "role": "tenant",
            "email": f"managed_{unique_suffix}@example.com",
            "status": "active",
        },
    )["data"]
    assert created_user["status"] == "active"

    listed_users = api_request(
        "GET",
        "/api/v1/admin/users",
        step_name="admin list users",
        expected_status=200,
        headers=auth_headers(admin_token),
        params={"page": 1, "page_size": 100},
    )["data"]
    assert any(item["id"] == created_user["id"] for item in listed_users["list"])

    updated_user = api_request(
        "PUT",
        f"/api/v1/admin/users/{created_user['id']}",
        step_name="admin update user",
        expected_status=200,
        headers=auth_headers(admin_token),
        json={
            "username": f"managed_user_updated_{unique_suffix}",
            "password": "UpdatedPass123!",
            "role": "landlord",
            "real_name": "Managed User",
            "phone": "1234567890",
            "email": f"managed_updated_{unique_suffix}@example.com",
            "avatar": "https://example.com/avatar.png",
        },
    )["data"]
    assert updated_user["role"] == "landlord"
    assert updated_user["username"] == f"managed_user_updated_{unique_suffix}"

    disabled_user = api_request(
        "PATCH",
        f"/api/v1/admin/users/{created_user['id']}/status",
        step_name="admin disable user",
        expected_status=200,
        headers=auth_headers(admin_token),
        json={"status": "disabled"},
    )["data"]
    assert disabled_user["status"] == "disabled"

    enabled_user = api_request(
        "PATCH",
        f"/api/v1/admin/users/{created_user['id']}/status",
        step_name="admin enable user",
        expected_status=200,
        headers=auth_headers(admin_token),
        json={"status": "active"},
    )["data"]
    assert enabled_user["status"] == "active"

    house_context = create_pending_contract(
        f"house_{unique_suffix}",
        api_request,
        auth_headers,
        landlord_token,
        tenant_token,
    )

    houses = api_request(
        "GET",
        "/api/v1/admin/houses",
        step_name="admin list houses",
        expected_status=200,
        headers=auth_headers(admin_token),
        params={"page": 1, "page_size": 100},
    )["data"]
    assert any(item["id"] == house_context["house_id"] for item in houses["list"])

    house_detail = api_request(
        "GET",
        f"/api/v1/admin/houses/{house_context['house_id']}",
        step_name="admin get house detail",
        expected_status=200,
        headers=auth_headers(admin_token),
    )["data"]
    assert house_detail["id"] == house_context["house_id"]

    empty_page = api_request(
        "GET",
        "/api/v1/admin/houses",
        step_name="admin list houses empty page",
        expected_status=200,
        headers=auth_headers(admin_token),
        params={"page": 9999, "page_size": 10},
    )["data"]
    assert empty_page["list"] == []

    tenant_forbidden = request_payload(
        http,
        base_url,
        "GET",
        "/api/v1/admin/users",
        step_name="tenant admin users forbidden",
        expected_status=403,
        headers=auth_headers(tenant_token),
    )
    assert tenant_forbidden["code"] == 1004

    landlord_forbidden = request_payload(
        http,
        base_url,
        "GET",
        "/api/v1/admin/houses",
        step_name="landlord admin houses forbidden",
        expected_status=403,
        headers=auth_headers(landlord_token),
    )
    assert landlord_forbidden["code"] == 1004


def test_admin_repair_complaint_and_contract_management(
    unique_suffix: str,
    api_request,
    auth_headers,
    http: requests.Session,
    base_url: str,
) -> None:
    _, admin_token = create_user_and_login(f"admin_ops_{unique_suffix}", "admin", api_request)
    _, landlord_token = create_user_and_login(f"landlord_ops_{unique_suffix}", "landlord", api_request)
    _, tenant_token = create_user_and_login(f"tenant_ops_{unique_suffix}", "tenant", api_request)

    active_contract = create_active_contract(
        f"active_{unique_suffix}",
        api_request,
        auth_headers,
        landlord_token,
        tenant_token,
    )

    repair = api_request(
        "POST",
        "/api/v1/repairs",
        step_name="create admin repair",
        expected_status=201,
        headers=auth_headers(tenant_token),
        json={
            "contract_id": active_contract["contract_id"],
            "description": "admin repair item",
        },
    )["data"]
    complaint = api_request(
        "POST",
        "/api/v1/complaints",
        step_name="create admin complaint",
        expected_status=201,
        headers=auth_headers(tenant_token),
        json={
            "contract_id": active_contract["contract_id"],
            "description": "admin complaint item",
        },
    )["data"]

    repairs = api_request(
        "GET",
        "/api/v1/admin/repairs",
        step_name="admin list repairs",
        expected_status=200,
        headers=auth_headers(admin_token),
        params={"page": 1, "page_size": 100},
    )["data"]
    assert any(item["id"] == repair["id"] for item in repairs["list"])

    complaints = api_request(
        "GET",
        "/api/v1/admin/complaints",
        step_name="admin list complaints",
        expected_status=200,
        headers=auth_headers(admin_token),
        params={"page": 1, "page_size": 100},
    )["data"]
    assert any(item["id"] == complaint["id"] for item in complaints["list"])

    processed_repair = api_request(
        "PATCH",
        f"/api/v1/admin/repairs/{repair['id']}/process",
        step_name="admin process repair",
        expected_status=200,
        headers=auth_headers(admin_token),
    )["data"]
    assert processed_repair["status"] == "processing"

    completed_repair = api_request(
        "PATCH",
        f"/api/v1/admin/repairs/{repair['id']}/complete",
        step_name="admin complete repair",
        expected_status=200,
        headers=auth_headers(admin_token),
    )["data"]
    assert completed_repair["status"] == "completed"

    closed_repair = api_request(
        "PATCH",
        f"/api/v1/admin/repairs/{repair['id']}/close",
        step_name="admin close repair",
        expected_status=200,
        headers=auth_headers(admin_token),
    )["data"]
    assert closed_repair["status"] == "closed"

    invalid_repair = request_payload(
        http,
        base_url,
        "PATCH",
        f"/api/v1/admin/repairs/{repair['id']}/process",
        step_name="admin invalid repair transition",
        expected_status=400,
        headers=auth_headers(admin_token),
    )
    assert invalid_repair["code"] == 2702

    processed_complaint = api_request(
        "PATCH",
        f"/api/v1/admin/complaints/{complaint['id']}/process",
        step_name="admin process complaint",
        expected_status=200,
        headers=auth_headers(admin_token),
    )["data"]
    assert processed_complaint["status"] == "processing"

    resolved_complaint = api_request(
        "PATCH",
        f"/api/v1/admin/complaints/{complaint['id']}/resolve",
        step_name="admin resolve complaint",
        expected_status=200,
        headers=auth_headers(admin_token),
    )["data"]
    assert resolved_complaint["status"] == "resolved"

    closed_complaint = api_request(
        "PATCH",
        f"/api/v1/admin/complaints/{complaint['id']}/close",
        step_name="admin close complaint",
        expected_status=200,
        headers=auth_headers(admin_token),
    )["data"]
    assert closed_complaint["status"] == "closed"

    invalid_complaint = request_payload(
        http,
        base_url,
        "PATCH",
        f"/api/v1/admin/complaints/{complaint['id']}/process",
        step_name="admin invalid complaint transition",
        expected_status=400,
        headers=auth_headers(admin_token),
    )
    assert invalid_complaint["code"] == 2802

    pending_for_activate = create_pending_contract(
        f"pending_activate_{unique_suffix}",
        api_request,
        auth_headers,
        landlord_token,
        tenant_token,
    )
    activated_contract = api_request(
        "PATCH",
        f"/api/v1/admin/contracts/{pending_for_activate['contract_id']}/status",
        step_name="admin activate contract",
        expected_status=200,
        headers=auth_headers(admin_token),
        json={"status": "active"},
    )["data"]
    assert activated_contract["status"] == "active"

    pending_for_cancel = create_pending_contract(
        f"pending_cancel_{unique_suffix}",
        api_request,
        auth_headers,
        landlord_token,
        tenant_token,
    )
    cancelled_contract = api_request(
        "PATCH",
        f"/api/v1/admin/contracts/{pending_for_cancel['contract_id']}/status",
        step_name="admin cancel contract",
        expected_status=200,
        headers=auth_headers(admin_token),
        json={"status": "cancelled"},
    )["data"]
    assert cancelled_contract["status"] == "cancelled"

    active_for_terminate = create_active_contract(
        f"active_terminate_{unique_suffix}",
        api_request,
        auth_headers,
        landlord_token,
        tenant_token,
    )
    terminated_contract = api_request(
        "PATCH",
        f"/api/v1/admin/contracts/{active_for_terminate['contract_id']}/status",
        step_name="admin terminate contract",
        expected_status=200,
        headers=auth_headers(admin_token),
        json={"status": "terminated"},
    )["data"]
    assert terminated_contract["status"] == "terminated"

    contracts = api_request(
        "GET",
        "/api/v1/admin/contracts",
        step_name="admin list contracts",
        expected_status=200,
        headers=auth_headers(admin_token),
        params={"page": 1, "page_size": 100},
    )["data"]
    assert any(item["id"] == activated_contract["id"] for item in contracts["list"])

    invalid_contract = request_payload(
        http,
        base_url,
        "PATCH",
        f"/api/v1/admin/contracts/{terminated_contract['id']}/status",
        step_name="admin invalid contract transition",
        expected_status=400,
        headers=auth_headers(admin_token),
        json={"status": "cancelled"},
    )
    assert invalid_contract["code"] == 2402
