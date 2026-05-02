from __future__ import annotations

# Run:
#   cd backend
#   pytest tests/api/test_repair_flow.py -q

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


def create_user_and_login(unique_suffix: str, role: str, api_request) -> str:
    username = f"{role}_{unique_suffix}"
    password = "Password123!"
    api_request(
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
    return login["data"]["token"]


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
        step_name="create repair house",
        expected_status=201,
        headers=auth_headers(landlord_token),
        json={
            "title": f"Repair House {unique_suffix}",
            "address": f"Repair Address {unique_suffix}",
            "region": "Repair Region",
            "community": "Repair Community",
            "house_type": "1室1厅",
            "area": 60,
            "rent": 2400,
            "deposit": 2400,
            "decoration": "精装",
            "floor": "12/18",
            "orientation": "南",
            "description": "repair flow house",
        },
    )
    house_id = house_response["data"]["id"]

    api_request(
        "PATCH",
        f"/api/v1/houses/{house_id}/publish",
        step_name="publish repair house",
        expected_status=200,
        headers=auth_headers(landlord_token),
    )

    appointment_response = api_request(
        "POST",
        "/api/v1/appointments",
        step_name="create repair appointment",
        expected_status=201,
        headers=auth_headers(tenant_token),
        json={
            "house_id": house_id,
            "appointment_time": (datetime.now() + timedelta(days=1)).isoformat(),
            "remark": "repair appointment",
        },
    )
    appointment_id = appointment_response["data"]["id"]

    api_request(
        "PATCH",
        f"/api/v1/appointments/{appointment_id}/confirm",
        step_name="confirm repair appointment",
        expected_status=200,
        headers=auth_headers(landlord_token),
    )

    contract_response = api_request(
        "POST",
        "/api/v1/contracts",
        step_name="create repair contract",
        expected_status=201,
        headers=auth_headers(landlord_token),
        json={
            "appointment_id": appointment_id,
            "start_date": (date.today() + timedelta(days=7)).isoformat(),
            "end_date": (date.today() + timedelta(days=372)).isoformat(),
            "monthly_rent": 2400,
            "deposit": 2400,
            "remark": "repair contract",
        },
    )
    contract_id = contract_response["data"]["id"]

    confirm_response = api_request(
        "PATCH",
        f"/api/v1/contracts/{contract_id}/confirm",
        step_name="confirm repair contract",
        expected_status=200,
        headers=auth_headers(tenant_token),
    )

    return {
        "house_id": house_id,
        "contract_id": contract_id,
        "tenant_id": confirm_response["data"]["tenant_id"],
        "landlord_id": confirm_response["data"]["landlord_id"],
    }


def create_repair(api_request, auth_headers, tenant_token: str, contract_id: int, description: str) -> dict[str, Any]:
    return api_request(
        "POST",
        "/api/v1/repairs",
        step_name=f"create repair {description}",
        expected_status=201,
        headers=auth_headers(tenant_token),
        json={
            "contract_id": contract_id,
            "description": description,
        },
    )


def test_repair_flow(
    unique_suffix: str,
    api_request,
    auth_headers,
    http: requests.Session,
    base_url: str,
) -> None:
    landlord_token = create_user_and_login(f"landlord_{unique_suffix}", "landlord", api_request)
    tenant_token = create_user_and_login(f"tenant_{unique_suffix}", "tenant", api_request)
    admin_token = create_user_and_login(f"admin_{unique_suffix}", "admin", api_request)
    outsider_token = create_user_and_login(f"outsider_{unique_suffix}", "tenant", api_request)

    active_contract = create_active_contract(
        unique_suffix,
        api_request,
        auth_headers,
        landlord_token,
        tenant_token,
    )

    created = create_repair(
        api_request,
        auth_headers,
        tenant_token,
        active_contract["contract_id"],
        "  kitchen sink is leaking  ",
    )["data"]
    assert created["status"] == "pending"
    assert created["description"] == "kitchen sink is leaking"

    processed = api_request(
        "PATCH",
        f"/api/v1/repairs/{created['id']}/process",
        step_name="process repair",
        expected_status=200,
        headers=auth_headers(landlord_token),
    )["data"]
    assert processed["status"] == "processing"
    assert processed["processed_at"] is not None

    completed = api_request(
        "PATCH",
        f"/api/v1/repairs/{created['id']}/complete",
        step_name="complete repair",
        expected_status=200,
        headers=auth_headers(landlord_token),
    )["data"]
    assert completed["status"] == "completed"
    assert completed["completed_at"] is not None

    reopened = api_request(
        "PATCH",
        f"/api/v1/repairs/{created['id']}/reopen",
        step_name="reopen completed repair",
        expected_status=200,
        headers=auth_headers(tenant_token),
    )["data"]
    assert reopened["status"] == "reopened"
    assert reopened["reopened_at"] is not None

    api_request(
        "PATCH",
        f"/api/v1/repairs/{created['id']}/process",
        step_name="reprocess reopened repair",
        expected_status=200,
        headers=auth_headers(landlord_token),
    )
    second_completed = api_request(
        "PATCH",
        f"/api/v1/repairs/{created['id']}/complete",
        step_name="recomplete reopened repair",
        expected_status=200,
        headers=auth_headers(landlord_token),
    )["data"]
    assert second_completed["status"] == "completed"

    closed = api_request(
        "PATCH",
        f"/api/v1/repairs/{created['id']}/close",
        step_name="close repair",
        expected_status=200,
        headers=auth_headers(tenant_token),
    )["data"]
    assert closed["status"] == "closed"
    assert closed["closed_at"] is not None

    reopened_from_closed = api_request(
        "PATCH",
        f"/api/v1/repairs/{created['id']}/reopen",
        step_name="reopen closed repair",
        expected_status=200,
        headers=auth_headers(tenant_token),
    )["data"]
    assert reopened_from_closed["status"] == "reopened"

    rejected_repair = create_repair(
        api_request,
        auth_headers,
        tenant_token,
        active_contract["contract_id"],
        "need to check window frame",
    )["data"]
    rejected = api_request(
        "PATCH",
        f"/api/v1/repairs/{rejected_repair['id']}/reject",
        step_name="reject repair",
        expected_status=200,
        headers=auth_headers(landlord_token),
    )["data"]
    assert rejected["status"] == "rejected"
    assert rejected["rejected_at"] is not None

    outsider_detail = request_payload(
        http,
        base_url,
        "GET",
        f"/api/v1/repairs/{created['id']}",
        step_name="outsider repair detail",
        expected_status=404,
        headers=auth_headers(outsider_token),
    )
    assert outsider_detail["code"] == 2701

    admin_process = api_request(
        "PATCH",
        f"/api/v1/repairs/{created['id']}/process",
        step_name="admin process repair",
        expected_status=200,
        headers=auth_headers(admin_token),
    )
    assert admin_process["data"]["status"] == "processing"

    tenant_list = api_request(
        "GET",
        "/api/v1/repairs",
        step_name="tenant list repairs",
        expected_status=200,
        headers=auth_headers(tenant_token),
        params={"page": 1, "page_size": 100},
    )
    assert any(item["id"] == created["id"] for item in tenant_list["data"]["list"])

    landlord_list = api_request(
        "GET",
        "/api/v1/repairs",
        step_name="landlord list repairs",
        expected_status=200,
        headers=auth_headers(landlord_token),
        params={"page": 1, "page_size": 100, "status": "processing"},
    )
    assert any(item["id"] == created["id"] for item in landlord_list["data"]["list"])

    admin_list = api_request(
        "GET",
        "/api/v1/repairs",
        step_name="admin list repairs",
        expected_status=200,
        headers=auth_headers(admin_token),
        params={"page": 1, "page_size": 100},
    )
    assert any(item["id"] == created["id"] for item in admin_list["data"]["list"])


def test_repair_validation_and_permissions(
    unique_suffix: str,
    api_request,
    auth_headers,
    http: requests.Session,
    base_url: str,
) -> None:
    landlord_token = create_user_and_login(f"landlord_err_{unique_suffix}", "landlord", api_request)
    tenant_token = create_user_and_login(f"tenant_err_{unique_suffix}", "tenant", api_request)
    other_tenant_token = create_user_and_login(f"tenant_other_{unique_suffix}", "tenant", api_request)

    active_contract = create_active_contract(
        f"errors_{unique_suffix}",
        api_request,
        auth_headers,
        landlord_token,
        tenant_token,
    )

    landlord_create = request_payload(
        http,
        base_url,
        "POST",
        "/api/v1/repairs",
        step_name="landlord create repair",
        expected_status=403,
        headers=auth_headers(landlord_token),
        json={
            "contract_id": active_contract["contract_id"],
            "description": "landlord should not create",
        },
    )
    assert landlord_create["code"] == 1004

    not_owner_create = request_payload(
        http,
        base_url,
        "POST",
        "/api/v1/repairs",
        step_name="other tenant create repair",
        expected_status=404,
        headers=auth_headers(other_tenant_token),
        json={
            "contract_id": active_contract["contract_id"],
            "description": "not owner",
        },
    )
    assert not_owner_create["code"] == 2401

    repair = create_repair(
        api_request,
        auth_headers,
        tenant_token,
        active_contract["contract_id"],
        "air conditioner issue",
    )["data"]

    tenant_process = request_payload(
        http,
        base_url,
        "PATCH",
        f"/api/v1/repairs/{repair['id']}/process",
        step_name="tenant process repair",
        expected_status=403,
        headers=auth_headers(tenant_token),
    )
    assert tenant_process["code"] == 1004

    landlord_close = request_payload(
        http,
        base_url,
        "PATCH",
        f"/api/v1/repairs/{repair['id']}/close",
        step_name="landlord close repair",
        expected_status=403,
        headers=auth_headers(landlord_token),
    )
    assert landlord_close["code"] == 1004

    invalid_complete = request_payload(
        http,
        base_url,
        "PATCH",
        f"/api/v1/repairs/{repair['id']}/complete",
        step_name="complete pending repair",
        expected_status=400,
        headers=auth_headers(landlord_token),
    )
    assert invalid_complete["code"] == 2702

    api_request(
        "PATCH",
        f"/api/v1/repairs/{repair['id']}/process",
        step_name="process repair for invalid close",
        expected_status=200,
        headers=auth_headers(landlord_token),
    )
    invalid_close = request_payload(
        http,
        base_url,
        "PATCH",
        f"/api/v1/repairs/{repair['id']}/close",
        step_name="close processing repair",
        expected_status=400,
        headers=auth_headers(tenant_token),
    )
    assert invalid_close["code"] == 2702

    closed_contract = create_active_contract(
        f"closed_contract_{unique_suffix}",
        api_request,
        auth_headers,
        landlord_token,
        tenant_token,
    )
    api_request(
        "PATCH",
        f"/api/v1/contracts/{closed_contract['contract_id']}/terminate",
        step_name="terminate contract",
        expected_status=200,
        headers=auth_headers(landlord_token),
    )
    inactive_contract_create = request_payload(
        http,
        base_url,
        "POST",
        "/api/v1/repairs",
        step_name="create repair on inactive contract",
        expected_status=400,
        headers=auth_headers(tenant_token),
        json={
            "contract_id": closed_contract["contract_id"],
            "description": "inactive contract repair",
        },
    )
    assert inactive_contract_create["code"] == 2703

    rejected_repair = create_repair(
        api_request,
        auth_headers,
        tenant_token,
        active_contract["contract_id"],
        "door handle issue",
    )["data"]
    api_request(
        "PATCH",
        f"/api/v1/repairs/{rejected_repair['id']}/reject",
        step_name="reject repair for invalid process",
        expected_status=200,
        headers=auth_headers(landlord_token),
    )
    rejected_process = request_payload(
        http,
        base_url,
        "PATCH",
        f"/api/v1/repairs/{rejected_repair['id']}/process",
        step_name="process rejected repair",
        expected_status=400,
        headers=auth_headers(landlord_token),
    )
    assert rejected_process["code"] == 2702

    closable_repair = create_repair(
        api_request,
        auth_headers,
        tenant_token,
        active_contract["contract_id"],
        "bathroom light issue",
    )["data"]
    api_request(
        "PATCH",
        f"/api/v1/repairs/{closable_repair['id']}/process",
        step_name="process repair before close cycle",
        expected_status=200,
        headers=auth_headers(landlord_token),
    )
    api_request(
        "PATCH",
        f"/api/v1/repairs/{closable_repair['id']}/complete",
        step_name="complete repair before close cycle",
        expected_status=200,
        headers=auth_headers(landlord_token),
    )
    api_request(
        "PATCH",
        f"/api/v1/repairs/{closable_repair['id']}/close",
        step_name="close repair once",
        expected_status=200,
        headers=auth_headers(tenant_token),
    )
    close_again = request_payload(
        http,
        base_url,
        "PATCH",
        f"/api/v1/repairs/{closable_repair['id']}/close",
        step_name="close repair twice",
        expected_status=400,
        headers=auth_headers(tenant_token),
    )
    assert close_again["code"] == 2702
