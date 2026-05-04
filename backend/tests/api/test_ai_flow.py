from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any

import pytest

BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.container import services as service_container
from app.factory import create_app


@dataclass
class DummyUser:
    id: int
    role: str = "tenant"
    status: str = "active"


@dataclass
class DummyHouse:
    id: int
    landlord_id: int
    title: str = "近地铁一室一厅"
    region: str = "浦东新区"
    address: str = "xx路88号"
    community: str | None = "阳光花园"
    house_type: str = "1室1厅1卫"
    area: float = 58.0
    rent: float = 3200.0
    deposit: float = 3200.0
    decoration: str | None = "精装"
    floor: str | None = "8/18"
    orientation: str | None = "南"
    description: str | None = "拎包入住"
    status: str = "listed"
    deleted_at: object | None = None


class FakeUserRepository:
    def __init__(self, users: dict[int, DummyUser]) -> None:
        self.users = users

    def get_by_id(self, db, user_id: int):
        return self.users.get(user_id)


class FakeHouseRepository:
    def __init__(self, houses: dict[int, DummyHouse]) -> None:
        self.houses = houses

    def get_by_id(self, db, house_id: int):
        return self.houses.get(house_id)


class FakeResponse:
    def __init__(self, *, status_code: int, payload: Any = None, text: str = "ok") -> None:
        self.status_code = status_code
        self._payload = payload
        self.text = text

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload


@pytest.fixture
def ai_test_client(monkeypatch):
    monkeypatch.setenv("DATABASE_URI", "sqlite:///:memory:")
    monkeypatch.setenv("AI_ENGINE_BASE_URL", "http://ai-engine:9000")
    monkeypatch.setenv("AI_ENGINE_API_KEY", "change-me")
    monkeypatch.setenv("AI_ENGINE_TIMEOUT_SECONDS", "20")

    service_container._ai_service.user_repository = FakeUserRepository({1: DummyUser(id=1)})
    service_container._ai_service.house_repository = FakeHouseRepository(
        {1: DummyHouse(id=1, landlord_id=2)}
    )

    app = create_app("testing")
    app.testing = True
    monkeypatch.setattr("app.modules.ai.router.get_required_current_user_id", lambda: 1)

    with app.test_client() as client:
        yield client


def test_house_chat_http_unwraps_ai_engine_data_shell(ai_test_client, monkeypatch) -> None:
    def fake_post(url, json, headers, timeout):
        return FakeResponse(
            status_code=200,
            payload={
                "code": 200,
                "msg": "success",
                "data": {
                    "answer": "这套房月租 3200 元，押金 3200 元。",
                    "session_id": "rental:house:1:user:1",
                },
            },
        )

    monkeypatch.setattr("app.common.ai_engine_client.requests.post", fake_post)

    response = ai_test_client.post(
        "/api/v1/ai/house-chat",
        json={"house_id": 1, "message": "这套房押金多少？"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["code"] == 0
    assert payload["data"]["answer"] == "这套房月租 3200 元，押金 3200 元。"
    assert payload["data"]["session_id"] == "rental:house:1:user:1"
    assert payload["data"]["sources"] == []
    assert payload["data"]["suggestions"] == []
    assert payload["data"]["metadata"] == {}


def test_general_chat_http_returns_stable_optional_fields(ai_test_client, monkeypatch) -> None:
    def fake_post(url, json, headers, timeout):
        return FakeResponse(
            status_code=200,
            payload={
                "code": 200,
                "msg": "success",
                "data": {
                    "answer": "签合同时建议重点确认租金、押金和违约责任。",
                    "session_id": "rental:general:user:1",
                    "metadata": {"mode": "general-chat"},
                },
            },
        )

    monkeypatch.setattr("app.common.ai_engine_client.requests.post", fake_post)

    response = ai_test_client.post("/api/v1/ai/chat", json={"message": "租房合同要注意什么？"})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["code"] == 0
    assert payload["data"]["sources"] == []
    assert payload["data"]["suggestions"] == []
    assert payload["data"]["metadata"] == {"mode": "general-chat"}


def test_house_chat_forbidden_for_non_owner_draft_house(ai_test_client, monkeypatch) -> None:
    service_container._ai_service.house_repository = FakeHouseRepository(
        {1: DummyHouse(id=1, landlord_id=2, status="draft")}
    )
    monkeypatch.setattr(
        "app.common.ai_engine_client.requests.post",
        lambda *args, **kwargs: FakeResponse(status_code=200, payload={"code": 200, "msg": "success", "data": {"answer": "ok"}}),
    )

    response = ai_test_client.post(
        "/api/v1/ai/house-chat",
        json={"house_id": 1, "message": "可以预约吗？"},
    )

    assert response.status_code == 403
    payload = response.get_json()
    assert payload["code"] == 1004


def test_house_chat_allows_owner_for_offline_house(ai_test_client, monkeypatch) -> None:
    service_container._ai_service.user_repository = FakeUserRepository({2: DummyUser(id=2, role="landlord")})
    service_container._ai_service.house_repository = FakeHouseRepository(
        {1: DummyHouse(id=1, landlord_id=2, status="offline")}
    )
    monkeypatch.setattr("app.modules.ai.router.get_required_current_user_id", lambda: 2)

    def fake_post(url, json, headers, timeout):
        return FakeResponse(
            status_code=200,
            payload={"code": 200, "msg": "success", "data": {"answer": "房东可查看", "session_id": json["session_id"]}},
        )

    monkeypatch.setattr("app.common.ai_engine_client.requests.post", fake_post)

    response = ai_test_client.post(
        "/api/v1/ai/house-chat",
        json={"house_id": 1, "message": "房东自己提问"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["code"] == 0
    assert payload["data"]["session_id"] == "rental:house:1:user:2"


def test_ai_engine_payload_error_maps_to_5000(ai_test_client, monkeypatch) -> None:
    def fake_post(url, json, headers, timeout):
        return FakeResponse(
            status_code=200,
            payload={"code": 503, "msg": "upstream unavailable", "data": None},
        )

    monkeypatch.setattr("app.common.ai_engine_client.requests.post", fake_post)

    response = ai_test_client.post("/api/v1/ai/chat", json={"message": "hello"})

    assert response.status_code == 500
    payload = response.get_json()
    assert payload["code"] == 5000


def test_ai_engine_invalid_data_payload_maps_to_5000(ai_test_client, monkeypatch) -> None:
    def fake_post(url, json, headers, timeout):
        return FakeResponse(
            status_code=200,
            payload={"code": 200, "msg": "success", "data": "not-a-dict"},
        )

    monkeypatch.setattr("app.common.ai_engine_client.requests.post", fake_post)

    response = ai_test_client.post("/api/v1/ai/chat", json={"message": "hello"})

    assert response.status_code == 500
    payload = response.get_json()
    assert payload["code"] == 5000
