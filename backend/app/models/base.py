"""
Base Pydantic models shared across the entire application.

Rules:
  - All domain models inherit from AppBaseModel.
  - All API response models inherit from BaseResponse.
  - Use PaginatedResponse for list endpoints that support pagination.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Generic, TypeVar
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field


def _utcnow() -> datetime:
    """Return a timezone-aware UTC datetime (avoids deprecated datetime.utcnow())."""
    return datetime.now(tz=timezone.utc)


# ── Application Base ───────────────────────────────────────────────────────


class AppBaseModel(BaseModel):
    """
    Root base model for all domain models.

    - snake_case attributes on Python side.
    - camelCase aliases are NOT used here (the API contract uses snake_case).
    - Forbids extra fields to catch typos and accidental data leakage.
    """

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        str_strip_whitespace=True,
        frozen=False,
    )


# ── Identifiable Mixin ─────────────────────────────────────────────────────


class IdentifiableMixin(AppBaseModel):
    """Adds a UUID primary key and creation timestamp to any model."""

    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=_utcnow)


# ── Response Envelope ──────────────────────────────────────────────────────

DataT = TypeVar("DataT")


class BaseResponse(AppBaseModel, Generic[DataT]):
    """
    Standard success response envelope.

    Every successful endpoint returns:
        { "data": <payload> }
    """

    data: DataT


class PaginationMeta(AppBaseModel):
    """Pagination metadata included in list responses."""

    total: int = Field(ge=0, description="Total number of items across all pages.")
    page: int = Field(ge=1, description="Current page number (1-indexed).")
    per_page: int = Field(ge=1, le=100, description="Items per page.")

    @property
    def total_pages(self) -> int:
        if self.per_page == 0:
            return 0
        return -(-self.total // self.per_page)  # ceiling division

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_prev(self) -> bool:
        return self.page > 1


class PaginatedResponse(AppBaseModel, Generic[DataT]):
    """
    Paginated list response envelope.

    Returns:
        { "data": <list_payload>, "meta": { "total", "page", "per_page" } }
    """

    data: DataT
    meta: PaginationMeta


# ── Error Models ───────────────────────────────────────────────────────────


class ErrorDetail(AppBaseModel):
    """Represents the inner ``error`` object in the error envelope."""

    code: str = Field(description="Machine-readable error code from the API contract.")
    message: str = Field(description="Human-readable error description.")
    details: dict[str, Any] | None = Field(
        default=None,
        description="Optional extra context (e.g. validation field errors).",
    )


class ErrorResponse(AppBaseModel):
    """
    Standard error envelope returned for all non-2xx responses.

    Shape: { "error": { "code", "message", "details"? } }
    """

    error: ErrorDetail


# ── Shared Field Types ─────────────────────────────────────────────────────


class TimestampMixin(AppBaseModel):
    """Provides created_at and updated_at timestamps."""

    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)
