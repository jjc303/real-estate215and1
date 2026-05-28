from __future__ import annotations


def _create_and_publish_house(api_request, auth_headers, token: str, *, title: str, house_type: str, orientation: str, rent: int, area: int) -> dict[str, object]:
    house = api_request(
        "POST",
        "/api/v1/houses",
        step_name=f"create {title}",
        expected_status=201,
        headers=auth_headers(token),
        json={
            "title": title,
            "address": f"{title} Address",
            "region": "TestRegion",
            "community": "TestCommunity",
            "house_type": house_type,
            "area": area,
            "rent": rent,
            "deposit": rent,
            "decoration": "simple",
            "floor": "6/18",
            "orientation": orientation,
            "description": f"{title} description",
        },
    )["data"]
    house_id = house["id"]
    api_request(
        "PATCH",
        f"/api/v1/houses/{house_id}/publish",
        step_name=f"publish {title}",
        expected_status=200,
        headers=auth_headers(token),
    )
    return house


def test_house_list_filters_house_type_orientation_and_ranges(
    unique_suffix: str,
    api_request,
    auth_headers,
    http,
    base_url,
) -> None:
    landlord_username = f"house_filter_{unique_suffix}"
    password = "Password123!"
    api_request(
        "POST",
        "/api/v1/users",
        step_name="register landlord",
        expected_status=201,
        json={"username": landlord_username, "password": password, "role": "landlord"},
    )
    token = api_request(
        "POST",
        "/api/v1/auth/login",
        step_name="landlord login",
        expected_status=200,
        json={"username": landlord_username, "password": password},
    )["data"]["token"]

    h1 = _create_and_publish_house(
        api_request,
        auth_headers,
        token,
        title="h1",
        house_type="1室1厅1卫",
        orientation="南",
        rent=3000,
        area=45,
    )
    h2 = _create_and_publish_house(
        api_request,
        auth_headers,
        token,
        title="h2",
        house_type="2室1厅1卫",
        orientation="东南",
        rent=4200,
        area=72,
    )
    h3 = _create_and_publish_house(
        api_request,
        auth_headers,
        token,
        title="h3",
        house_type="3室2厅2卫",
        orientation="北",
        rent=5600,
        area=105,
    )

    # house_type supports csv and fuzzy contains matching.
    by_house_type = api_request(
        "GET",
        "/api/v1/houses",
        step_name="filter by house_type csv",
        expected_status=200,
        params={"house_type": "1室,2室", "page": 1, "page_size": 20},
    )["data"]["list"]
    by_house_type_ids = {item["id"] for item in by_house_type}
    assert h1["id"] in by_house_type_ids
    assert h2["id"] in by_house_type_ids
    assert h3["id"] not in by_house_type_ids

    # orientation supports csv and fuzzy contains matching.
    by_orientation = api_request(
        "GET",
        "/api/v1/houses",
        step_name="filter by orientation csv",
        expected_status=200,
        params={"orientation": "南,东南", "page": 1, "page_size": 20},
    )["data"]["list"]
    by_orientation_ids = {item["id"] for item in by_orientation}
    assert h1["id"] in by_orientation_ids
    assert h2["id"] in by_orientation_ids
    assert h3["id"] not in by_orientation_ids

    # Combined filters should narrow the result.
    combined = api_request(
        "GET",
        "/api/v1/houses",
        step_name="combined filters",
        expected_status=200,
        params={
            "house_type": "2室",
            "orientation": "东南",
            "min_rent": 4000,
            "max_rent": 5000,
            "min_area": 60,
            "max_area": 90,
            "page": 1,
            "page_size": 20,
        },
    )["data"]["list"]
    combined_ids = {item["id"] for item in combined}
    assert h2["id"] in combined_ids
    assert h1["id"] not in combined_ids
    assert h3["id"] not in combined_ids

    # Range validation still works.
    invalid_resp = http.get(
        f"{base_url}/api/v1/houses",
        params={"min_rent": 5000, "max_rent": 4000},
        timeout=20,
    )
    assert invalid_resp.status_code == 400, invalid_resp.text
    invalid_payload = invalid_resp.json()
    assert invalid_payload["code"] == 3001, invalid_payload
