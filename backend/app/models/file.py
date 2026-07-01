"""
File domain models.

Separates the internal stored record (with local_path, md5_hash, file_type)
from the public API response (which matches the API contract exactly).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal
from uuid import UUID

from pydantic import Field

from app.models.base import AppBaseModel, IdentifiableMixin


def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


# ── Internal Record (not exposed to API) ───────────────────────────────────


class UploadedFileRecord(IdentifiableMixin):
    """
    Full internal representation of an uploaded file.

    Stored in the in-memory store.  Contains fields that are never
    sent to the client (local_path, md5_hash, file_type).
    """

    name: str = Field(description="Sanitized filename used on disk.")
    original_name: str = Field(description="Raw filename as uploaded by the client.")
    size: int = Field(ge=0, description="File size in bytes.")
    mime_type: str
    file_type: Literal["job_description", "resume"]
    local_path: str = Field(description="Absolute filesystem path.")
    md5_hash: str = Field(description="MD5 of file content for duplicate detection.")
    uploaded_at: datetime = Field(default_factory=_utcnow)


# ── Public API Response ────────────────────────────────────────────────────


class UploadedFileRead(AppBaseModel):
    """
    Public response for a successfully uploaded file.

    Matches the ``UploadedFile`` model in the API contract exactly.
    """

    id: UUID
    name: str
    size: int = Field(ge=0)
    mime_type: str
    upload_url: str | None = Field(
        default=None,
        description="Pre-signed URL for direct download (not yet wired).",
    )
    uploaded_at: datetime

    @classmethod
    def from_record(cls, record: UploadedFileRecord) -> "UploadedFileRead":
        """Convert an internal record to the public API shape."""
        return cls(
            id=record.id,
            name=record.original_name,  # show the original name to the client
            size=record.size,
            mime_type=record.mime_type,
            upload_url=None,
            uploaded_at=record.uploaded_at,
        )


# ── Request Forms ──────────────────────────────────────────────────────────


class FileTypeAnnotation:
    """Valid values for the ``file_type`` form field."""

    JOB_DESCRIPTION = "job_description"
    RESUME = "resume"
    VALUES = frozenset({JOB_DESCRIPTION, RESUME})
