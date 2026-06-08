from __future__ import annotations

from decimal import Decimal
import logging
from typing import Any

from flask import current_app, has_app_context
from sqlalchemy.orm import Session

from app.common.ai_engine_client import AIEngineClient, AIEngineClientError
from app.core.exceptions import (
    ForbiddenException,
    HouseNotFoundException,
    InternalServerException,
    UnauthorizedException,
)
from app.modules.house.model import House
from app.modules.house.repository import HouseRepository
from app.modules.user.model import User
from app.modules.user.repository import UserRepository

logger = logging.getLogger(__name__)


class AIService:
    def __init__(
        self,
        user_repository: UserRepository,
        house_repository: HouseRepository,
        ai_engine_client: AIEngineClient,
    ) -> None:
        self.user_repository = user_repository
        self.house_repository = house_repository
        self.ai_engine_client = ai_engine_client

    def house_chat(
        self,
        db: Session,
        *,
        current_user_id: int,
        house_id: int,
        message: str,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        user = self._get_active_user(db, current_user_id)
        house = self.house_repository.get_by_id(db, house_id)
        if house is None or house.deleted_at is not None:
            raise HouseNotFoundException()

        self._ensure_house_visible_to_user(user, house)
        resolved_session_id = session_id or f"rental:house:{house_id}:user:{current_user_id}"
        payload = {
            "user_id": f"rental_user_{current_user_id}",
            "session_id": resolved_session_id,
            "message": message,
            "user_context": {
                "id": user.id,
                "role": user.role,
            },
            "house_context": self._build_house_context(house),
            "platform_context": {
                "domain": "rental",
                "source": "real-estate-platform",
            },
        }

        try:
            result = self.ai_engine_client.house_chat(payload)
        except AIEngineClientError as exc:
            self._log_engine_error(exc)
            raise InternalServerException(message="internal server error") from exc

        return self._normalize_ai_result(result, resolved_session_id)

    def chat(
        self,
        db: Session,
        *,
        current_user_id: int,
        message: str,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        user = self._get_active_user(db, current_user_id)
        resolved_session_id = session_id or f"rental:general:user:{current_user_id}"
        payload = {
            "user_id": f"rental_user_{current_user_id}",
            "session_id": resolved_session_id,
            "message": message,
            "user_context": {
                "id": user.id,
                "role": user.role,
            },
            "platform_context": {
                "domain": "rental",
                "source": "real-estate-platform",
            },
        }

        try:
            result = self.ai_engine_client.chat(payload)
        except AIEngineClientError as exc:
            self._log_engine_error(exc)
            raise InternalServerException(message="internal server error") from exc

        return self._normalize_ai_result(result, resolved_session_id)

    def _get_active_user(self, db: Session, user_id: int) -> User:
        user = self.user_repository.get_by_id(db, user_id)
        if user is None:
            raise UnauthorizedException(message="unauthorized")
        if user.status != "active":
            raise ForbiddenException(message="user status is not allowed")
        return user

    def _ensure_house_visible_to_user(self, user: User, house: House) -> None:
        if house.status in {"listed", "rented", "maintenance"}:
            return
        if house.status in {"draft", "offline"}:
            if user.role == "admin" or house.landlord_id == user.id:
                return
            raise ForbiddenException(message="forbidden")
        raise HouseNotFoundException()

    def _build_house_context(self, house: House) -> dict[str, Any]:
        return {
            "id": house.id,
            "title": house.title,
            "region": house.region,
            "address": house.address,
            "community": house.community,
            "house_type": house.house_type,
            "area": self._to_number(house.area),
            "rent": self._to_number(house.rent),
            "deposit": self._to_number(house.deposit),
            "decoration": house.decoration,
            "floor": house.floor,
            "orientation": house.orientation,
            "description": house.description,
            "status": house.status,
        }

    def _normalize_ai_result(self, result: dict[str, Any], fallback_session_id: str) -> dict[str, Any]:
        answer = result.get("answer")
        if not isinstance(answer, str) or answer.strip() == "":
            raise InternalServerException(message="internal server error")

        payload: dict[str, Any] = {
            "answer": answer,
            "session_id": result.get("session_id") or fallback_session_id,
            "sources": result.get("sources") if isinstance(result.get("sources"), list) else [],
            "suggestions": result.get("suggestions") if isinstance(result.get("suggestions"), list) else [],
            "metadata": result.get("metadata") if isinstance(result.get("metadata"), dict) else {},
        }
        return payload

    def _to_number(self, value: Decimal | None) -> float | None:
        if value is None:
            return None
        return float(value)

    def _log_engine_error(self, exc: AIEngineClientError) -> None:
        active_logger = current_app.logger if has_app_context() else logger
        active_logger.error(
            "AI engine request failed: path=%s status=%s upstream_code=%s upstream_msg=%s error=%s",
            exc.path,
            exc.status_code,
            exc.upstream_code,
            exc.upstream_msg,
            str(exc),
        )
