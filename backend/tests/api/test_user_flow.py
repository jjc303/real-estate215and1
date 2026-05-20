from __future__ import annotations

# Run:
#   cd backend
#   pytest tests/api/test_user_flow.py -q


def test_user_update_me_success(
    unique_suffix: str,
    api_request,
    auth_headers,
) -> None:
    username = f"update_me_{unique_suffix}"
    password = "Password123!"

    register = api_request(
        "POST",
        "/api/v1/users",
        step_name="register user",
        expected_status=201,
        json={
            "username": username,
            "password": password,
            "role": "tenant",
            "real_name": "Original Name",
            "phone": "13800000000",
            "email": f"{username}@example.com",
        },
    )
    assert register["data"]["username"] == username
    assert register["data"]["real_name"] == "Original Name"

    login = api_request(
        "POST",
        "/api/v1/auth/login",
        step_name="user login",
        expected_status=200,
        json={"username": username, "password": password},
    )
    token = login["data"]["token"]

    updated = api_request(
        "PUT",
        "/api/v1/users/me",
        step_name="update own profile",
        expected_status=200,
        headers=auth_headers(token),
        json={
            "real_name": "Updated Name",
            "phone": "13900000001",
            "avatar": "https://example.com/new_avatar.png",
        },
    )
    assert updated["data"]["real_name"] == "Updated Name"
    assert updated["data"]["phone"] == "13900000001"
    assert updated["data"]["avatar"] == "https://example.com/new_avatar.png"
    assert updated["data"]["username"] == username


def test_user_update_me_unauthorized(
    unique_suffix: str,
    http,
    base_url,
) -> None:
    response = http.put(
        f"{base_url}/api/v1/users/me",
        json={"real_name": "Hacker"},
        timeout=20,
    )
    assert response.status_code == 401
    payload = response.json()
    assert payload["code"] == 1003


def test_user_update_me_email_conflict(
    unique_suffix: str,
    api_request,
    auth_headers,
    http,
    base_url,
) -> None:
    password = "Password123!"
    user_a = f"email_conflict_a_{unique_suffix}"
    user_b = f"email_conflict_b_{unique_suffix}"

    api_request(
        "POST",
        "/api/v1/users",
        step_name="register user A",
        expected_status=201,
        json={
            "username": user_a,
            "password": password,
            "role": "tenant",
            "email": f"{user_a}@example.com",
        },
    )
    api_request(
        "POST",
        "/api/v1/users",
        step_name="register user B",
        expected_status=201,
        json={
            "username": user_b,
            "password": password,
            "role": "tenant",
            "email": f"{user_b}@example.com",
        },
    )

    login_b = api_request(
        "POST",
        "/api/v1/auth/login",
        step_name="user B login",
        expected_status=200,
        json={"username": user_b, "password": password},
    )
    token_b = login_b["data"]["token"]

    response = http.put(
        f"{base_url}/api/v1/users/me",
        headers=auth_headers(token_b),
        json={"email": f"{user_a}@example.com"},
        timeout=20,
    )
    assert response.status_code == 409
    payload = response.json()
    assert payload["code"] == 2002


def test_user_update_me_password(
    unique_suffix: str,
    api_request,
    auth_headers,
) -> None:
    username = f"update_pwd_{unique_suffix}"
    password = "OldPass123!"

    api_request(
        "POST",
        "/api/v1/users",
        step_name="register user",
        expected_status=201,
        json={
            "username": username,
            "password": password,
            "role": "landlord",
        },
    )

    login = api_request(
        "POST",
        "/api/v1/auth/login",
        step_name="login with old password",
        expected_status=200,
        json={"username": username, "password": password},
    )
    token = login["data"]["token"]

    api_request(
        "PUT",
        "/api/v1/users/me",
        step_name="update password",
        expected_status=200,
        headers=auth_headers(token),
        json={"password": "NewPass456!"},
    )

    login_with_new = api_request(
        "POST",
        "/api/v1/auth/login",
        step_name="login with new password",
        expected_status=200,
        json={"username": username, "password": "NewPass456!"},
    )
    assert login_with_new["data"]["token"] is not None