from __future__ import annotations

# Run:
#   cd backend
#   pytest tests/api/test_statistics_flow.py -q

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


def create_user_and_login(
    unique_suffix: str,
    role: str,
    api_request,
    *,
    status: str = "active",
) -> tuple[int, str]:
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
            "status": status,
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


def create_house(
    unique_suffix: str,
    api_request,
    auth_headers,
    landlord_token: str,
    *,
    title_prefix: str,
) -> int:
    response = api_request(
        "POST",
        "/api/v1/houses",
        step_name=f"create house {title_prefix}",
        expected_status=201,
        headers=auth_headers(landlord_token),
        json={
            "title": f"{title_prefix} {unique_suffix}",
            "address": f"{title_prefix} Address {unique_suffix}",
            "region": "Statistics Region",
            "community": "Statistics Community",
            "house_type": "1室1厅",
            "area": 66,
            "rent": 2600,
            "deposit": 2600,
            "decoration": "精装",
            "floor": "9/18",
            "orientation": "南",
            "description": "statistics house",
        },
    )
    return response["data"]["id"]


def publish_house(api_request, auth_headers, landlord_token: str, house_id: int) -> None:
    api_request(
        "PATCH",
        f"/api/v1/houses/{house_id}/publish",
        step_name="publish house",
        expected_status=200,
        headers=auth_headers(landlord_token),
    )


def create_active_contract(
    unique_suffix: str,
    api_request,
    auth_headers,
    landlord_token: str,
    tenant_token: str,
) -> dict[str, int]:
    house_id = create_house(
        unique_suffix,
        api_request,
        auth_headers,
        landlord_token,
        title_prefix="Statistics Active House",
    )
    publish_house(api_request, auth_headers, landlord_token, house_id)

    appointment = api_request(
        "POST",
        "/api/v1/appointments",
        step_name="create statistics appointment",
        expected_status=201,
        headers=auth_headers(tenant_token),
        json={
            "house_id": house_id,
            "appointment_time": (datetime.now() + timedelta(days=1)).isoformat(),
            "remark": "statistics appointment",
        },
    )["data"]

    api_request(
        "PATCH",
        f"/api/v1/appointments/{appointment['id']}/confirm",
        step_name="confirm statistics appointment",
        expected_status=200,
        headers=auth_headers(landlord_token),
    )

    contract = api_request(
        "POST",
        "/api/v1/contracts",
        step_name="create statistics contract",
        expected_status=201,
        headers=auth_headers(landlord_token),
        json={
            "appointment_id": appointment["id"],
            "start_date": (date.today() + timedelta(days=7)).isoformat(),
            "end_date": (date.today() + timedelta(days=372)).isoformat(),
            "monthly_rent": 2600,
            "deposit": 2600,
            "remark": "statistics contract",
        },
    )["data"]

    confirmed = api_request(
        "PATCH",
        f"/api/v1/contracts/{contract['id']}/confirm",
        step_name="confirm statistics contract",
        expected_status=200,
        headers=auth_headers(tenant_token),
    )["data"]

    return {
        "house_id": house_id,
        "contract_id": contract["id"],
        "tenant_id": confirmed["tenant_id"],
        "landlord_id": confirmed["landlord_id"],
    }


def test_statistics_empty_and_non_admin_forbidden(
    unique_suffix: str,
    api_request,
    auth_headers,
    http: requests.Session,
    base_url: str,
) -> None:
    _, admin_token = create_user_and_login(f"admin_empty_{unique_suffix}", "admin", api_request)
    _, tenant_token = create_user_and_login(f"tenant_empty_{unique_suffix}", "tenant", api_request)
    _, landlord_token = create_user_and_login(f"landlord_empty_{unique_suffix}", "landlord", api_request)

    house_stats = api_request(
        "GET",
        "/api/v1/statistics/house-utilization",
        step_name="empty house stats",
        expected_status=200,
        headers=auth_headers(admin_token),
    )["data"]
    assert house_stats["total_houses"] >= 0
    assert house_stats["occupied_houses"] >= 0
    assert house_stats["utilization_rate"] >= 0.0

    rent_income = api_request(
        "GET",
        "/api/v1/statistics/rent-income",
        step_name="empty rent income",
        expected_status=200,
        headers=auth_headers(admin_token),
    )["data"]
    assert rent_income["total_income"] >= 0.0
    assert isinstance(rent_income["monthly_income"], list)

    active_users = api_request(
        "GET",
        "/api/v1/statistics/active-users",
        step_name="empty active users",
        expected_status=200,
        headers=auth_headers(admin_token),
    )["data"]
    assert active_users["active_user_count"] >= 3

    complaint_repair = api_request(
        "GET",
        "/api/v1/statistics/complaint-repair-count",
        step_name="empty complaint repair",
        expected_status=200,
        headers=auth_headers(admin_token),
    )["data"]
    assert complaint_repair["repair_count"] >= 0
    assert complaint_repair["complaint_count"] >= 0

    tenant_forbidden = request_payload(
        http,
        base_url,
        "GET",
        "/api/v1/statistics/house-utilization",
        step_name="tenant statistics forbidden",
        expected_status=403,
        headers=auth_headers(tenant_token),
    )
    assert tenant_forbidden["code"] == 1004

    landlord_forbidden = request_payload(
        http,
        base_url,
        "GET",
        "/api/v1/statistics/rent-income",
        step_name="landlord statistics forbidden",
        expected_status=403,
        headers=auth_headers(landlord_token),
    )
    assert landlord_forbidden["code"] == 1004


def test_statistics_aggregations(
    unique_suffix: str,
    api_request,
    auth_headers,
) -> None:
    _, admin_token = create_user_and_login(f"admin_stats_{unique_suffix}", "admin", api_request)
    _, landlord_token = create_user_and_login(f"landlord_stats_{unique_suffix}", "landlord", api_request)
    _, tenant_token = create_user_and_login(f"tenant_stats_{unique_suffix}", "tenant", api_request)

    baseline_house_stats = api_request(
        "GET",
        "/api/v1/statistics/house-utilization",
        step_name="baseline house utilization",
        expected_status=200,
        headers=auth_headers(admin_token),
    )["data"]
    baseline_rent_income = api_request(
        "GET",
        "/api/v1/statistics/rent-income",
        step_name="baseline rent income",
        expected_status=200,
        headers=auth_headers(admin_token),
    )["data"]
    baseline_active_users = api_request(
        "GET",
        "/api/v1/statistics/active-users",
        step_name="baseline active users",
        expected_status=200,
        headers=auth_headers(admin_token),
    )["data"]
    baseline_complaint_repair = api_request(
        "GET",
        "/api/v1/statistics/complaint-repair-count",
        step_name="baseline complaint repair count",
        expected_status=200,
        headers=auth_headers(admin_token),
    )["data"]
    baseline_monthly_income = {
        item["month"]: item["amount"] for item in baseline_rent_income["monthly_income"]
    }

    create_user_and_login(f"inactive_stats_{unique_suffix}", "tenant", api_request, status="inactive")

    contract_context = create_active_contract(
        unique_suffix,
        api_request,
        auth_headers,
        landlord_token,
        tenant_token,
    )

    extra_house_id = create_house(
        unique_suffix,
        api_request,
        auth_headers,
        landlord_token,
        title_prefix="Statistics Extra House",
    )
    publish_house(api_request, auth_headers, landlord_token, extra_house_id)

    bill = api_request(
        "POST",
        "/api/v1/bills",
        step_name="create statistics bill",
        expected_status=201,
        headers=auth_headers(landlord_token),
        json={
            "contract_id": contract_context["contract_id"],
            "bill_type": "rent",
            "amount": 2600,
            "due_date": (date.today() + timedelta(days=7)).isoformat(),
            "remark": "statistics rent bill",
        },
    )["data"]

    api_request(
        "POST",
        "/api/v1/payments",
        step_name="create statistics payment",
        expected_status=201,
        headers=auth_headers(tenant_token),
        json={
            "bill_id": bill["id"],
            "amount": 2600,
            "payment_method": "mock",
            "remark": "statistics payment",
        },
    )

    api_request(
        "POST",
        "/api/v1/repairs",
        step_name="create statistics repair",
        expected_status=201,
        headers=auth_headers(tenant_token),
        json={
            "contract_id": contract_context["contract_id"],
            "description": "statistics repair item",
        },
    )

    api_request(
        "POST",
        "/api/v1/complaints",
        step_name="create statistics complaint",
        expected_status=201,
        headers=auth_headers(tenant_token),
        json={
            "contract_id": contract_context["contract_id"],
            "description": "statistics complaint item",
        },
    )

    house_stats = api_request(
        "GET",
        "/api/v1/statistics/house-utilization",
        step_name="statistics house utilization",
        expected_status=200,
        headers=auth_headers(admin_token),
    )["data"]
    assert house_stats["total_houses"] == baseline_house_stats["total_houses"] + 2
    assert house_stats["occupied_houses"] == baseline_house_stats["occupied_houses"] + 1
    expected_utilization_rate = house_stats["occupied_houses"] / house_stats["total_houses"]
    assert abs(house_stats["utilization_rate"] - expected_utilization_rate) < 1e-9

    rent_income = api_request(
        "GET",
        "/api/v1/statistics/rent-income",
        step_name="statistics rent income",
        expected_status=200,
        headers=auth_headers(admin_token),
    )["data"]
    assert rent_income["total_income"] == baseline_rent_income["total_income"] + 2600.0
    current_month = datetime.now().strftime("%Y-%m")
    rent_income_map = {item["month"]: item["amount"] for item in rent_income["monthly_income"]}
    assert len(current_month) == 7
    assert rent_income_map[current_month] == baseline_monthly_income.get(current_month, 0.0) + 2600.0

    active_users = api_request(
        "GET",
        "/api/v1/statistics/active-users",
        step_name="statistics active users",
        expected_status=200,
        headers=auth_headers(admin_token),
    )["data"]
    assert active_users["active_user_count"] == baseline_active_users["active_user_count"]

    complaint_repair = api_request(
        "GET",
        "/api/v1/statistics/complaint-repair-count",
        step_name="statistics complaint repair count",
        expected_status=200,
        headers=auth_headers(admin_token),
    )["data"]
    assert complaint_repair["repair_count"] == baseline_complaint_repair["repair_count"] + 1
    assert complaint_repair["complaint_count"] == baseline_complaint_repair["complaint_count"] + 1
