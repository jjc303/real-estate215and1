from __future__ import annotations

from typing import Any

import requests

FORBIDDEN_CODE = 1004
NEWS_NOT_FOUND_CODE = 3002


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
            f"expected HTTP {expected_status}, got HTTP {response.status_code}; body={response.text!r}"
        ) from exc

    if response.status_code != expected_status:
        raise AssertionError(
            f"{step_name} failed: {method} {base_url}{path} expected HTTP {expected_status}, "
            f"got HTTP {response.status_code}; response={payload!r}"
        )
    return payload


def create_user_and_login(unique_suffix: str, role: str, api_request) -> tuple[int, str]:
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


def list_notifications(api_request, auth_headers, token: str) -> list[dict[str, Any]]:
    response = api_request(
        "GET",
        "/api/v1/notifications",
        step_name="list notifications",
        expected_status=200,
        headers=auth_headers(token),
        params={"page": 1, "page_size": 100},
    )
    return response["data"]["list"]


def find_news_item(items: list[dict[str, Any]], news_id: int) -> dict[str, Any] | None:
    return next((item for item in items if item["id"] == news_id), None)


def test_news_admin_flow_and_notification_retention(
    unique_suffix: str,
    api_request,
    auth_headers,
    http: requests.Session,
    base_url: str,
) -> None:
    _, tenant_token = create_user_and_login(f"tenant_{unique_suffix}", "tenant", api_request)
    _, landlord_token = create_user_and_login(f"landlord_{unique_suffix}", "landlord", api_request)
    _, admin_token = create_user_and_login(f"admin_{unique_suffix}", "admin", api_request)

    initial_news_list = api_request(
        "GET",
        "/api/v1/news",
        step_name="tenant list initial news",
        expected_status=200,
        headers=auth_headers(tenant_token),
        params={"page": 1, "page_size": 10},
    )["data"]
    initial_total = initial_news_list["total"]

    draft_news = api_request(
        "POST",
        "/api/v1/news",
        step_name="admin create draft news",
        expected_status=201,
        headers=auth_headers(admin_token),
        json={
            "title": f"Draft news {unique_suffix}",
            "content": "Draft only content",
            "status": "draft",
        },
    )["data"]
    assert draft_news["status"] == "draft"

    published_news = api_request(
        "POST",
        "/api/v1/news",
        step_name="admin create published news",
        expected_status=201,
        headers=auth_headers(admin_token),
        json={
            "title": f"Published news {unique_suffix}",
            "content": "Published content",
            "status": "published",
        },
    )["data"]
    assert published_news["status"] == "published"

    admin_news_list = api_request(
        "GET",
        "/api/v1/news",
        step_name="admin list all news",
        expected_status=200,
        headers=auth_headers(admin_token),
        params={"page": 1, "page_size": 10},
    )["data"]
    assert {item["id"] for item in admin_news_list["list"]} >= {draft_news["id"], published_news["id"]}

    admin_draft_only = api_request(
        "GET",
        "/api/v1/news",
        step_name="admin list draft news",
        expected_status=200,
        headers=auth_headers(admin_token),
        params={"page": 1, "page_size": 10, "status": "draft"},
    )["data"]
    assert admin_draft_only["total"] >= 1
    assert all(item["status"] == "draft" for item in admin_draft_only["list"])
    assert any(item["id"] == draft_news["id"] for item in admin_draft_only["list"])

    tenant_news_list = api_request(
        "GET",
        "/api/v1/news",
        step_name="tenant list published news",
        expected_status=200,
        headers=auth_headers(tenant_token),
        params={"page": 1, "page_size": 10, "status": "draft"},
    )["data"]
    assert tenant_news_list["total"] >= initial_total + 1
    assert any(item["id"] == published_news["id"] for item in tenant_news_list["list"])
    assert all(item["status"] == "published" for item in tenant_news_list["list"])
    assert all(item["id"] != draft_news["id"] for item in tenant_news_list["list"])

    guest_news_list = api_request(
        "GET",
        "/api/v1/news",
        step_name="guest list published news",
        expected_status=200,
        params={"page": 1, "page_size": 10},
    )["data"]
    assert any(item["id"] == published_news["id"] for item in guest_news_list["list"])
    assert all(item["status"] == "published" for item in guest_news_list["list"])

    published_detail = api_request(
        "GET",
        f"/api/v1/news/{published_news['id']}",
        step_name="tenant get published news detail",
        expected_status=200,
        headers=auth_headers(tenant_token),
    )["data"]
    assert published_detail["id"] == published_news["id"]

    tenant_draft_detail = request_payload(
        http,
        base_url,
        "GET",
        f"/api/v1/news/{draft_news['id']}",
        step_name="tenant get draft news detail forbidden by visibility",
        expected_status=404,
        headers=auth_headers(tenant_token),
    )
    assert tenant_draft_detail["code"] == NEWS_NOT_FOUND_CODE

    guest_draft_detail = request_payload(
        http,
        base_url,
        "GET",
        f"/api/v1/news/{draft_news['id']}",
        step_name="guest get draft news detail forbidden by visibility",
        expected_status=404,
    )
    assert guest_draft_detail["code"] == NEWS_NOT_FOUND_CODE

    tenant_notifications_after_create = list_notifications(api_request, auth_headers, tenant_token)
    landlord_notifications_after_create = list_notifications(api_request, auth_headers, landlord_token)
    assert len(tenant_notifications_after_create) == 1
    assert len(landlord_notifications_after_create) == 1
    assert tenant_notifications_after_create[0]["source_type"] == "news"
    assert tenant_notifications_after_create[0]["source_id"] == published_news["id"]

    updated_published = api_request(
        "PATCH",
        f"/api/v1/news/{published_news['id']}",
        step_name="admin update published news",
        expected_status=200,
        headers=auth_headers(admin_token),
        json={"content": "Updated published content"},
    )["data"]
    assert updated_published["content"] == "Updated published content"

    published_from_draft = api_request(
        "PATCH",
        f"/api/v1/news/{draft_news['id']}",
        step_name="admin publish draft news",
        expected_status=200,
        headers=auth_headers(admin_token),
        json={"status": "published"},
    )["data"]
    assert published_from_draft["status"] == "published"

    tenant_notifications_after_update = list_notifications(api_request, auth_headers, tenant_token)
    landlord_notifications_after_update = list_notifications(api_request, auth_headers, landlord_token)
    assert len(tenant_notifications_after_update) == 3
    assert len(landlord_notifications_after_update) == 3
    assert {item["source_id"] for item in tenant_notifications_after_update} >= {
        draft_news["id"],
        published_news["id"],
    }

    api_request(
        "DELETE",
        f"/api/v1/news/{published_news['id']}",
        step_name="admin delete published news",
        expected_status=200,
        headers=auth_headers(admin_token),
    )

    deleted_detail = request_payload(
        http,
        base_url,
        "GET",
        f"/api/v1/news/{published_news['id']}",
        step_name="get deleted news detail",
        expected_status=404,
        headers=auth_headers(admin_token),
    )
    assert deleted_detail["code"] == NEWS_NOT_FOUND_CODE

    tenant_notifications_after_delete = list_notifications(api_request, auth_headers, tenant_token)
    assert len(tenant_notifications_after_delete) == 3
    assert any(item["source_id"] == published_news["id"] for item in tenant_notifications_after_delete)

    final_tenant_news_list = api_request(
        "GET",
        "/api/v1/news",
        step_name="tenant list news after delete",
        expected_status=200,
        headers=auth_headers(tenant_token),
        params={"page": 1, "page_size": 20},
    )["data"]["list"]
    assert find_news_item(final_tenant_news_list, draft_news["id"]) is not None
    assert find_news_item(final_tenant_news_list, published_news["id"]) is None


def test_news_permissions_and_validation(
    unique_suffix: str,
    api_request,
    auth_headers,
    http: requests.Session,
    base_url: str,
) -> None:
    _, tenant_token = create_user_and_login(f"tenant_perm_{unique_suffix}", "tenant", api_request)
    _, landlord_token = create_user_and_login(f"landlord_perm_{unique_suffix}", "landlord", api_request)
    _, admin_token = create_user_and_login(f"admin_perm_{unique_suffix}", "admin", api_request)

    created_news = api_request(
        "POST",
        "/api/v1/news",
        step_name="admin create news for permission tests",
        expected_status=201,
        headers=auth_headers(admin_token),
        json={
            "title": f"Permission news {unique_suffix}",
            "content": "Permission content",
            "status": "published",
        },
    )["data"]

    tenant_create_forbidden = request_payload(
        http,
        base_url,
        "POST",
        "/api/v1/news",
        step_name="tenant create news forbidden",
        expected_status=403,
        headers=auth_headers(tenant_token),
        json={"title": "Nope", "content": "Nope", "status": "draft"},
    )
    assert tenant_create_forbidden["code"] == FORBIDDEN_CODE

    landlord_update_forbidden = request_payload(
        http,
        base_url,
        "PATCH",
        f"/api/v1/news/{created_news['id']}",
        step_name="landlord update news forbidden",
        expected_status=403,
        headers=auth_headers(landlord_token),
        json={"content": "Not allowed"},
    )
    assert landlord_update_forbidden["code"] == FORBIDDEN_CODE

    tenant_delete_forbidden = request_payload(
        http,
        base_url,
        "DELETE",
        f"/api/v1/news/{created_news['id']}",
        step_name="tenant delete news forbidden",
        expected_status=403,
        headers=auth_headers(tenant_token),
    )
    assert tenant_delete_forbidden["code"] == FORBIDDEN_CODE

    invalid_title = request_payload(
        http,
        base_url,
        "POST",
        "/api/v1/news",
        step_name="create news with blank title",
        expected_status=400,
        headers=auth_headers(admin_token),
        json={"title": "   ", "content": "Valid content", "status": "draft"},
    )
    assert invalid_title["code"] == 3001

    invalid_content = request_payload(
        http,
        base_url,
        "POST",
        "/api/v1/news",
        step_name="create news with blank content",
        expected_status=400,
        headers=auth_headers(admin_token),
        json={"title": "Valid title", "content": "   ", "status": "draft"},
    )
    assert invalid_content["code"] == 3001

    overlong_content = request_payload(
        http,
        base_url,
        "POST",
        "/api/v1/news",
        step_name="create news with overlong content",
        expected_status=400,
        headers=auth_headers(admin_token),
        json={"title": "Valid title", "content": "x" * 5001, "status": "draft"},
    )
    assert overlong_content["code"] == 3001

    empty_patch = request_payload(
        http,
        base_url,
        "PATCH",
        f"/api/v1/news/{created_news['id']}",
        step_name="patch news with empty body",
        expected_status=400,
        headers=auth_headers(admin_token),
        json={},
    )
    assert empty_patch["code"] == 3001

    invalid_status = request_payload(
        http,
        base_url,
        "GET",
        "/api/v1/news",
        step_name="list news with invalid status",
        expected_status=400,
        headers=auth_headers(admin_token),
        params={"page": 1, "page_size": 10, "status": "archived"},
    )
    assert invalid_status["code"] == 3001

    invalid_page_size = request_payload(
        http,
        base_url,
        "GET",
        "/api/v1/news",
        step_name="list news with invalid page size",
        expected_status=400,
        params={"page": 1, "page_size": 101},
    )
    assert invalid_page_size["code"] == 3001

    missing_detail = request_payload(
        http,
        base_url,
        "GET",
        "/api/v1/news/99999999",
        step_name="get missing news detail",
        expected_status=404,
        headers=auth_headers(admin_token),
    )
    assert missing_detail["code"] == NEWS_NOT_FOUND_CODE

    missing_update = request_payload(
        http,
        base_url,
        "PATCH",
        "/api/v1/news/99999999",
        step_name="update missing news detail",
        expected_status=404,
        headers=auth_headers(admin_token),
        json={"content": "Missing"},
    )
    assert missing_update["code"] == NEWS_NOT_FOUND_CODE

    missing_delete = request_payload(
        http,
        base_url,
        "DELETE",
        "/api/v1/news/99999999",
        step_name="delete missing news detail",
        expected_status=404,
        headers=auth_headers(admin_token),
    )
    assert missing_delete["code"] == NEWS_NOT_FOUND_CODE
