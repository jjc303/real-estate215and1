from __future__ import annotations

# Run:
#   cd backend
#   pytest tests/api/test_payment_flow.py -q

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
            f"expected HTTP {expected_status}, got HTTP {response.status_code}; "
            f"body={response.text!r}"
        ) from exc

    if response.status_code != expected_status:
        raise AssertionError(
            f"{step_name} failed: {method} {base_url}{path} expected HTTP {expected_status}, "
            f"got HTTP {response.status_code}; response={payload!r}"
        )
    return payload


def create_authenticated_users(unique_suffix: str, api_request) -> tuple[str, str]:
    landlord_username = f"payment_landlord_{unique_suffix}"
    tenant_username = f"payment_tenant_{unique_suffix}"
    password = "Password123!"

    api_request(
        "POST",
        "/api/v1/users",
        step_name="register payment landlord",
        expected_status=201,
        json={
            "username": landlord_username,
            "password": password,
            "role": "landlord",
            "email": f"{landlord_username}@example.com",
        },
    )
    api_request(
        "POST",
        "/api/v1/users",
        step_name="register payment tenant",
        expected_status=201,
        json={
            "username": tenant_username,
            "password": password,
            "role": "tenant",
            "email": f"{tenant_username}@example.com",
        },
    )

    landlord_login = api_request(
        "POST",
        "/api/v1/auth/login",
        step_name="payment landlord login",
        expected_status=200,
        json={"username": landlord_username, "password": password},
    )
    tenant_login = api_request(
        "POST",
        "/api/v1/auth/login",
        step_name="payment tenant login",
        expected_status=200,
        json={"username": tenant_username, "password": password},
    )
    return landlord_login["data"]["token"], tenant_login["data"]["token"]


def create_outsider_token(unique_suffix: str, api_request) -> str:
    username = f"payment_outsider_{unique_suffix}"
    password = "Password123!"
    api_request(
        "POST",
        "/api/v1/users",
        step_name="register payment outsider",
        expected_status=201,
        json={
            "username": username,
            "password": password,
            "role": "tenant",
            "email": f"{username}@example.com",
        },
    )
    outsider_login = api_request(
        "POST",
        "/api/v1/auth/login",
        step_name="payment outsider login",
        expected_status=200,
        json={"username": username, "password": password},
    )
    return outsider_login["data"]["token"]


def create_admin_token(unique_suffix: str, api_request) -> str:
    username = f"payment_admin_{unique_suffix}"
    password = "Password123!"
    api_request(
        "POST",
        "/api/v1/users",
        step_name="register payment admin",
        expected_status=201,
        json={
            "username": username,
            "password": password,
            "role": "admin",
            "email": f"{username}@example.com",
        },
    )
    admin_login = api_request(
        "POST",
        "/api/v1/auth/login",
        step_name="payment admin login",
        expected_status=200,
        json={"username": username, "password": password},
    )
    return admin_login["data"]["token"]


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
        step_name="payment create house",
        expected_status=201,
        headers=auth_headers(landlord_token),
        json={
            "title": f"Payment House {unique_suffix}",
            "address": f"Payment Address {unique_suffix}",
            "region": "Payment Region",
            "community": "Payment Community",
            "house_type": "1室1厅",
            "area": 62,
            "rent": 2600,
            "deposit": 2600,
            "decoration": "精装修",
            "floor": "10/18",
            "orientation": "南",
            "description": "Payment flow house",
        },
    )
    house_id = create_house["data"]["id"]

    publish_house = api_request(
        "PATCH",
        f"/api/v1/houses/{house_id}/publish",
        step_name="payment publish house",
        expected_status=200,
        headers=auth_headers(landlord_token),
    )
    assert publish_house["data"]["status"] == "listed"

    appointment_time = (datetime.now() + timedelta(days=1)).isoformat()
    create_appointment = api_request(
        "POST",
        "/api/v1/appointments",
        step_name="payment create appointment",
        expected_status=201,
        headers=auth_headers(tenant_token),
        json={
            "house_id": house_id,
            "appointment_time": appointment_time,
            "remark": "payment appointment",
        },
    )
    appointment_id = create_appointment["data"]["id"]

    confirm_appointment = api_request(
        "PATCH",
        f"/api/v1/appointments/{appointment_id}/confirm",
        step_name="payment confirm appointment",
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
        step_name=f"create payment contract {remark}",
        expected_status=201,
        headers=auth_headers(landlord_token),
        json={
            "appointment_id": appointment_id,
            "start_date": start_date,
            "end_date": end_date,
            "monthly_rent": 2600,
            "deposit": 2600,
            "remark": remark,
        },
    )
    return create_contract_response["data"]["id"]


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
        remark=f"payment active contract {unique_suffix}",
    )
    confirm_contract = api_request(
        "PATCH",
        f"/api/v1/contracts/{contract_id}/confirm",
        step_name="tenant confirm payment contract",
        expected_status=200,
        headers=auth_headers(tenant_token),
    )
    assert confirm_contract["data"]["status"] == "active"
    return {
        "house_id": house_id,
        "contract_id": contract_id,
        "tenant_id": confirm_contract["data"]["tenant_id"],
        "landlord_id": confirm_contract["data"]["landlord_id"],
    }


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
        step_name=f"create payment bill {remark}",
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


def list_notifications(api_request, auth_headers, token: str) -> list[dict[str, Any]]:
    response = api_request(
        "GET",
        "/api/v1/notifications",
        step_name="list payment notifications",
        expected_status=200,
        headers=auth_headers(token),
        params={"page": 1, "page_size": 100},
    )
    return response["data"]["list"]


def test_payment_flow(
    unique_suffix: str,
    api_request,
    auth_headers,
    http: requests.Session,
    base_url: str,
) -> None:
    landlord_token, tenant_token = create_authenticated_users(unique_suffix, api_request)
    outsider_token = create_outsider_token(unique_suffix, api_request)
    admin_token = create_admin_token(unique_suffix, api_request)

    unpaid_contract = create_active_contract(
        f"unpaid_{unique_suffix}",
        api_request,
        auth_headers,
        landlord_token,
        tenant_token,
    )
    unpaid_bill = create_bill(
        api_request,
        auth_headers,
        landlord_token,
        unpaid_contract["contract_id"],
        due_date=(date.today() + timedelta(days=10)).isoformat(),
        amount=2600,
        remark="unpaid bill",
    )["data"]

    pay_unpaid = api_request(
        "POST",
        "/api/v1/payments",
        step_name="tenant pay unpaid bill",
        expected_status=201,
        headers=auth_headers(tenant_token),
        json={
            "bill_id": unpaid_bill["id"],
            "amount": 2600,
            "payment_method": "mock",
            "remark": "mock payment",
        },
    )
    payment = pay_unpaid["data"]
    assert pay_unpaid["code"] == 0
    assert payment["status"] == "success"
    assert payment["payment_method"] == "mock"
    assert payment["bill_id"] == unpaid_bill["id"]
    assert payment["contract_id"] == unpaid_contract["contract_id"]
    assert payment["house_id"] == unpaid_contract["house_id"]
    assert payment["tenant_id"] == unpaid_contract["tenant_id"]
    assert payment["landlord_id"] == unpaid_contract["landlord_id"]
    datetime.fromisoformat(payment["paid_at"])

    tenant_notifications = list_notifications(api_request, auth_headers, tenant_token)
    landlord_notifications = list_notifications(api_request, auth_headers, landlord_token)
    tenant_payment_notification = next(
        (item for item in tenant_notifications if item["source_type"] == "bill" and item["source_id"] == unpaid_bill["id"]),
        None,
    )
    landlord_payment_notification = next(
        (item for item in landlord_notifications if item["source_type"] == "bill" and item["source_id"] == unpaid_bill["id"]),
        None,
    )
    assert tenant_payment_notification is not None, f"tenant payment notification missing: {tenant_notifications!r}"
    assert landlord_payment_notification is not None, f"landlord payment notification missing: {landlord_notifications!r}"
    assert tenant_payment_notification["title"] == "Payment successful"
    assert landlord_payment_notification["title"] == "Bill paid"

    paid_bill_detail = api_request(
        "GET",
        f"/api/v1/bills/{unpaid_bill['id']}",
        step_name="get paid bill detail",
        expected_status=200,
        headers=auth_headers(tenant_token),
    )
    assert paid_bill_detail["data"]["status"] == "paid"

    landlord_payments = api_request(
        "GET",
        "/api/v1/payments",
        step_name="landlord list payments",
        expected_status=200,
        headers=auth_headers(landlord_token),
        params={"page": 1, "page_size": 100},
    )
    landlord_payment = next(
        (item for item in landlord_payments["data"]["list"] if item["id"] == payment["id"]),
        None,
    )
    assert landlord_payment is not None, f"landlord payment {payment['id']} not found: {landlord_payments!r}"

    tenant_payments = api_request(
        "GET",
        "/api/v1/payments",
        step_name="tenant list payments",
        expected_status=200,
        headers=auth_headers(tenant_token),
        params={"page": 1, "page_size": 100},
    )
    tenant_payment = next(
        (item for item in tenant_payments["data"]["list"] if item["id"] == payment["id"]),
        None,
    )
    assert tenant_payment is not None, f"tenant payment {payment['id']} not found: {tenant_payments!r}"

    payment_detail = api_request(
        "GET",
        f"/api/v1/payments/{payment['id']}",
        step_name="tenant get payment detail",
        expected_status=200,
        headers=auth_headers(tenant_token),
    )
    assert payment_detail["data"]["id"] == payment["id"]

    duplicate_payment = request_payload(
        http,
        base_url,
        "POST",
        "/api/v1/payments",
        step_name="duplicate payment",
        expected_status=409,
        headers=auth_headers(tenant_token),
        json={
            "bill_id": unpaid_bill["id"],
            "amount": 2600,
            "payment_method": "mock",
        },
    )
    assert duplicate_payment["code"] == 2604

    landlord_pay = request_payload(
        http,
        base_url,
        "POST",
        "/api/v1/payments",
        step_name="landlord cannot pay bill",
        expected_status=403,
        headers=auth_headers(landlord_token),
        json={
            "bill_id": unpaid_bill["id"],
            "amount": 2600,
            "payment_method": "mock",
        },
    )
    assert landlord_pay["code"] == FORBIDDEN_CODE

    admin_pay = request_payload(
        http,
        base_url,
        "POST",
        "/api/v1/payments",
        step_name="admin cannot pay bill",
        expected_status=403,
        headers=auth_headers(admin_token),
        json={
            "bill_id": unpaid_bill["id"],
            "amount": 2600,
            "payment_method": "mock",
        },
    )
    assert admin_pay["code"] == FORBIDDEN_CODE

    outsider_detail = request_payload(
        http,
        base_url,
        "GET",
        f"/api/v1/payments/{payment['id']}",
        step_name="outsider get payment detail",
        expected_status=404,
        headers=auth_headers(outsider_token),
    )
    assert outsider_detail["code"] == 2601

    overdue_contract = create_active_contract(
        f"overdue_{unique_suffix}",
        api_request,
        auth_headers,
        landlord_token,
        tenant_token,
    )
    overdue_bill = create_bill(
        api_request,
        auth_headers,
        landlord_token,
        overdue_contract["contract_id"],
        due_date=(date.today() - timedelta(days=1)).isoformat(),
        amount=2600,
        remark="overdue bill",
    )["data"]
    assert date.fromisoformat(overdue_bill["due_date"]) < date.today()

    overdue_mark = api_request(
        "PATCH",
        f"/api/v1/bills/{overdue_bill['id']}/mark-overdue",
        step_name="mark bill overdue before payment",
        expected_status=200,
        headers=auth_headers(landlord_token),
    )
    assert overdue_mark["data"]["status"] == "overdue"

    pay_overdue = api_request(
        "POST",
        "/api/v1/payments",
        step_name="tenant pay overdue bill",
        expected_status=201,
        headers=auth_headers(tenant_token),
        json={
            "bill_id": overdue_bill["id"],
            "amount": 2600,
            "payment_method": "offline",
            "remark": "offline payment",
        },
    )
    assert pay_overdue["data"]["status"] == "success"
    assert pay_overdue["data"]["payment_method"] == "offline"

    overdue_paid_detail = api_request(
        "GET",
        f"/api/v1/bills/{overdue_bill['id']}",
        step_name="get overdue paid bill detail",
        expected_status=200,
        headers=auth_headers(tenant_token),
    )
    assert overdue_paid_detail["data"]["status"] == "paid"


def test_payment_validation_errors(
    unique_suffix: str,
    api_request,
    auth_headers,
    http: requests.Session,
    base_url: str,
) -> None:
    landlord_token, tenant_token = create_authenticated_users(f"errors_{unique_suffix}", api_request)
    outsider_token = create_outsider_token(f"errors_{unique_suffix}", api_request)

    mismatch_contract = create_active_contract(
        f"mismatch_{unique_suffix}",
        api_request,
        auth_headers,
        landlord_token,
        tenant_token,
    )
    mismatch_bill = create_bill(
        api_request,
        auth_headers,
        landlord_token,
        mismatch_contract["contract_id"],
        due_date=(date.today() + timedelta(days=10)).isoformat(),
        amount=2600,
        remark="mismatch bill",
    )["data"]
    amount_mismatch = request_payload(
        http,
        base_url,
        "POST",
        "/api/v1/payments",
        step_name="payment amount mismatch",
        expected_status=400,
        headers=auth_headers(tenant_token),
        json={
            "bill_id": mismatch_bill["id"],
            "amount": 2500,
            "payment_method": "mock",
        },
    )
    assert amount_mismatch["code"] == 2603

    outsider_pay = request_payload(
        http,
        base_url,
        "POST",
        "/api/v1/payments",
        step_name="outsider tenant cannot pay bill",
        expected_status=403,
        headers=auth_headers(outsider_token),
        json={
            "bill_id": mismatch_bill["id"],
            "amount": 2600,
            "payment_method": "mock",
        },
    )
    assert outsider_pay["code"] == FORBIDDEN_CODE

    landlord_pay = request_payload(
        http,
        base_url,
        "POST",
        "/api/v1/payments",
        step_name="landlord cannot pay bill",
        expected_status=403,
        headers=auth_headers(landlord_token),
        json={
            "bill_id": mismatch_bill["id"],
            "amount": 2600,
            "payment_method": "mock",
        },
    )
    assert landlord_pay["code"] == FORBIDDEN_CODE

    missing_bill = request_payload(
        http,
        base_url,
        "POST",
        "/api/v1/payments",
        step_name="pay missing bill",
        expected_status=404,
        headers=auth_headers(tenant_token),
        json={
            "bill_id": 99999999,
            "amount": 2600,
            "payment_method": "mock",
        },
    )
    assert missing_bill["code"] == 2501

    cancelled_contract = create_active_contract(
        f"cancelled_{unique_suffix}",
        api_request,
        auth_headers,
        landlord_token,
        tenant_token,
    )
    cancelled_bill = create_bill(
        api_request,
        auth_headers,
        landlord_token,
        cancelled_contract["contract_id"],
        due_date=(date.today() + timedelta(days=10)).isoformat(),
        amount=2600,
        remark="cancelled bill",
    )["data"]
    cancel_bill = api_request(
        "PATCH",
        f"/api/v1/bills/{cancelled_bill['id']}/cancel",
        step_name="cancel bill before payment attempt",
        expected_status=200,
        headers=auth_headers(landlord_token),
    )
    assert cancel_bill["data"]["status"] == "cancelled"

    pay_cancelled = request_payload(
        http,
        base_url,
        "POST",
        "/api/v1/payments",
        step_name="pay cancelled bill",
        expected_status=400,
        headers=auth_headers(tenant_token),
        json={
            "bill_id": cancelled_bill["id"],
            "amount": 2600,
            "payment_method": "mock",
        },
    )
    assert pay_cancelled["code"] == 2602
