"""
Analysis job domain models.

Covers the full status lifecycle:
  UPLOADED → PROCESSING → PARSING → EMBEDDING → SCORING → RANKING → COMPLETED
                                                                    ↘ FAILED

Progress stages map to the four-step pipeline shown in the Analyzing Loader screen.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Literal
from uuid import UUID

from pydantic import Field, computed_field

from app.models.base import AppBaseModel, IdentifiableMixin


def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


# ── Enums ──────────────────────────────────────────────────────────────────


class JobStatus(str, Enum):
    """
    Granular pipeline status.

    Maps to the four visible stages on the frontend Analyzing Loader screen.
    The frontend polls GET /analysis/jobs/{id} every 2 s and advances the
    stage indicators based on this value.
    """

    UPLOADED = "uploaded"      # Files received; job queued
    PROCESSING = "processing"  # Stage 1 active — JD semantic extraction
    PARSING = "parsing"        # Stage 2 active — resume parsing
    EMBEDDING = "embedding"    # Stage 3 active — cross-signal matching (part 1)
    SCORING = "scoring"        # Stage 3 active — cross-signal matching (part 2)
    RANKING = "ranking"        # Stage 4 active — recruiter insight generation
    COMPLETED = "completed"    # All stages done
    FAILED = "failed"          # Unrecoverable error


class StageStatus(str, Enum):
    PENDING = "pending"
    LOADING = "loading"
    DONE = "done"
    ERROR = "error"


# ── Stage Labels (must match frontend copy) ────────────────────────────────

_STAGE_LABELS: list[str] = [
    "Extracting semantic layers from job description...",
    "Parsing candidate resumes...",
    "Performing cross-signal skill gap matching...",
    "Generating recruiter insights...",
]

# Maps JobStatus → (active_stage_index, stage_status_for_active)
# active_stage_index = -1  means all pending (UPLOADED)
# active_stage_index =  4  means all done (COMPLETED)
_STATUS_STAGE_MAP: dict[JobStatus, tuple[int, StageStatus]] = {
    JobStatus.UPLOADED:    (-1, StageStatus.PENDING),
    JobStatus.PROCESSING:  (0,  StageStatus.LOADING),
    JobStatus.PARSING:     (1,  StageStatus.LOADING),
    JobStatus.EMBEDDING:   (2,  StageStatus.LOADING),
    JobStatus.SCORING:     (2,  StageStatus.LOADING),
    JobStatus.RANKING:     (3,  StageStatus.LOADING),
    JobStatus.COMPLETED:   (4,  StageStatus.DONE),
    JobStatus.FAILED:      (-2, StageStatus.ERROR),   # -2 = special case
}

_STATUS_PROGRESS_PCT: dict[JobStatus, int] = {
    JobStatus.UPLOADED:   0,
    JobStatus.PROCESSING: 10,
    JobStatus.PARSING:    30,
    JobStatus.EMBEDDING:  50,
    JobStatus.SCORING:    65,
    JobStatus.RANKING:    80,
    JobStatus.COMPLETED:  100,
    JobStatus.FAILED:     0,
}

_STATUS_ETA_SECONDS: dict[JobStatus, int] = {
    JobStatus.UPLOADED:   32,
    JobStatus.PROCESSING: 25,
    JobStatus.PARSING:    18,
    JobStatus.EMBEDDING:  12,
    JobStatus.SCORING:    8,
    JobStatus.RANKING:    4,
    JobStatus.COMPLETED:  0,
    JobStatus.FAILED:     0,
}


# ── Sub-models ─────────────────────────────────────────────────────────────


class ProgressStage(AppBaseModel):
    """A single stage entry in the progress_stages list (API contract shape)."""

    id: int = Field(ge=1, le=4)
    label: str
    status: StageStatus


# ── Internal Record ────────────────────────────────────────────────────────


class AnalysisJobRecord(IdentifiableMixin):
    """
    Full internal representation of an analysis job.

    Stored in the in-memory store.  The ``current_stage_index`` field
    is used by the FAILED handler to know which stage to mark as error.
    """

    status: JobStatus = JobStatus.UPLOADED
    job_description_file_id: UUID
    resume_file_ids: list[UUID] = Field(default_factory=list)
    job_description_id: UUID | None = None   # set after JD parsing (Module 4)
    current_stage_index: int = -1            # tracks last active stage for FAILED
    completed_at: datetime | None = None
    error_message: str | None = None


# ── Request / Response Shapes ──────────────────────────────────────────────


class AnalysisJobCreate(AppBaseModel):
    """Request body for POST /v1/analysis/jobs."""

    job_description_file_id: UUID
    resume_file_ids: list[UUID] = Field(
        min_length=1,
        max_length=10,
        description="Between 1 and 10 resume file IDs.",
    )


class AnalysisJobRead(AppBaseModel):
    """
    Public API response for an analysis job.

    Matches the ``AnalysisJob`` model in the API contract exactly.
    ``progress_stages`` and ``estimated_seconds_remaining`` are computed
    dynamically from the current ``status``.
    """

    id: UUID
    status: JobStatus
    progress_stages: list[ProgressStage]
    estimated_seconds_remaining: int | None
    job_description_id: UUID | None
    resume_file_ids: list[UUID]
    created_at: datetime
    completed_at: datetime | None

    @classmethod
    def from_record(cls, record: AnalysisJobRecord) -> "AnalysisJobRead":
        """Convert an internal job record to the public API shape."""
        return cls(
            id=record.id,
            status=record.status,
            progress_stages=_compute_stages(record.status, record.current_stage_index),
            estimated_seconds_remaining=_STATUS_ETA_SECONDS.get(record.status),
            job_description_id=record.job_description_id,
            resume_file_ids=record.resume_file_ids,
            created_at=record.created_at,
            completed_at=record.completed_at,
        )


# ── Stage Computation ──────────────────────────────────────────────────────


def _compute_stages(status: JobStatus, failed_at_index: int = -1) -> list[ProgressStage]:
    """
    Derive the four progress stage statuses from the current job status.

    Rules:
      - All stages before active_index → "done"
      - Active stage → "loading"
      - All stages after active_index → "pending"
      - COMPLETED → all "done"
      - FAILED → stage at failed_at_index → "error"; rest retain their state
    """
    active_index, _ = _STATUS_STAGE_MAP.get(status, (-1, StageStatus.PENDING))

    stages: list[ProgressStage] = []

    for i, label in enumerate(_STAGE_LABELS):
        stage_id = i + 1  # 1-indexed for the API

        if status == JobStatus.COMPLETED:
            stage_status = StageStatus.DONE
        elif status == JobStatus.FAILED:
            if i < failed_at_index:
                stage_status = StageStatus.DONE
            elif i == failed_at_index:
                stage_status = StageStatus.ERROR
            else:
                stage_status = StageStatus.PENDING
        elif active_index == -1:
            stage_status = StageStatus.PENDING
        elif i < active_index:
            stage_status = StageStatus.DONE
        elif i == active_index:
            stage_status = StageStatus.LOADING
        else:
            stage_status = StageStatus.PENDING

        stages.append(ProgressStage(id=stage_id, label=label, status=stage_status))

    return stages
