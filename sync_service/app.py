"""FastAPI 애플리케이션 팩토리."""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

from .config import Settings, get_settings
from .routes.health import router as health_router

logger = structlog.get_logger(__name__)


def configure_logging() -> None:
    """구조화 로깅 기본 설정."""

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(structlog.INFO),
        cache_logger_on_first_use=True,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):  # type: ignore[override]
    """애플리케이션 라이프사이클 훅."""

    configure_logging()
    logger.info("startup", app=app.title)
    try:
        yield
    finally:
        logger.info("shutdown", app=app.title)


def create_app(settings: Settings | None = None) -> FastAPI:
    """FastAPI 애플리케이션을 생성한다."""

    settings = settings or get_settings()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.include_router(health_router, prefix=settings.api_prefix)
    return app
