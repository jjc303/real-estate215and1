"""Test house video upload, list, and delete."""

from __future__ import annotations

import io


def _create_and_publish_house(api_request, auth_headers, token: str) -> dict[str, object]:
    house = api_request(
        "POST",
        "/api/v1/houses",
        step_name="create house",
        expected_status=201,
        headers=auth_headers(token),
        json={
            "title": "Video Test House",
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
            "description": "Test house for video",
        },
    )["data"]
    api_request(
        "PATCH",
        f"/api/v1/houses/{house['id']}/publish",
        step_name="publish house",
        expected_status=200,
        headers=auth_headers(token),
    )
    return house


def _make_mp4_file() -> io.BytesIO:
    """Create a minimal fake mp4 file-like object."""
    data = io.BytesIO(b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42mp41")
    data.name = "test.mp4"
    return data


def test_video_upload_and_list(
    unique_suffix: str,
    api_request,
    auth_headers,
    http,
    base_url,
) -> None:
    username = f"vid_{unique_suffix}"
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

    house = _create_and_publish_house(api_request, auth_headers, token)
    house_id = house["id"]

    # Upload video
    video_file = _make_mp4_file()
    resp = http.post(
        f"{base_url}/api/v1/houses/{house_id}/videos/upload",
        headers=auth_headers(token),
        files={"file": ("test.mp4", video_file, "video/mp4")},
        data={"duration": "120"},
        timeout=20,
    )
    assert resp.status_code == 201, f"upload failed: {resp.text}"
    payload = resp.json()
    assert payload["code"] == 0, f"upload code not 0: {payload}"
    video = payload["data"]
    assert video["house_id"] == house_id
    assert video["mime_type"] == "video/mp4"
    assert video["duration"] == 120
    assert video["status"] == "active"
    assert video["url"].startswith("/uploads/houses")
    video_id = video["id"]

    # List videos
    list_resp = http.get(
        f"{base_url}/api/v1/houses/{house_id}/videos",
        timeout=20,
    )
    assert list_resp.status_code == 200
    list_payload = list_resp.json()
    assert list_payload["code"] == 0
    video_ids = [v["id"] for v in list_payload["data"]]
    assert video_id in video_ids, f"video {video_id} not found in list"

    # Delete video
    del_resp = http.delete(
        f"{base_url}/api/v1/houses/{house_id}/videos/{video_id}",
        headers=auth_headers(token),
        timeout=20,
    )
    assert del_resp.status_code == 200
    del_payload = del_resp.json()
    assert del_payload["code"] == 0

    # Verify deletion (list no longer includes it)
    list_after = http.get(
        f"{base_url}/api/v1/houses/{house_id}/videos",
        timeout=20,
    )
    list_after_ids = [v["id"] for v in list_after.json()["data"]]
    assert video_id not in list_after_ids, "video should have been deleted"


def test_video_upload_without_token_fails(
    unique_suffix: str,
    api_request,
    auth_headers,
    http,
    base_url,
) -> None:
    username = f"vidno_{unique_suffix}"
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

    house = _create_and_publish_house(api_request, auth_headers, token)

    # Upload without token -> 401
    video_file = _make_mp4_file()
    resp = http.post(
        f"{base_url}/api/v1/houses/{house['id']}/videos/upload",
        files={"file": ("test.mp4", video_file, "video/mp4")},
        timeout=20,
    )
    assert resp.status_code == 401, f"expected 401, got {resp.status_code}"


def test_video_upload_non_owner_fails(
    unique_suffix: str,
    api_request,
    auth_headers,
    http,
    base_url,
) -> None:
    owner = f"vidown_{unique_suffix}"
    other = f"vidoth_{unique_suffix}"
    password = "Password123!"

    for user in [owner, other]:
        api_request(
            "POST",
            "/api/v1/users",
            step_name=f"register {user}",
            expected_status=201,
            json={"username": user, "password": password, "role": "landlord"},
        )

    owner_token = api_request(
        "POST", "/api/v1/auth/login", step_name="owner login", expected_status=200,
        json={"username": owner, "password": password},
    )["data"]["token"]

    other_token = api_request(
        "POST", "/api/v1/auth/login", step_name="other login", expected_status=200,
        json={"username": other, "password": password},
    )["data"]["token"]

    house = _create_and_publish_house(api_request, auth_headers, owner_token)

    # Other user uploads -> 404 (house not found for this user)
    video_file = _make_mp4_file()
    resp = http.post(
        f"{base_url}/api/v1/houses/{house['id']}/videos/upload",
        headers=auth_headers(other_token),
        files={"file": ("test.mp4", video_file, "video/mp4")},
        timeout=20,
    )
    assert resp.status_code == 404, f"expected 404, got {resp.status_code}: {resp.text}"
