from __future__ import annotations

# Run:
#   cd backend
#   pytest tests/api/test_bill_flow.py -q
#
# Or in Docker:
#   cd deploy
#   docker compose exec backend pytest tests/api/test_bill_flow.py -q
#
# Or override base URL:
#   set API_BASE_URL=http://127.0.0.1:8000
#   pytest tests/api/test_bill_flow.py -q

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


def create_authenticated_users(
    unique_suffix: str,
    api_request,
) -> tuple[str, str]:
    landlord_username = f"bill_landlord_{unique_suffix}"
    tenant_username = f"bill_tenant_{unique_suffix}"
    password = "Password123!"

    landlord_register = api_request(
        "POST",
        "/api/v1/users",
        step_name="register bill landlord",
        expected_status=201,
        json={
            "username": landlord_username,
            "password": password,
            "role": "landlord",
            "email": f"{landlord_username}@example.com",
        },
    )
    assert landlord_register["data"]["username"] == landlord_username

    tenant_register = api_request(
        "POST",
        "/api/v1/users",
        step_name="register bill tenant",
        expected_status=201,
        json={
            "username": tenant_username,
            "password": password,
            "role": "tenant",
            "email": f"{tenant_username}@example.com",
        },
    )
    assert tenant_register["data"]["username"] == tenant_username

    landlord_login = api_request(
        "POST",
        "/api/v1/auth/login",
        step_name="bill landlord login",
        expected_status=200,
        json={"username": landlord_username, "password": password},
    )
    tenant_login = api_request(
        "POST",
        "/api/v1/auth/login",
        step_name="bill tenant login",
        expected_status=200,
        json={"username": tenant_username, "password": password},
    )
    return landlord_login["data"]["token"], tenant_login["data"]["token"]


def create_house_and_confirmed_appointment(
    unique_suffix: str,
    api_request,
    auth_headers,
    landlord_token: str,
    tenant_token: str,
) -> tuple[int, int]:
    create_house = api_request(
        "POST",
        "/api/v1/houses",
        step_name="bill create house",
        expected_status=201,
        headers=auth_headers(landlord_token),
        json={
            "title": f"Bill House {unique_suffix}",
            "address": f"Bill Address {unique_suffix}",
            "region": "Bill Region",
            "community": "Bill Community",
            "house_type": "1室1厅",
            "area": 58,
            "rent": 2500,
            "deposit": 2500,
            "decoration": "精装修",
            "floor": "8/18",
            "orientation": "南",
            "description": "Bill flow house",
        },
    )
    house_id = create_house["data"]["id"]

    publish_house = api_request(
        "PATCH",
        f"/api/v1/houses/{house_id}/publish",
        step_name="bill publish house",
        expected_status=200,
        headers=auth_headers(landlord_token),
    )
    assert publish_house["data"]["status"] == "listed"

    appointment_time = (datetime.now() + timedelta(days=1)).isoformat()
    create_appointment = api_request(
        "POST",
        "/api/v1/appointments",
        step_name="bill create appointment",
        expected_status=201,
        headers=auth_headers(tenant_token),
        json={
            "house_id": house_id,
            "appointment_time": appointment_time,
            "remark": "bill appointment",
        },
    )
    appointment_id = create_appointment["data"]["id"]

    confirm_appointment = api_request(
        "PATCH",
        f"/api/v1/appointments/{appointment_id}/confirm",
        step_name="bill confirm appointment",
        expected_status=200,
        headers=auth_headers(landlord_token),
    )
    assert confirm_appointment["data"]["status"] == "confirmed"
    return house_id, appointment_id


def create_contract(
    api_request,
    auth_headers,
    landlord_token: str,
    appointment_id: int,
    *,
    remark: str,
) -> int:
    start_date = (date.today() + timedelta(days=7)).isoformat()
    end_date = (date.today() + timedelta(days=372)).isoformat()
    create_contract_response = api_request(
        "POST",
        "/api/v1/contracts",
        step_name=f"create contract {remark}",
        expected_status=201,
        headers=auth_headers(landlord_token),
        json={
            "appointment_id": appointment_id,
            "start_date": start_date,
            "end_date": end_date,
            "monthly_rent": 2500,
            "deposit": 2500,
            "remark": remark,
        },
    )
    return create_contract_response["data"]["id"]


def create_bill(
    api_request,
    auth_headers,
    landlord_token: str,
    contract_id: int,
    *,
    due_date: str,
    amount: int | float,
    remark: str,
) -> dict[str, Any]:
    return api_request(
        "POST",
        "/api/v1/bills",
        step_name=f"create bill {remark}",
        expected_status=201,
        headers=auth_headers(landlord_token),
        json={
            "contract_id": contract_id,
            "bill_type": "rent",
            "amount": amount,
            "due_date": due_date,
            "remark": remark,
        },
    )


def create_active_contract(
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
    contract_id = create_contract(
        api_request,
        auth_headers,
        landlord_token,
        appointment_id,
        remark=f"active contract {unique_suffix}",
    )
    confirm_contract = api_request(
        "PATCH",
        f"/api/v1/contracts/{contract_id}/confirm",
        step_name="tenant confirm bill contract",
        expected_status=200,
        headers=auth_headers(tenant_token),
    )
    assert confirm_contract["data"]["status"] == "active"
    return {
        "house_id": house_id,
        "appointment_id": appointment_id,
        "contract_id": contract_id,
        "tenant_id": confirm_contract["data"]["tenant_id"],
        "landlord_id": confirm_contract["data"]["landlord_id"],
    }


def test_bill_flow(
    unique_suffix: str,
    api_request,
    auth_headers,
    http: requests.Session,
    base_url: str,
) -> None:
    landlord_token, tenant_token = create_authenticated_users(unique_suffix, api_request)
    contract_context = create_active_contract(
        unique_suffix,
        api_request,
        auth_headers,
        landlord_token,
        tenant_token,
    )
    contract_id = contract_context["contract_id"]

    future_bill_response = create_bill(
        api_request,
        auth_headers,
        landlord_token,
        contract_id,
        due_date=(date.today() + timedelta(days=10)).isoformat(),
        amount=2500,
        remark="future due bill",
    )
    future_bill = future_bill_response["data"]
    future_bill_id = future_bill["id"]
    assert future_bill_response["code"] == 0
    assert future_bill["status"] == "unpaid"
    assert future_bill["contract_id"] == contract_id
    assert future_bill["house_id"] == contract_context["house_id"]
    assert future_bill["tenant_id"] == contract_context["tenant_id"]
    assert future_bill["landlord_id"] == contract_context["landlord_id"]

    landlord_bills = api_request(
        "GET",
        "/api/v1/bills",
        step_name="landlord list bills",
        expected_status=200,
        headers=auth_headers(landlord_token),
        params={"page": 1, "page_size": 100},
    )
    landlord_bill = next(
        (item for item in landlord_bills["data"]["list"] if item["id"] == future_bill_id),
        None,
    )
    assert landlord_bill is not None, f"landlord bill {future_bill_id} not found: {landlord_bills!r}"

    tenant_bills = api_request(
        "GET",
        "/api/v1/bills",
        step_name="tenant list bills",
        expected_status=200,
        headers=auth_headers(tenant_token),
        params={"page": 1, "page_size": 100},
    )
    tenant_bill = next(
        (item for item in tenant_bills["data"]["list"] if item["id"] == future_bill_id),
        None,
    )
    assert tenant_bill is not None, f"tenant bill {future_bill_id} not found: {tenant_bills!r}"

    bill_detail = api_request(
        "GET",
        f"/api/v1/bills/{future_bill_id}",
        step_name="tenant get bill detail",
        expected_status=200,
        headers=auth_headers(tenant_token),
    )
    assert bill_detail["data"]["id"] == future_bill_id

    future_mark_overdue = request_payload(
        http,
        base_url,
        "PATCH",
        f"/api/v1/bills/{future_bill_id}/mark-overdue",
        step_name="mark future bill overdue",
        expected_status=400,
        headers=auth_headers(landlord_token),
    )
    assert future_mark_overdue["code"] == 2502

    overdue_bill_response = create_bill(
        api_request,
        auth_headers,
        landlord_token,
        contract_id,
        due_date=(date.today() - timedelta(days=1)).isoformat(),
        amount=2600,
        remark="past due bill",
    )
    overdue_bill = overdue_bill_response["data"]
    overdue_bill_id = overdue_bill["id"]

    mark_overdue = api_request(
        "PATCH",
        f"/api/v1/bills/{overdue_bill_id}/mark-overdue",
        step_name="landlord mark past-due bill overdue",
        expected_status=200,
        headers=auth_headers(landlord_token),
    )
    assert mark_overdue["data"]["status"] == "overdue"

    mark_overdue_again = request_payload(
        http,
        base_url,
        "PATCH",
        f"/api/v1/bills/{overdue_bill_id}/mark-overdue",
        step_name="mark overdue again",
        expected_status=400,
        headers=auth_headers(landlord_token),
    )
    assert mark_overdue_again["code"] == 2502

    cancel_bill = api_request(
        "PATCH",
        f"/api/v1/bills/{overdue_bill_id}/cancel",
        step_name="landlord cancel overdue bill",
        expected_status=200,
        headers=auth_headers(landlord_token),
    )
    assert cancel_bill["data"]["status"] == "cancelled"

    cancel_bill_again = request_payload(
        http,
        base_url,
        "PATCH",
        f"/api/v1/bills/{overdue_bill_id}/cancel",
        step_name="cancel bill again",
        expected_status=400,
        headers=auth_headers(landlord_token),
    )
    assert cancel_bill_again["code"] == 2502


def test_bill_validation_errors(
    unique_suffix: str,
    api_request,
    auth_headers,
    http: requests.Session,
    base_url: str,
) -> None:
    landlord_token, tenant_token = create_authenticated_users(f"errors_{unique_suffix}", api_request)
    active_contract = create_active_contract(
        f"errors_active_{unique_suffix}",
        api_request,
        auth_headers,
        landlord_token,
        tenant_token,
    )
    _, pending_appointment_id = create_house_and_confirmed_appointment(
        f"errors_pending_{unique_suffix}",
        api_request,
        auth_headers,
        landlord_token,
        tenant_token,
    )
    pending_contract_id = create_contract(
        api_request,
        auth_headers,
        landlord_token,
        pending_appointment_id,
        remark=f"pending contract {unique_suffix}",
    )
    tenant_create_bill = request_payload(
        http,
        base_url,
        "POST",
        "/api/v1/bills",
        step_name="tenant create bill",
        expected_status=404,
        headers=auth_headers(tenant_token),
        json={
            "contract_id": active_contract["contract_id"],
            "bill_type": "rent",
            "amount": 2500,
            "due_date": (date.today() + timedelta(days=10)).isoformat(),
            "remark": "tenant create",
        },
    )
    assert tenant_create_bill["code"] == 2401

    amount_zero = request_payload(
        http,
        base_url,
        "POST",
        "/api/v1/bills",
        step_name="create bill with amount zero",
        expected_status=400,
        headers=auth_headers(landlord_token),
        json={
            "contract_id": active_contract["contract_id"],
            "bill_type": "rent",
            "amount": 0,
            "due_date": (date.today() + timedelta(days=10)).isoformat(),
            "remark": "bad amount",
        },
    )
    assert amount_zero["code"] == 3001

    invalid_bill_type = request_payload(
        http,
        base_url,
        "POST",
        "/api/v1/bills",
        step_name="create bill with invalid type",
        expected_status=400,
        headers=auth_headers(landlord_token),
        json={
            "contract_id": active_contract["contract_id"],
            "bill_type": "water",
            "amount": 100,
            "due_date": (date.today() + timedelta(days=10)).isoformat(),
            "remark": "bad type",
        },
    )
    assert invalid_bill_type["code"] == 3001

    invalid_due_date = request_payload(
        http,
        base_url,
        "POST",
        "/api/v1/bills",
        step_name="create bill with invalid due date",
        expected_status=400,
        headers=auth_headers(landlord_token),
        json={
            "contract_id": active_contract["contract_id"],
            "bill_type": "rent",
            "amount": 100,
            "due_date": "2026/05/01",
            "remark": "bad date",
        },
    )
    assert invalid_due_date["code"] == 3001

    extra_house_id = request_payload(
        http,
        base_url,
        "POST",
        "/api/v1/bills",
        step_name="create bill with extra house id",
        expected_status=400,
        headers=auth_headers(landlord_token),
        json={
            "contract_id": active_contract["contract_id"],
            "bill_type": "rent",
            "amount": 100,
            "due_date": (date.today() + timedelta(days=10)).isoformat(),
            "remark": "extra field",
            "house_id": 999999,
        },
    )
    assert extra_house_id["code"] == 3001

    pending_contract_bill = request_payload(
        http,
        base_url,
        "POST",
        "/api/v1/bills",
        step_name="create bill with pending contract",
        expected_status=400,
        headers=auth_headers(landlord_token),
        json={
            "contract_id": pending_contract_id,
            "bill_type": "rent",
            "amount": 100,
            "due_date": (date.today() + timedelta(days=10)).isoformat(),
            "remark": "pending contract bill",
        },
    )
    assert pending_contract_bill["code"] == 2503
