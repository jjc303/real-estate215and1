from __future__ import annotations

from typing import Any

from flask import current_app
import requests


class AIEngineClientError(Exception):
    def __init__(
        self,
        message: str,
        *,
        path: str | None = None,
        status_code: int | None = None,
        upstream_code: object | None = None,
        upstream_msg: object | None = None,
    ) -> None:
        super().__init__(message)
        self.path = path
        self.status_code = status_code
        self.upstream_code = upstream_code
        self.upstream_msg = upstream_msg


class AIEngineClient:
    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout_seconds: int | None = None,
    ) -> None:
        self._base_url = base_url
        self._api_key = api_key
        self._timeout_seconds = timeout_seconds

    def house_chat(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._post("/api/v1/rental/house-chat", payload)

    def chat(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._post("/api/v1/rental/chat", payload)

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        base_url = self._get_base_url()
        timeout_seconds = self._get_timeout_seconds()
        headers = {"Content-Type": "application/json"}
        api_key = self._get_api_key()
        if api_key:
            headers["X-API-Key"] = api_key

        try:
            response = requests.post(
                f"{base_url.rstrip('/')}{path}",
                json=payload,
                headers=headers,
                timeout=timeout_seconds,
            )
        except requests.RequestException as exc:
            raise AIEngineClientError("ai engine request failed", path=path) from exc

        if response.status_code < 200 or response.status_code >= 300:
            raise AIEngineClientError(
                f"ai engine returned status {response.status_code}",
                path=path,
                status_code=response.status_code,
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise AIEngineClientError(
                "ai engine returned invalid json",
                path=path,
                status_code=response.status_code,
            ) from exc

        if not isinstance(data, dict):
            raise AIEngineClientError(
                "ai engine returned invalid payload",
                path=path,
                status_code=response.status_code,
            )

        if "code" in data or "msg" in data or "data" in data:
            upstream_code = data.get("code")
            upstream_msg = data.get("msg")
            if upstream_code != 200:
                raise AIEngineClientError(
                    "ai engine returned error payload",
                    path=path,
                    status_code=response.status_code,
                    upstream_code=upstream_code,
                    upstream_msg=upstream_msg,
                )

            inner = data.get("data")
            if not isinstance(inner, dict):
                raise AIEngineClientError(
                    "ai engine returned invalid payload",
                    path=path,
                    status_code=response.status_code,
                    upstream_code=upstream_code,
                    upstream_msg=upstream_msg,
                )
            return inner

        return data

    def _get_base_url(self) -> str:
        value = (self._base_url or current_app.config.get("AI_ENGINE_BASE_URL", "")).strip()
        if not value:
            raise AIEngineClientError("ai engine base url is not configured")
        return value

    def _get_api_key(self) -> str:
        return (self._api_key or current_app.config.get("AI_ENGINE_API_KEY", "")).strip()

    def _get_timeout_seconds(self) -> int:
        value = self._timeout_seconds or current_app.config.get("AI_ENGINE_TIMEOUT_SECONDS", 20)
        return int(value)
