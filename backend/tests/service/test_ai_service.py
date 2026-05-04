from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

import pytest

BASE_DIR = Path(__file__).resolve().parents[2]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.common.ai_engine_client import AIEngineClientError
from app.core.exceptions import ForbiddenException, HouseNotFoundException, InternalServerException, UnauthorizedException
from app.modules.ai.service import AIService


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


class FakeAIEngineClient:
    def __init__(self, *, should_fail: bool = False) -> None:
        self.should_fail = should_fail
        self.last_house_payload = None
        self.last_chat_payload = None

    def house_chat(self, payload):
        if self.should_fail:
            raise AIEngineClientError("boom")
        self.last_house_payload = payload
        return {
            "answer": "这套房月租 3200 元，押金 3200 元。",
            "session_id": payload["session_id"],
            "sources": [],
            "suggestions": ["可以继续询问通勤和配套"],
        }

    def chat(self, payload):
        if self.should_fail:
            raise AIEngineClientError("boom")
        self.last_chat_payload = payload
        return {
            "answer": "签合同要重点确认租金、押金、租期和违约责任。",
            "session_id": payload["session_id"],
        }


def build_service(
    *,
    users: dict[int, DummyUser] | None = None,
    houses: dict[int, DummyHouse] | None = None,
    client: FakeAIEngineClient | None = None,
) -> tuple[AIService, FakeAIEngineClient]:
    fake_client = client or FakeAIEngineClient()
    service = AIService(
        FakeUserRepository(users if users is not None else {1: DummyUser(id=1)}),
        FakeHouseRepository(houses if houses is not None else {1: DummyHouse(id=1, landlord_id=2)}),
        fake_client,
    )
    return service, fake_client


def test_house_chat_allows_listed_house_for_logged_in_user() -> None:
    service, client = build_service()

    result = service.house_chat(
        None,
        current_user_id=1,
        house_id=1,
        message="这套房押金多少？",
    )

    assert result["answer"]
    assert result["session_id"] == "rental:house:1:user:1"
    assert client.last_house_payload["user_id"] == "rental_user_1"
    assert client.last_house_payload["house_context"]["rent"] == 3200.0


def test_house_chat_forbids_non_owner_for_draft_house() -> None:
    service, _ = build_service(
        houses={1: DummyHouse(id=1, landlord_id=2, status="draft")},
    )

    with pytest.raises(ForbiddenException):
        service.house_chat(None, current_user_id=1, house_id=1, message="可以预约吗？")


def test_house_chat_allows_owner_for_offline_house() -> None:
    service, client = build_service(
        users={2: DummyUser(id=2, role="landlord")},
        houses={1: DummyHouse(id=1, landlord_id=2, status="offline")},
    )

    result = service.house_chat(None, current_user_id=2, house_id=1, message="这套房还在吗？")

    assert result["session_id"] == "rental:house:1:user:2"
    assert client.last_house_payload["user_context"]["role"] == "landlord"


def test_house_chat_allows_admin_for_draft_house() -> None:
    service, _ = build_service(
        users={9: DummyUser(id=9, role="admin")},
        houses={1: DummyHouse(id=1, landlord_id=2, status="draft")},
    )

    result = service.house_chat(None, current_user_id=9, house_id=1, message="检查房源信息")
    assert result["answer"]


def test_house_chat_raises_when_house_missing() -> None:
    service, _ = build_service(houses={})

    with pytest.raises(HouseNotFoundException):
        service.house_chat(None, current_user_id=1, house_id=1, message="hello")


def test_house_chat_raises_internal_error_when_engine_fails() -> None:
    service, _ = build_service(client=FakeAIEngineClient(should_fail=True))

    with pytest.raises(InternalServerException):
        service.house_chat(None, current_user_id=1, house_id=1, message="hello")


def test_chat_success_uses_default_session_id() -> None:
    service, client = build_service()

    result = service.chat(None, current_user_id=1, message="租房合同要注意什么？")

    assert result["session_id"] == "rental:general:user:1"
    assert client.last_chat_payload["platform_context"]["domain"] == "rental"


def test_chat_rejects_missing_user() -> None:
    service, _ = build_service(users={})

    with pytest.raises(UnauthorizedException):
        service.chat(None, current_user_id=1, message="hello")


def test_chat_rejects_disabled_user() -> None:
    service, _ = build_service(users={1: DummyUser(id=1, status="disabled")})

    with pytest.raises(ForbiddenException):
        service.chat(None, current_user_id=1, message="hello")
