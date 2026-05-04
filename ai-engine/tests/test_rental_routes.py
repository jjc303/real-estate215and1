"""Route tests for rental AI endpoints."""

from fastapi.testclient import TestClient

from api.main import app


class FakeRentalService:
    async def ahouse_chat(self, **kwargs):
        return {
            "answer": "这套房月租 3000 元，押金 3000 元。",
            "session_id": kwargs["session_id"],
            "sources": [],
            "suggestions": [],
            "metadata": {"mode": "house-chat"},
        }

    async def achat(self, **kwargs):
        return {
            "answer": "签合同前建议确认租金、押金、租期和违约责任。",
            "session_id": kwargs["session_id"],
            "sources": [],
            "suggestions": [],
            "metadata": {"mode": "general-chat"},
        }


def _auth_headers():
    return {"X-API-Key": "test-api-key"}


def test_house_chat_route_success(monkeypatch, test_env):
    monkeypatch.setattr("api.routes.rental.get_required_service", lambda *args: FakeRentalService())
    client = TestClient(app)

    response = client.post(
        "/api/v1/rental/house-chat",
        headers=_auth_headers(),
        json={
            "user_id": "rental_user_1",
            "session_id": "rental:house:1:user:1",
            "message": "这套房押金多少？",
            "user_context": {"id": 1, "role": "tenant"},
            "house_context": {"id": 1, "title": "一室一厅", "status": "listed"},
            "platform_context": {"domain": "rental", "source": "real-estate-platform"},
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["code"] == 200
    assert payload["data"]["answer"]


def test_general_chat_route_success(monkeypatch, test_env):
    monkeypatch.setattr("api.routes.rental.get_required_service", lambda *args: FakeRentalService())
    client = TestClient(app)

    response = client.post(
        "/api/v1/rental/chat",
        headers=_auth_headers(),
        json={
            "user_id": "rental_user_2",
            "session_id": "rental:general:user:2",
            "message": "签合同要注意什么？",
            "user_context": {"id": 2, "role": "tenant"},
            "platform_context": {"domain": "rental", "source": "real-estate-platform"},
        },
    )

    assert response.status_code == 200
    assert response.json()["data"]["session_id"] == "rental:general:user:2"


def test_house_context_missing_returns_validation_error(test_env):
    client = TestClient(app)

    response = client.post(
        "/api/v1/rental/house-chat",
        headers=_auth_headers(),
        json={
            "user_id": "rental_user_1",
            "session_id": "rental:house:1:user:1",
            "message": "这套房押金多少？",
            "user_context": {"id": 1, "role": "tenant"},
            "platform_context": {"domain": "rental", "source": "real-estate-platform"},
        },
    )

    assert response.status_code == 422


def test_invalid_api_key_rejected(test_env):
    client = TestClient(app)

    response = client.post(
        "/api/v1/rental/chat",
        headers={"X-API-Key": "wrong"},
        json={
            "user_id": "rental_user_2",
            "session_id": "rental:general:user:2",
            "message": "签合同要注意什么？",
            "user_context": {"id": 2, "role": "tenant"},
            "platform_context": {"domain": "rental", "source": "real-estate-platform"},
        },
    )

    assert response.status_code == 401


def test_legacy_api_key_header_rejected(test_env):
    client = TestClient(app)

    response = client.post(
        "/api/v1/rental/chat",
        headers={"api-key": "test-api-key"},
        json={
            "user_id": "rental_user_2",
            "session_id": "rental:general:user:2",
            "message": "绛惧悎鍚岃娉ㄦ剰浠€涔堬紵",
            "user_context": {"id": 2, "role": "tenant"},
            "platform_context": {"domain": "rental", "source": "real-estate-platform"},
        },
    )

    assert response.status_code == 401


def test_status_route_still_available(monkeypatch, test_env):
    monkeypatch.setattr(
        "api.routes.status.service_manager.get_runtime_status",
        lambda: {
            "generated_at": "2026-05-04T00:00:00+00:00",
            "summary": "租房 AI 引擎运行正常。",
            "overall_status": "ok",
            "total_services": 3,
            "initialized_services": 3,
            "healthy_services": 3,
            "warning_services": 0,
            "error_services": 0,
            "degraded_services": [],
            "unavailable_services": [],
            "services": [],
        },
    )
    client = TestClient(app)
    response = client.get("/api/v1/status", headers=_auth_headers())
    assert response.status_code == 200
    assert response.json()["data"]["overall_status"] == "ok"
