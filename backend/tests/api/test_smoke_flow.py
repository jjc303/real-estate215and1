from __future__ import annotations

# Run:
#   cd backend
#   pytest tests/api/test_smoke_flow.py -q
#
# Or override base URL:
#   set API_BASE_URL=http://127.0.0.1:8000
#   pytest tests/api/test_smoke_flow.py -q

from datetime import date, datetime, timedelta

def test_full_rental_flow(
    unique_suffix: str,
    api_request,
    auth_headers,
) -> None:
    landlord_username = f"landlord_{unique_suffix}"
    tenant_username = f"tenant_{unique_suffix}"
    password = "Password123!"

    register_landlord = api_request(
        "POST",
        "/api/v1/users",
        step_name="register landlord",
        expected_status=201,
        json={
            "username": landlord_username,
            "password": password,
            "role": "landlord",
            "email": f"{landlord_username}@example.com",
        },
    )
    assert register_landlord["data"]["username"] == landlord_username

    register_tenant = api_request(
        "POST",
        "/api/v1/users",
        step_name="register tenant",
        expected_status=201,
        json={
            "username": tenant_username,
            "password": password,
            "role": "tenant",
            "email": f"{tenant_username}@example.com",
        },
    )
    assert register_tenant["data"]["username"] == tenant_username

    landlord_login = api_request(
        "POST",
        "/api/v1/auth/login",
        step_name="landlord login",
        expected_status=200,
        json={"username": landlord_username, "password": password},
    )
    landlord_token = landlord_login["data"]["token"]

    tenant_login = api_request(
        "POST",
        "/api/v1/auth/login",
        step_name="tenant login",
        expected_status=200,
        json={"username": tenant_username, "password": password},
    )
    tenant_token = tenant_login["data"]["token"]

    create_house = api_request(
        "POST",
        "/api/v1/houses",
        step_name="create house",
        expected_status=201,
        headers=auth_headers(landlord_token),
        json={
            "title": f"Smoke House {unique_suffix}",
            "address": f"Smoke Address {unique_suffix}",
            "region": "Smoke Region",
            "community": "Smoke Community",
            "house_type": "1室1厅",
            "area": 55,
            "rent": 2000,
            "deposit": 2000,
            "decoration": "精装修",
            "floor": "6/18",
            "orientation": "南",
            "description": "Smoke flow house",
        },
    )
    house_id = create_house["data"]["id"]

    publish_house = api_request(
        "PATCH",
        f"/api/v1/houses/{house_id}/publish",
        step_name="publish house",
        expected_status=200,
        headers=auth_headers(landlord_token),
    )
    assert publish_house["data"]["status"] == "listed"

    add_favorite = api_request(
        "POST",
        "/api/v1/favorites",
        step_name="tenant add favorite",
        expected_status=201,
        headers=auth_headers(tenant_token),
        json={"house_id": house_id},
    )
    assert add_favorite["data"]["house_id"] == house_id

    appointment_time = (datetime.now() + timedelta(days=1)).isoformat()
    create_appointment = api_request(
        "POST",
        "/api/v1/appointments",
        step_name="tenant create appointment",
        expected_status=201,
        headers=auth_headers(tenant_token),
        json={
            "house_id": house_id,
            "appointment_time": appointment_time,
            "remark": "Smoke appointment",
        },
    )
    appointment_id = create_appointment["data"]["id"]

    confirm_appointment = api_request(
        "PATCH",
        f"/api/v1/appointments/{appointment_id}/confirm",
        step_name="landlord confirm appointment",
        expected_status=200,
        headers=auth_headers(landlord_token),
    )
    assert confirm_appointment["data"]["status"] == "confirmed"

    create_conversation = api_request(
        "POST",
        "/api/v1/conversations",
        step_name="tenant create conversation",
        expected_status=201,
        headers=auth_headers(tenant_token),
        json={"house_id": house_id},
    )
    conversation_id = create_conversation["data"]["id"]

    send_message = api_request(
        "POST",
        f"/api/v1/conversations/{conversation_id}/messages",
        step_name="tenant send message",
        expected_status=201,
        headers=auth_headers(tenant_token),
        json={"content": "  你好，这个房子还在吗？  "},
    )
    assert send_message["data"]["content"] == "你好，这个房子还在吗？"

    landlord_conversations = api_request(
        "GET",
        "/api/v1/conversations",
        step_name="landlord list conversations",
        expected_status=200,
        headers=auth_headers(landlord_token),
        params={"page": 1, "page_size": 100},
    )
    conversation_items = landlord_conversations["data"]["list"]
    target_conversation = next(
        (
            item
            for item in conversation_items
            if item["id"] == conversation_id
        ),
        None,
    )
    assert target_conversation is not None, (
        f"landlord list conversations failed: conversation {conversation_id} not found; "
        f"list={conversation_items!r}"
    )
    assert target_conversation["unread_count"] >= 1

    mark_read = api_request(
        "PATCH",
        f"/api/v1/conversations/{conversation_id}/read",
        step_name="landlord mark conversation read",
        expected_status=200,
        headers=auth_headers(landlord_token),
    )
    assert mark_read["data"]["updated"] >= 1

    start_date = (date.today() + timedelta(days=7)).isoformat()
    end_date = (date.today() + timedelta(days=372)).isoformat()
    create_contract = api_request(
        "POST",
        "/api/v1/contracts",
        step_name="landlord create contract",
        expected_status=201,
        headers=auth_headers(landlord_token),
        json={
            "appointment_id": appointment_id,
            "start_date": start_date,
            "end_date": end_date,
            "monthly_rent": 2000,
            "deposit": 2000,
            "remark": "Smoke contract",
        },
    )
    contract_id = create_contract["data"]["id"]
    assert create_contract["data"]["status"] == "pending"

    confirm_contract = api_request(
        "PATCH",
        f"/api/v1/contracts/{contract_id}/confirm",
        step_name="tenant confirm contract",
        expected_status=200,
        headers=auth_headers(tenant_token),
    )
    assert confirm_contract["data"]["status"] == "active"

    contract_detail = api_request(
        "GET",
        f"/api/v1/contracts/{contract_id}",
        step_name="get contract detail",
        expected_status=200,
        headers=auth_headers(tenant_token),
    )
    assert contract_detail["data"]["status"] == "active"
