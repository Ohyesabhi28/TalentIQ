"""
Common shared Pydantic models used across multiple domains.

These are thin data-transfer objects (DTOs) that do NOT contain business logic.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import EmailStr, Field, HttpUrl

from app.models.base import AppBaseModel, IdentifiableMixin, TimestampMixin


# ── User ───────────────────────────────────────────────────────────────────


class UserRole(str):
    RECRUITER = "recruiter"
    ADMIN = "admin"
    VIEWER = "viewer"


class UserRead(IdentifiableMixin, TimestampMixin):
    """
    Public representation of a User.
    Matches the ``User`` model in the API contract.
    """

    name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    role: Literal["recruiter", "admin", "viewer"] = "recruiter"
    avatar_url: str | None = None


# ── Session / Auth ─────────────────────────────────────────────────────────


class SessionRead(AppBaseModel):
    """
    Returned after a successful login or token refresh.
    Matches the ``Session`` model in the API contract.
    """

    access_token: str
    token_type: Literal["Bearer"] = "Bearer"
    expires_in: int = Field(description="Seconds until access_token expires.")
    refresh_token: str
    user: UserRead


# ── Uploaded File ──────────────────────────────────────────────────────────


class UploadedFileRead(IdentifiableMixin):
    """
    Returned after a successful file upload.
    Matches the ``UploadedFile`` model in the API contract.
    """

    name: str
    size: int = Field(ge=0, description="File size in bytes.")
    mime_type: str
    upload_url: str | None = Field(
        default=None,
        description="Pre-signed URL for direct client-side access (if applicable).",
    )
    uploaded_at: datetime


# ── Notification ───────────────────────────────────────────────────────────


class NotificationRead(IdentifiableMixin):
    """Single notification item returned by GET /notifications."""

    type: Literal["analysis_complete", "ticket_updated", "system"]
    title: str
    body: str
    read: bool = False


class NotificationsResponse(AppBaseModel):
    """Response body for GET /notifications."""

    unread_count: int = Field(ge=0)
    notifications: list[NotificationRead] = Field(default_factory=list)


# ── Support Ticket ─────────────────────────────────────────────────────────


class SupportTicketCreate(AppBaseModel):
    """Request body for POST /support/tickets."""

    name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    description: str = Field(min_length=10, max_length=5000)


class SupportTicketRead(IdentifiableMixin):
    """
    Returned after creating a support ticket.
    Matches the ``SupportTicket`` model in the API contract.
    """

    ticket_number: str
    name: str
    email: EmailStr
    description: str
    status: Literal["open", "in_progress", "resolved"] = "open"


# ── Health ─────────────────────────────────────────────────────────────────


class ServiceHealth(AppBaseModel):
    """Status of an individual backing service (database, redis, etc.)."""

    name: str
    status: Literal["healthy", "degraded", "unhealthy"]
    latency_ms: float | None = None
    detail: str | None = None


class HealthRead(AppBaseModel):
    """Response body for GET /health."""

    status: Literal["healthy", "degraded", "unhealthy"]
    version: str
    environment: str
    services: list[ServiceHealth] = Field(default_factory=list)
