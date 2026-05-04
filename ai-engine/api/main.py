"""Rental AI engine FastAPI entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api.routes.rental import router as rental_router
from api.routes.status import router as status_router
from config.config import settings
from services.service_manager import service_manager
from utils.async_utils import AsyncExecutionHelper
from utils.exceptions import handle_exception
from utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and shutdown all services."""
    logger.info("Initializing rental AI engine services...")
    try:
        await AsyncExecutionHelper.run_blocking(service_manager.initialize_all)
        logger.info("Rental AI engine services initialized")
    except Exception as exc:
        logger.error(f"Service initialization failed: {exc}")

    yield

    logger.info("Shutting down rental AI engine services...")
    try:
        await AsyncExecutionHelper.run_blocking(service_manager.shutdown_all)
        logger.info("Rental AI engine services shut down")
    except Exception as exc:
        logger.error(f"Service shutdown failed: {exc}")


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "房地产租赁平台专用 AI 引擎。\n\n"
        "提供房源问答、通用租房顾问对话和运行状态检查能力。"
    ),
    version=settings.APP_VERSION,
    lifespan=lifespan,
)


@app.get("/")
def read_root():
    return {"message": "Hello from rental AI engine"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    http_exception = handle_exception(exc)
    return JSONResponse(
        status_code=http_exception.status_code,
        content={
            "code": http_exception.detail.get("code", http_exception.status_code),
            "msg": http_exception.detail.get("message", "Unknown error"),
            "data": None,
        },
    )


app.include_router(rental_router, prefix="/api/v1/rental")
app.include_router(status_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api.main:app", host=settings.HOST, port=settings.PORT, reload=True)
