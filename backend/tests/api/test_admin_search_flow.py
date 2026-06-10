"""Integration tests for admin search functionality."""

from __future__ import annotations


def _admin_token(api_request, auth_headers):
    """Get admin token for testing."""
    return api_request(
        "POST", "/api/v1/auth/login",
        step_name="admin login",
        expected_status=200,
        json={"username": "admin_00000", "password": "123456"},
    )["data"]["token"]


def test_admin_search_users_by_keyword(
    unique_suffix: str,
    api_request,
    auth_headers,
) -> None:
    username = f"asearch_{unique_suffix}"
    password = "Password123!"
    api_request(
        "POST", "/api/v1/users",
        step_name="register user for search",
        expected_status=201,
        json={"username": username, "password": password, "role": "tenant"},
    )
    admin_token = _admin_token(api_request, auth_headers)

    result = api_request(
        "GET", "/api/v1/admin/users",
        step_name="search users by keyword",
        expected_status=200,
        headers=auth_headers(admin_token),
        params={"keyword": unique_suffix},
    )
    assert result["data"]["total"] >= 1
    usernames = [u["username"] for u in result["data"]["list"]]
    assert username in usernames


def test_admin_search_users_by_role(
    unique_suffix: str,
    api_request,
    auth_headers,
) -> None:
    admin_token = _admin_token(api_request, auth_headers)

    result = api_request(
        "GET", "/api/v1/admin/users",
        step_name="search users by role",
        expected_status=200,
        headers=auth_headers(admin_token),
        params={"role": "admin"},
    )
    assert result["data"]["total"] >= 1


def test_admin_search_houses_by_status(
    unique_suffix: str,
    api_request,
    auth_headers,
) -> None:
    admin_token = _admin_token(api_request, auth_headers)

    result = api_request(
        "GET", "/api/v1/admin/houses",
        step_name="admin search houses by status",
        expected_status=200,
        headers=auth_headers(admin_token),
        params={"status": "listed"},
    )
    assert result["data"]["total"] >= 1
    for house in result["data"]["list"]:
        assert house["status"] == "listed"


def test_admin_search_bills_by_status(
    unique_suffix: str,
    api_request,
    auth_headers,
) -> None:
    admin_token = _admin_token(api_request, auth_headers)

    result = api_request(
        "GET", "/api/v1/admin/bills",
        step_name="admin list bills",
        expected_status=200,
        headers=auth_headers(admin_token),
        params={"status": "paid"},
    )
    assert "total" in result["data"]
    assert "list" in result["data"]
