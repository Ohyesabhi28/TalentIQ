"""
Custom ASGI middleware for the TalentIQ backend.

Middlewares in this module:
  - RequestLoggingMiddleware — logs every request with method, path, status, and timing.
  - RequestIDMiddleware     — attaches/propagates a unique X-Request-ID header.

Order matters: middleware is applied bottom-up (last-added runs first on request).
Register in main.py using app.add_middleware() in reverse priority order.
"""

from __future__ import annotations

import time
import uuid
from typing import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.logging_config import get_logger

logger = get_logger(__name__)

# Paths that should not appear in access logs (health/ping endpoints)
_SILENT_PATHS: frozenset[str] = frozenset({"/health", "/ping", "/favicon.ico"})


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Ensure every request carries a unique ``X-Request-ID`` correlation ID.

    - If the incoming request already has the header, its value is kept.
    - Otherwise a new UUID4 is generated and attached.
    - The ID is always echoed back in the response header.
    - The ID is stored in ``request.state.request_id`` for use by other layers.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Log structured access log entries for every HTTP request.

    Skips paths listed in _SILENT_PATHS to avoid log noise from health checks.

    Log fields:
      - method      HTTP method (GET, POST, …)
      - path        URL path
      - status      HTTP response status code
      - duration_ms Wall-clock time in milliseconds
      - request_id  Correlation ID from RequestIDMiddleware
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        if request.url.path in _SILENT_PATHS:
            return await call_next(request)

        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)

        request_id = getattr(request.state, "request_id", "-")

        log_fn = logger.warning if response.status_code >= 400 else logger.info
        log_fn(
            "%s %s → %d (%.1f ms)",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            extra={
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": duration_ms,
                "request_id": request_id,
            },
        )
        return response
