"""Test house status transitions: DRAFT, LISTED, RENTED, OFFLINE, MAINTENANCE."""

from __future__ import annotations

from datetime import date, datetime, timedelta


def _create_house(api_request, auth_headers, token: str) -> dict[str, object]:
    return api_request(
        "POST",
        "/api/v1/houses",
        step_name="create house",
        expected_status=201,
        headers=auth_headers(token),
        json={
            "title": "Status Test House",
            "address": "Test Address",
            "region": "TestRegion",
            "community": "Test Community",
            "house_type": "1室1厅",
            "area": 55,
            "rent": 2000,
            "deposit": 2000,
            "decoration": "精装修",
            "floor": "6/18",
            "orientation": "南",
            "description": "Test house for status transitions",
        },
    )["data"]


def _publish_house(api_request, auth_headers, token: str, house_id: int) -> dict[str, object]:
    return api_request(
        "PATCH",
        f"/api/v1/houses/{house_id}/publish",
        step_name="publish house",
        expected_status=200,
        headers=auth_headers(token),
    )["data"]


def test_publish_house_draft_to_listed(
    unique_suffix: str,
    api_request,
    auth_headers,
) -> None:
    username = f"pub_{unique_suffix}"
    password = "Password123!"

    api_request(
        "POST",
        "/api/v1/users",
        step_name="register landlord",
        expected_status=201,
        json={"username": username, "password": password, "role": "landlord"},
    )
    token = api_request(
        "POST",
        "/api/v1/auth/login",
        step_name="login",
        expected_status=200,
        json={"username": username, "password": password},
    )["data"]["token"]

    house = _create_house(api_request, auth_headers, token)
    assert house["status"] == "draft", f"expected draft, got {house['status']}"

    published = _publish_house(api_request, auth_headers, token, house["id"])
    assert published["status"] == "listed", f"expected listed, got {published['status']}"


def test_offline_house_listed_to_offline(
    unique_suffix: str,
    api_request,
    auth_headers,
) -> None:
    username = f"off_{unique_suffix}"
    password = "Password123!"

    api_request(
        "POST",
        "/api/v1/users",
        step_name="register landlord",
        expected_status=201,
        json={"username": username, "password": password, "role": "landlord"},
    )
    token = api_request(
        "POST",
        "/api/v1/auth/login",
        step_name="login",
        expected_status=200,
        json={"username": username, "password": password},
    )["data"]["token"]

    house = _create_house(api_request, auth_headers, token)
    _publish_house(api_request, auth_headers, token, house["id"])

    offline = api_request(
        "PATCH",
        f"/api/v1/houses/{house['id']}/offline",
        step_name="offline house",
        expected_status=200,
        headers=auth_headers(token),
    )["data"]
    assert offline["status"] == "offline", f"expected offline, got {offline['status']}"


def test_republish_offline_to_listed(
    unique_suffix: str,
    api_request,
    auth_headers,
) -> None:
    username = f"repub_{unique_suffix}"
    password = "Password123!"

    api_request(
        "POST",
        "/api/v1/users",
        step_name="register landlord",
        expected_status=201,
        json={"username": username, "password": password, "role": "landlord"},
    )
    token = api_request(
        "POST",
        "/api/v1/auth/login",
        step_name="login",
        expected_status=200,
        json={"username": username, "password": password},
    )["data"]["token"]

    house = _create_house(api_request, auth_headers, token)
    _publish_house(api_request, auth_headers, token, house["id"])

    # Offline first
    api_request(
        "PATCH",
        f"/api/v1/houses/{house['id']}/offline",
        step_name="offline house",
        expected_status=200,
        headers=auth_headers(token),
    )

    # Republish from OFFLINE
    republished = _publish_house(api_request, auth_headers, token, house["id"])
    assert republished["status"] == "listed", f"expected listed, got {republished['status']}"


def test_contract_confirm_auto_rented(
    unique_suffix: str,
    api_request,
    auth_headers,
) -> None:
    landlord = f"rent_l_{unique_suffix}"
    tenant = f"rent_t_{unique_suffix}"
    password = "Password123!"

    for user in [landlord, tenant]:
        api_request(
            "POST",
            "/api/v1/users",
            step_name=f"register {user}",
            expected_status=201,
            json={"username": user, "password": password, "role": "landlord" if "l" in user else "tenant"},
        )

    landlord_token = api_request(
        "POST", "/api/v1/auth/login", step_name="landlord login", expected_status=200,
        json={"username": landlord, "password": password},
    )["data"]["token"]

    tenant_token = api_request(
        "POST", "/api/v1/auth/login", step_name="tenant login", expected_status=200,
        json={"username": tenant, "password": password},
    )["data"]["token"]

    # Create and publish house
    house = _create_house(api_request, auth_headers, landlord_token)
    _publish_house(api_request, auth_headers, landlord_token, house["id"])

    # Tenant creates appointment
    appointment_time = (datetime.now() + timedelta(days=1)).isoformat()
    appointment = api_request(
        "POST",
        "/api/v1/appointments",
        step_name="create appointment",
        expected_status=201,
        headers=auth_headers(tenant_token),
        json={"house_id": house["id"], "appointment_time": appointment_time},
    )["data"]

    # Landlord confirms appointment
    api_request(
        "PATCH",
        f"/api/v1/appointments/{appointment['id']}/confirm",
        step_name="confirm appointment",
        expected_status=200,
        headers=auth_headers(landlord_token),
    )

    # Landlord creates contract
    start_date = (date.today() + timedelta(days=7)).isoformat()
    end_date = (date.today() + timedelta(days=372)).isoformat()
    contract = api_request(
        "POST",
        "/api/v1/contracts",
        step_name="create contract",
        expected_status=201,
        headers=auth_headers(landlord_token),
        json={
            "appointment_id": appointment["id"],
            "start_date": start_date,
            "end_date": end_date,
            "monthly_rent": 2000,
            "deposit": 2000,
        },
    )["data"]

    # Tenant confirms contract -> triggers house -> RENTED
    api_request(
        "PATCH",
        f"/api/v1/contracts/{contract['id']}/confirm",
        step_name="confirm contract",
        expected_status=200,
        headers=auth_headers(tenant_token),
    )

    # Verify house status is now RENTED
    house_detail = api_request(
        "GET",
        f"/api/v1/houses/{house['id']}",
        step_name="get house detail as landlord",
        expected_status=200,
        headers=auth_headers(landlord_token),
    )["data"]
    assert house_detail["status"] == "rented", f"expected rented, got {house_detail['status']}"


def test_contract_terminate_auto_listed(
    unique_suffix: str,
    api_request,
    auth_headers,
) -> None:
    landlord = f"term_l_{unique_suffix}"
    tenant = f"term_t_{unique_suffix}"
    password = "Password123!"

    for user in [landlord, tenant]:
        api_request(
            "POST",
            "/api/v1/users",
            step_name=f"register {user}",
            expected_status=201,
            json={"username": user, "password": password, "role": "landlord" if "l" in user else "tenant"},
        )

    landlord_token = api_request(
        "POST", "/api/v1/auth/login", step_name="landlord login", expected_status=200,
        json={"username": landlord, "password": password},
    )["data"]["token"]

    tenant_token = api_request(
        "POST", "/api/v1/auth/login", step_name="tenant login", expected_status=200,
        json={"username": tenant, "password": password},
    )["data"]["token"]

    # Full flow: create house -> publish -> appointment -> contract -> confirm
    house = _create_house(api_request, auth_headers, landlord_token)
    _publish_house(api_request, auth_headers, landlord_token, house["id"])

    appointment_time = (datetime.now() + timedelta(days=1)).isoformat()
    appointment = api_request(
        "POST", "/api/v1/appointments", step_name="create appointment", expected_status=201,
        headers=auth_headers(tenant_token),
        json={"house_id": house["id"], "appointment_time": appointment_time},
    )["data"]

    api_request(
        "PATCH", f"/api/v1/appointments/{appointment['id']}/confirm",
        step_name="confirm appointment", expected_status=200,
        headers=auth_headers(landlord_token),
    )

    start_date = (date.today() + timedelta(days=7)).isoformat()
    end_date = (date.today() + timedelta(days=372)).isoformat()
    contract = api_request(
        "POST", "/api/v1/contracts", step_name="create contract", expected_status=201,
        headers=auth_headers(landlord_token),
        json={
            "appointment_id": appointment["id"],
            "start_date": start_date, "end_date": end_date,
            "monthly_rent": 2000, "deposit": 2000,
        },
    )["data"]

    api_request(
        "PATCH", f"/api/v1/contracts/{contract['id']}/confirm",
        step_name="confirm contract", expected_status=200,
        headers=auth_headers(tenant_token),
    )

    # Landlord terminates contract -> triggers house -> LISTED
    api_request(
        "PATCH",
        f"/api/v1/contracts/{contract['id']}/terminate",
        step_name="terminate contract",
        expected_status=200,
        headers=auth_headers(landlord_token),
    )

    house_detail = api_request(
        "GET",
        f"/api/v1/houses/{house['id']}",
        step_name="get house detail as landlord",
        expected_status=200,
        headers=auth_headers(landlord_token),
    )["data"]
    assert house_detail["status"] == "listed", f"expected listed, got {house_detail['status']}"


def test_set_and_restore_maintenance(
    unique_suffix: str,
    api_request,
    auth_headers,
) -> None:
    username = f"maint_{unique_suffix}"
    password = "Password123!"

    api_request(
        "POST",
        "/api/v1/users",
        step_name="register landlord",
        expected_status=201,
        json={"username": username, "password": password, "role": "landlord"},
    )
    token = api_request(
        "POST",
        "/api/v1/auth/login",
        step_name="login",
        expected_status=200,
        json={"username": username, "password": password},
    )["data"]["token"]

    house = _create_house(api_request, auth_headers, token)
    _publish_house(api_request, auth_headers, token, house["id"])

    # Set to MAINTENANCE
    maintenance = api_request(
        "PATCH",
        f"/api/v1/houses/{house['id']}/maintenance",
        step_name="set maintenance",
        expected_status=200,
        headers=auth_headers(token),
    )["data"]
    assert maintenance["status"] == "maintenance", f"expected maintenance, got {maintenance['status']}"

    # Restore from MAINTENANCE
    restored = api_request(
        "PATCH",
        f"/api/v1/houses/{house['id']}/restore",
        step_name="restore from maintenance",
        expected_status=200,
        headers=auth_headers(token),
    )["data"]
    assert restored["status"] == "listed", f"expected listed, got {restored['status']}"


def test_invalid_transitions_return_400(
    unique_suffix: str,
    api_request,
    auth_headers,
    http,
    base_url,
) -> None:
    username = f"inv_{unique_suffix}"
    password = "Password123!"

    api_request(
        "POST",
        "/api/v1/users",
        step_name="register landlord",
        expected_status=201,
        json={"username": username, "password": password, "role": "landlord"},
    )
    token = api_request(
        "POST",
        "/api/v1/auth/login",
        step_name="login",
        expected_status=200,
        json={"username": username, "password": password},
    )["data"]["token"]

    house = _create_house(api_request, auth_headers, token)
    house_id = house["id"]

    # DRAFT -> OFFLINE (invalid)
    resp = http.patch(
        f"{base_url}/api/v1/houses/{house_id}/offline",
        headers=auth_headers(token),
        timeout=20,
    )
    assert resp.status_code == 400, f"expected 400, got {resp.status_code}: {resp.text}"

    # DRAFT -> MAINTENANCE (invalid)
    resp = http.patch(
        f"{base_url}/api/v1/houses/{house_id}/maintenance",
        headers=auth_headers(token),
        timeout=20,
    )
    assert resp.status_code == 400, f"expected 400, got {resp.status_code}: {resp.text}"

    # DRAFT -> RENTED cannot be tested directly (only via contract flow)

    # Publish it
    _publish_house(api_request, auth_headers, token, house_id)

    # LISTED -> LISTED (publish again should fail)
    resp = http.patch(
        f"{base_url}/api/v1/houses/{house_id}/publish",
        headers=auth_headers(token),
        timeout=20,
    )
    assert resp.status_code == 400, f"expected 400, got {resp.status_code}: {resp.text}"

    # Set to MAINTENANCE
    api_request(
        "PATCH",
        f"/api/v1/houses/{house_id}/maintenance",
        step_name="set maintenance from listed",
        expected_status=200,
        headers=auth_headers(token),
    )

    # MAINTENANCE -> OFFLINE should work
    api_request(
        "PATCH",
        f"/api/v1/houses/{house_id}/offline",
        step_name="offline from maintenance",
        expected_status=200,
        headers=auth_headers(token),
    )

    # OFFLINE -> MAINTENANCE (invalid)
    resp = http.patch(
        f"{base_url}/api/v1/houses/{house_id}/maintenance",
        headers=auth_headers(token),
        timeout=20,
    )
    assert resp.status_code == 400, f"expected 400, got {resp.status_code}: {resp.text}"


def test_rented_house_hidden_from_public_list(
    unique_suffix: str,
    api_request,
    auth_headers,
) -> None:
    landlord = f"hid_l_{unique_suffix}"
    tenant = f"hid_t_{unique_suffix}"
    password = "Password123!"

    for user in [landlord, tenant]:
        api_request(
            "POST",
            "/api/v1/users",
            step_name=f"register {user}",
            expected_status=201,
            json={"username": user, "password": password, "role": "landlord" if "l" in user else "tenant"},
        )

    landlord_token = api_request(
        "POST", "/api/v1/auth/login", step_name="landlord login", expected_status=200,
        json={"username": landlord, "password": password},
    )["data"]["token"]

    tenant_token = api_request(
        "POST", "/api/v1/auth/login", step_name="tenant login", expected_status=200,
        json={"username": tenant, "password": password},
    )["data"]["token"]

    # Create and publish house
    house = _create_house(api_request, auth_headers, landlord_token)
    _publish_house(api_request, auth_headers, landlord_token, house["id"])

    # Confirm it appears in public list
    public_list = api_request(
        "GET", "/api/v1/houses", step_name="list public houses", expected_status=200,
        params={"page": 1, "page_size": 100},
    )["data"]["list"]
    public_ids = {item["id"] for item in public_list}
    assert house["id"] in public_ids, "house should be visible before renting"

    # Full contract flow to get house to RENTED
    appointment_time = (datetime.now() + timedelta(days=1)).isoformat()
    appointment = api_request(
        "POST", "/api/v1/appointments", step_name="create appointment", expected_status=201,
        headers=auth_headers(tenant_token),
        json={"house_id": house["id"], "appointment_time": appointment_time},
    )["data"]

    api_request(
        "PATCH", f"/api/v1/appointments/{appointment['id']}/confirm",
        step_name="confirm appointment", expected_status=200,
        headers=auth_headers(landlord_token),
    )

    start_date = (date.today() + timedelta(days=7)).isoformat()
    end_date = (date.today() + timedelta(days=372)).isoformat()
    contract = api_request(
        "POST", "/api/v1/contracts", step_name="create contract", expected_status=201,
        headers=auth_headers(landlord_token),
        json={
            "appointment_id": appointment["id"],
            "start_date": start_date, "end_date": end_date,
            "monthly_rent": 2000, "deposit": 2000,
        },
    )["data"]

    api_request(
        "PATCH", f"/api/v1/contracts/{contract['id']}/confirm",
        step_name="confirm contract", expected_status=200,
        headers=auth_headers(tenant_token),
    )

    # Verify house is RENTED
    house_detail = api_request(
        "GET",
        f"/api/v1/houses/{house['id']}",
        step_name="get house detail as landlord",
        expected_status=200,
        headers=auth_headers(landlord_token),
    )["data"]
    assert house_detail["status"] == "rented"

    # Verify it no longer appears in public list
    public_list_after = api_request(
        "GET", "/api/v1/houses", step_name="list public houses after rented", expected_status=200,
        params={"page": 1, "page_size": 100},
    )["data"]["list"]
    public_ids_after = {item["id"] for item in public_list_after}
    assert house["id"] not in public_ids_after, "rented house should not be in public list"


def test_maintenance_house_hidden_from_public_list(
    unique_suffix: str,
    api_request,
    auth_headers,
) -> None:
    username = f"mh_{unique_suffix}"
    password = "Password123!"

    api_request(
        "POST",
        "/api/v1/users",
        step_name="register landlord",
        expected_status=201,
        json={"username": username, "password": password, "role": "landlord"},
    )
    token = api_request(
        "POST",
        "/api/v1/auth/login",
        step_name="login",
        expected_status=200,
        json={"username": username, "password": password},
    )["data"]["token"]

    house = _create_house(api_request, auth_headers, token)
    _publish_house(api_request, auth_headers, token, house["id"])

    # Confirm it appears in public list
    public_list = api_request(
        "GET", "/api/v1/houses", step_name="list public houses", expected_status=200,
        params={"page": 1, "page_size": 100},
    )["data"]["list"]
    public_ids = {item["id"] for item in public_list}
    assert house["id"] in public_ids, "house should be visible before maintenance"

    # Set to MAINTENANCE
    api_request(
        "PATCH",
        f"/api/v1/houses/{house['id']}/maintenance",
        step_name="set maintenance",
        expected_status=200,
        headers=auth_headers(token),
    )

    # Verify it no longer appears in public list
    public_list_after = api_request(
        "GET", "/api/v1/houses", step_name="list public houses after maintenance", expected_status=200,
        params={"page": 1, "page_size": 100},
    )["data"]["list"]
    public_ids_after = {item["id"] for item in public_list_after}
    assert house["id"] not in public_ids_after, "maintenance house should not be in public list"
