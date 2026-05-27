from __future__ import annotations

from io import BytesIO


def _upload_file(http, base_url: str, path: str, *, token: str, field_name: str = "file") -> dict[str, object]:
    # requests will set multipart content-type automatically; override the session default header.
    headers = {"Authorization": f"Bearer {token}"}
    files = {field_name: ("avatar.png", BytesIO(b"fakepngdata"), "image/png")}
    response = http.post(f"{base_url}{path}", headers=headers, files=files, timeout=20)
    assert response.status_code in {200, 201}, response.text
    payload = response.json()
    assert payload["code"] == 0, payload
    return payload["data"]


def test_user_avatar_upload_and_get_current(
    unique_suffix: str,
    api_request,
    auth_headers,
    http,
    base_url,
) -> None:
    username = f"avatar_{unique_suffix}"
    password = "Password123!"

    api_request(
        "POST",
        "/api/v1/users",
        step_name="register user",
        expected_status=201,
        json={"username": username, "password": password, "role": "tenant"},
    )
    login = api_request(
        "POST",
        "/api/v1/auth/login",
        step_name="login user",
        expected_status=200,
        json={"username": username, "password": password},
    )
    token = login["data"]["token"]

    uploaded = _upload_file(http, base_url, "/api/v1/users/me/avatar/upload", token=token)
    assert uploaded["url"].startswith("/uploads/avatars/"), uploaded
    assert uploaded["is_current"] is True

    current = api_request(
        "GET",
        "/api/v1/users/me/avatar",
        step_name="get current avatar",
        expected_status=200,
        headers=auth_headers(token),
    )["data"]
    assert current is not None
    assert current["id"] == uploaded["id"]


def test_user_avatar_list(
    unique_suffix: str,
    api_request,
    auth_headers,
    http,
    base_url,
) -> None:
    username = f"avatar_list_{unique_suffix}"
    password = "Password123!"

    api_request(
        "POST",
        "/api/v1/users",
        step_name="register user",
        expected_status=201,
        json={"username": username, "password": password, "role": "tenant"},
    )
    token = api_request(
        "POST",
        "/api/v1/auth/login",
        step_name="login user",
        expected_status=200,
        json={"username": username, "password": password},
    )["data"]["token"]

    _upload_file(http, base_url, "/api/v1/users/me/avatar/upload", token=token)

    listed = api_request(
        "GET",
        "/api/v1/users/me/avatars",
        step_name="list avatars",
        expected_status=200,
        headers=auth_headers(token),
        params={"page": 1, "page_size": 10},
    )["data"]
    assert listed["total"] >= 1
    assert len(listed["list"]) >= 1
