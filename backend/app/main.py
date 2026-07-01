"""
FastAPI application factory and entry point.

Run with:
    uvicorn app.main:app --reload

The module exposes a single ``app`` object. Configuration is read from
environment variables / .env file via app.config.get_settings().
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.config import get_settings
from app.exceptions import register_exception_handlers
from app.logging_config import configure_logging, get_logger
from app.middleware import RequestIDMiddleware, RequestLoggingMiddleware

# Initialise logging before anything else so all startup messages are captured
_settings = get_settings()
configure_logging(level=_settings.LOG_LEVEL, use_json=_settings.LOG_JSON)

logger = get_logger(__name__)


# ── Lifespan ───────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Application lifespan manager.

    Code before ``yield`` runs at startup.
    Code after ``yield`` runs at shutdown.

    Subsequent modules will plug their own startup logic here
    (database pool, Redis connection, etc.).
    """
    settings = get_settings()

    logger.info(
        "Starting %s v%s [%s]",
        settings.APP_NAME,
        settings.APP_VERSION,
        settings.APP_ENV.upper(),
    )

    # ── Startup hooks (added per module) ───────────────────────────────────
    # Module 2: await database.connect()
    # Module 2: await redis.ping()
    # Module 3: ensure S3 bucket exists
    # Module 4: warm up AI model client

    logger.info("Application startup complete. Listening on %s:%d", settings.HOST, settings.PORT)

    yield  # ← application serves requests here

    # ── Shutdown hooks ─────────────────────────────────────────────────────
    # Module 2: await database.disconnect()
    # Module 2: await redis.close()

    logger.info("Application shutdown complete.")


# ── App Factory ────────────────────────────────────────────────────────────


def create_app() -> FastAPI:
    """
    Construct and configure the FastAPI application instance.

    Returns:
        A fully configured FastAPI application ready to be served by Uvicorn.
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.API_TITLE,
        description=settings.API_DESCRIPTION,
        version=settings.APP_VERSION,
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        openapi_url="/openapi.json" if settings.is_development else None,
        lifespan=lifespan,
    )

    # ── CORS ───────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    # ── Custom middleware (applied bottom-up; last-added runs first) ────────
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RequestIDMiddleware)

    # ── Exception handlers ─────────────────────────────────────────────────
    register_exception_handlers(app)

    # ── Routes ─────────────────────────────────────────────────────────────
    app.include_router(api_router)

    # ── Root-level utility routes (no /v1 prefix) ──────────────────────────
    @app.get("/ping", include_in_schema=False)
    async def ping() -> JSONResponse:
        """Ultra-lightweight liveness probe. Returns {"pong": true}."""
        return JSONResponse(content={"pong": True})

    logger.debug(
        "Application created — %d routes registered",
        len(app.routes),
    )

    return app


# Module-level ``app`` instance consumed by Uvicorn
app: FastAPI = create_app()
