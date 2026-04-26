from __future__ import annotations

import os
import time
from uuid import uuid4

import pytest
import requests


DEFAULT_BASE_URL = "http://127.0.0.1:8000"


@pytest.fixture
def base_url() -> str:
    return os.getenv("API_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


@pytest.fixture
def http() -> requests.Session:
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def unique_suffix() -> str:
    return f"{int(time.time() * 1000)}_{uuid4().hex[:8]}"


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers():
    return _auth_headers


def _api_request(
    http: requests.Session,
    method: str,
    base_url: str,
    path: str,
    *,
    step_name: str,
    expected_status: int,
    headers: dict[str, str] | None = None,
    json: dict[str, object] | None = None,
    params: dict[str, object] | None = None,
) -> dict[str, object]:
    response = http.request(
        method=method,
        url=f"{base_url}{path}",
        headers=headers,
        json=json,
        params=params,
        timeout=20,
    )
    return assert_success(
        response,
        step_name=step_name,
        method=method,
        url=f"{base_url}{path}",
        expected_status=expected_status,
    )


def assert_success(
    response: requests.Response,
    *,
    step_name: str,
    method: str,
    url: str,
    expected_status: int,
) -> dict[str, object]:
    try:
        payload = response.json()
    except ValueError as exc:
        raise AssertionError(
            f"{step_name} failed: {method} {url} returned non-JSON response; "
            f"expected HTTP {expected_status}, got HTTP {response.status_code}; "
            f"body={response.text!r}"
        ) from exc

    if response.status_code != expected_status:
        raise AssertionError(
            f"{step_name} failed: {method} {url} expected HTTP {expected_status}, "
            f"got HTTP {response.status_code}; response={payload!r}"
        )

    if payload.get("code") != 0:
        raise AssertionError(
            f"{step_name} failed: {method} {url} expected code == 0, "
            f"got code={payload.get('code')!r}; response={payload!r}"
        )

    return payload


@pytest.fixture
def api_request(http: requests.Session, base_url: str):
    def _request(
        method: str,
        path: str,
        *,
        step_name: str,
        expected_status: int,
        headers: dict[str, str] | None = None,
        json: dict[str, object] | None = None,
        params: dict[str, object] | None = None,
    ) -> dict[str, object]:
        return _api_request(
            http,
            method,
            base_url,
            path,
            step_name=step_name,
            expected_status=expected_status,
            headers=headers,
            json=json,
            params=params,
        )

    return _request
