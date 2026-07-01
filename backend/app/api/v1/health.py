"""
Health check endpoint.

GET /v1/health

Returns a summary of the application's operational status.
In Module 1 (foundation), the backing services are not yet connected,
so their status is reported as "degraded" with an informative detail.

In later modules each service check will be replaced with a real probe.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.config import get_settings
from app.constants import HEALTH_STATUS_DEGRADED, HEALTH_STATUS_HEALTHY
from app.logging_config import get_logger
from app.models.common import HealthRead, ServiceHealth

logger = get_logger(__name__)

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthRead,
    summary="Health check",
    description=(
        "Returns the operational status of the API and its backing services. "
        "Use this endpoint for liveness and readiness probes."
    ),
)
async def health_check() -> HealthRead:
    """
    Perform a lightweight health check.

    Checks:
      - Application process (always healthy if this runs)
      - Database connectivity (stub — not yet connected)
      - Redis connectivity  (stub — not yet connected)

    Returns:
        HealthRead with overall status and per-service detail.
    """
    settings = get_settings()

    services: list[ServiceHealth] = [
        ServiceHealth(
            name="database",
            status=HEALTH_STATUS_DEGRADED,
            detail="Not connected yet — will be wired in Module 2.",
        ),
        ServiceHealth(
            name="redis",
            status=HEALTH_STATUS_DEGRADED,
            detail="Not connected yet — will be wired in Module 2.",
        ),
    ]

    # Overall status: healthy only if ALL services are healthy
    all_healthy = all(s.status == HEALTH_STATUS_HEALTHY for s in services)
    overall = HEALTH_STATUS_HEALTHY if all_healthy else HEALTH_STATUS_DEGRADED

    logger.debug("Health check completed — overall status: %s", overall)

    return HealthRead(
        status=overall,
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
        services=services,
    )


# Note: /ping is registered directly on the FastAPI app in main.py
# so it is available at /ping (without the /v1 prefix).
# This keeps the health router clean and avoids prefix conflicts.
