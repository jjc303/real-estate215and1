"""API key authentication helpers."""

from fastapi import Header, HTTPException

from config.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)


def verify_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    """Verify the internal API key.

    `X-API-Key` is the canonical header for the rental engine.
    """
    expected_key = settings.AI_ENGINE_API_KEY
    if not expected_key:
        logger.error("AI engine API key is not configured")
        raise HTTPException(
            status_code=500,
            detail={"code": 500, "message": "AI engine API key is not configured"},
        )

    if x_api_key != expected_key:
        logger.warning("Invalid AI engine API key")
        raise HTTPException(
            status_code=401,
            detail={"code": 401, "message": "Invalid API key"},
        )
    return x_api_key
