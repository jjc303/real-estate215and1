from __future__ import annotations

from io import BytesIO


def _upload_house_image(http, base_url: str, house_id: int, *, token: str) -> dict[str, object]:
    response = http.post(
        f"{base_url}/api/v1/houses/{house_id}/images/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("house.png", BytesIO(b"fakepngdata"), "image/png")},
        timeout=20,
    )
    assert response.status_code in {200, 201}, response.text
    payload = response.json()
    assert payload["code"] == 0, payload
    return payload["data"]


def _upload_avatar(http, base_url: str, *, token: str) -> dict[str, object]:
    response = http.post(
        f"{base_url}/api/v1/users/me/avatar/upload",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("avatar.png", BytesIO(b"fakepngdata"), "image/png")},
        timeout=20,
    )
    assert response.status_code in {200, 201}, response.text
    payload = response.json()
    assert payload["code"] == 0, payload
    return payload["data"]


def test_upload_and_static_url_access_end_to_end(
    unique_suffix: str,
    api_request,
    auth_headers,
    http,
    base_url,
) -> None:
    landlord_username = f"upload_static_landlord_{unique_suffix}"
    password = "Password123!"

    api_request(
        "POST",
        "/api/v1/users",
        step_name="register landlord",
        expected_status=201,
        json={"username": landlord_username, "password": password, "role": "landlord"},
    )
    login_payload = api_request(
        "POST",
        "/api/v1/auth/login",
        step_name="landlord login",
        expected_status=200,
        json={"username": landlord_username, "password": password},
    )
    token = login_payload["data"]["token"]

    house = api_request(
        "POST",
        "/api/v1/houses",
        step_name="create house",
        expected_status=201,
        headers=auth_headers(token),
        json={
            "title": "Static access house",
            "address": "Static Road 1",
            "region": "TestRegion",
            "community": None,
            "house_type": "1B1B",
            "area": 55,
            "rent": 3200,
            "deposit": 3200,
            "decoration": None,
            "floor": None,
            "orientation": None,
            "description": "for upload static access smoke test",
        },
    )["data"]
    house_id = house["id"]

    house_image = _upload_house_image(http, base_url, house_id, token=token)
    assert house_image["url"].startswith("/uploads/"), house_image

    house_image_response = http.get(f"{base_url}{house_image['url']}", timeout=20)
    assert house_image_response.status_code == 200, house_image_response.text
    assert house_image_response.content, "house image content is empty"

    avatar = _upload_avatar(http, base_url, token=token)
    assert avatar["url"].startswith("/uploads/"), avatar

    avatar_response = http.get(f"{base_url}{avatar['url']}", timeout=20)
    assert avatar_response.status_code == 200, avatar_response.text
    assert avatar_response.content, "avatar content is empty"
