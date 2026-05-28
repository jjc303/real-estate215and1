from __future__ import annotations

from io import BytesIO


def _upload_house_image(http, base_url: str, house_id: int, *, token: str, is_cover: bool | None = None) -> dict[str, object]:
    headers = {"Authorization": f"Bearer {token}"}
    files = {"file": ("house.png", BytesIO(b"fakepngdata"), "image/png")}
    data = {}
    if is_cover is not None:
        data["is_cover"] = "true" if is_cover else "false"
    response = http.post(
        f"{base_url}/api/v1/houses/{house_id}/images/upload",
        headers=headers,
        files=files,
        data=data,
        timeout=20,
    )
    assert response.status_code in {200, 201}, response.text
    payload = response.json()
    assert payload["code"] == 0, payload
    return payload["data"]


def test_house_image_upload_list_patch_delete(
    unique_suffix: str,
    api_request,
    auth_headers,
    http,
    base_url,
) -> None:
    landlord_username = f"img_landlord_{unique_suffix}"
    tenant_username = f"img_tenant_{unique_suffix}"
    password = "Password123!"

    api_request(
        "POST",
        "/api/v1/users",
        step_name="register landlord",
        expected_status=201,
        json={"username": landlord_username, "password": password, "role": "landlord"},
    )
    api_request(
        "POST",
        "/api/v1/users",
        step_name="register tenant",
        expected_status=201,
        json={"username": tenant_username, "password": password, "role": "tenant"},
    )
    landlord_token = api_request(
        "POST",
        "/api/v1/auth/login",
        step_name="landlord login",
        expected_status=200,
        json={"username": landlord_username, "password": password},
    )["data"]["token"]
    tenant_token = api_request(
        "POST",
        "/api/v1/auth/login",
        step_name="tenant login",
        expected_status=200,
        json={"username": tenant_username, "password": password},
    )["data"]["token"]

    house = api_request(
        "POST",
        "/api/v1/houses",
        step_name="create house",
        expected_status=201,
        headers=auth_headers(landlord_token),
        json={
            "title": "House with images",
            "address": "Somewhere",
            "region": "TestRegion",
            "community": None,
            "house_type": "1B1B",
            "area": 50,
            "rent": 3000,
            "deposit": 3000,
            "decoration": None,
            "floor": None,
            "orientation": None,
            "description": None,
        },
    )["data"]
    house_id = house["id"]

    api_request(
        "PATCH",
        f"/api/v1/houses/{house_id}/publish",
        step_name="publish house",
        expected_status=200,
        headers=auth_headers(landlord_token),
    )

    uploaded = _upload_house_image(http, base_url, house_id, token=landlord_token)
    assert uploaded["house_id"] == house_id
    assert uploaded["url"].startswith("/uploads/houses/"), uploaded

    listed = api_request(
        "GET",
        f"/api/v1/houses/{house_id}/images",
        step_name="list images",
        expected_status=200,
    )["data"]
    assert any(item["id"] == uploaded["id"] for item in listed)

    patched = api_request(
        "PATCH",
        f"/api/v1/houses/{house_id}/images/{uploaded['id']}",
        step_name="patch image",
        expected_status=200,
        headers=auth_headers(landlord_token),
        json={"sort_order": 10, "is_cover": True},
    )["data"]
    assert patched["sort_order"] == 10
    assert patched["is_cover"] is True

    # Tenant should not be able to delete landlord's house images
    response = http.delete(
        f"{base_url}/api/v1/houses/{house_id}/images/{uploaded['id']}",
        headers={"Authorization": f"Bearer {tenant_token}"},
        timeout=20,
    )
    assert response.status_code in {403, 404}

    api_request(
        "DELETE",
        f"/api/v1/houses/{house_id}/images/{uploaded['id']}",
        step_name="delete image",
        expected_status=200,
        headers=auth_headers(landlord_token),
    )
