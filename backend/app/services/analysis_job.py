"""
AnalysisJobService — job lifecycle management and progress simulation.

Responsibilities:
  1. Validate that referenced file IDs exist in the store.
  2. Create an AnalysisJobRecord and persist it.
  3. Launch a background coroutine that advances the job status through
     the full pipeline (UPLOADED → … → COMPLETED) using time delays.
  4. Retrieve job status and convert to the public AnalysisJobRead shape.

No AI, no parsing, no embeddings in this module.
The simulation is replaced by real AI calls in Module 4.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from uuid import UUID

from app.exceptions import (
    AnalysisJobNotFoundError,
    CandidateNotFoundError,
)
from app.logging_config import get_logger
from app.models.analysis import (
    AnalysisJobCreate,
    AnalysisJobRead,
    AnalysisJobRecord,
    JobStatus,
)
from app.store.memory import InMemoryStore

logger = get_logger(__name__)

# ── Pipeline simulation timing ──────────────────────────────────────────────
# Each tuple is (target_status, delay_seconds_from_previous_stage)
_PIPELINE_STAGES: list[tuple[JobStatus, float]] = [
    (JobStatus.PROCESSING, 0.8),
    (JobStatus.PARSING,    2.0),
    (JobStatus.EMBEDDING,  2.0),
    (JobStatus.SCORING,    1.5),
    (JobStatus.RANKING,    1.5),
    (JobStatus.COMPLETED,  1.5),
]

# Maps JobStatus → the stage index that was "active" when it entered FAILED.
# Used by ProgressStage computation in the model layer.
_STATUS_STAGE_INDEX: dict[JobStatus, int] = {
    JobStatus.UPLOADED:    -1,
    JobStatus.PROCESSING:   0,
    JobStatus.PARSING:      1,
    JobStatus.EMBEDDING:    2,
    JobStatus.SCORING:      2,
    JobStatus.RANKING:      3,
    JobStatus.COMPLETED:    4,
    JobStatus.FAILED:       -1,  # overridden at the point of failure
}


class AnalysisJobService:
    """
    Orchestrates analysis job creation, status tracking, and retrieval.

    Constructed with an InMemoryStore injected via DI.
    """

    def __init__(self, store: InMemoryStore) -> None:
        self._store = store

    # ── Public API ──────────────────────────────────────────────────────────

    async def create_job(self, payload: AnalysisJobCreate) -> AnalysisJobRead:
        """
        Validate files and create a new analysis job.

        The job starts in UPLOADED status.  A background coroutine is
        immediately scheduled to advance it through the pipeline.

        Args:
            payload: Validated request body from POST /analysis/jobs.

        Returns:
            Public AnalysisJobRead with initial UPLOADED status.

        Raises:
            app.exceptions.FileNotFoundError: JD or resume file ID not found.
        """
        await self._validate_files(
            payload.job_description_file_id,
            payload.resume_file_ids,
        )

        record = AnalysisJobRecord(
            status=JobStatus.UPLOADED,
            job_description_file_id=payload.job_description_file_id,
            resume_file_ids=list(payload.resume_file_ids),
            current_stage_index=-1,
        )
        await self._store.save_job(record)

        logger.info(
            "Analysis job created: id=%s jd=%s resumes=%d",
            record.id,
            payload.job_description_file_id,
            len(payload.resume_file_ids),
        )

        # Fire-and-forget background simulation
        asyncio.create_task(
            self._simulate_pipeline(record.id),
            name=f"pipeline-{record.id}",
        )

        return AnalysisJobRead.from_record(record)

    async def get_job(self, job_id: UUID) -> AnalysisJobRead:
        """
        Retrieve the current state of an analysis job.

        Args:
            job_id: UUID from the URL path parameter.

        Returns:
            Public AnalysisJobRead with up-to-date status and progress stages.

        Raises:
            AnalysisJobNotFoundError: No job found with the given ID.
        """
        record = await self._store.get_job(job_id)
        if record is None:
            raise AnalysisJobNotFoundError()
        return AnalysisJobRead.from_record(record)

    # ── Private Helpers ─────────────────────────────────────────────────────

    async def _validate_files(
        self,
        jd_file_id: UUID,
        resume_file_ids: list[UUID],
    ) -> None:
        """
        Ensure all referenced file IDs exist in the store.

        Raises:
            app.exceptions.FileNotFoundError: Any file ID is unknown.
        """
        from app.exceptions import FileNotFoundError as AppFileNotFoundError

        jd_record = await self._store.get_file(jd_file_id)
        if jd_record is None:
            raise AppFileNotFoundError(
                f"Job description file '{jd_file_id}' not found."
            )

        for rid in resume_file_ids:
            resume = await self._store.get_file(rid)
            if resume is None:
                raise AppFileNotFoundError(f"Resume file '{rid}' not found.")

    async def _simulate_pipeline(self, job_id: UUID) -> None:
        """
        Background coroutine that advances the job through every pipeline stage.

        Each stage waits for a configured delay, then updates the job record.
        If any step raises an unexpected error, the job is marked FAILED.
        """
        logger.debug("Pipeline simulation started for job %s", job_id)
        last_stage_index = -1

        try:
            for target_status, delay in _PIPELINE_STAGES:
                await asyncio.sleep(delay)

                record = await self._store.get_job(job_id)
                if record is None:
                    logger.warning(
                        "Job %s disappeared during simulation; aborting.", job_id
                    )
                    return

                stage_index = _STATUS_STAGE_INDEX.get(target_status, last_stage_index)
                last_stage_index = stage_index

                updated = record.model_copy(
                    update={
                        "status": target_status,
                        "current_stage_index": stage_index,
                        "completed_at": (
                            datetime.now(tz=timezone.utc)
                            if target_status == JobStatus.COMPLETED
                            else None
                        ),
                    }
                )
                await self._store.update_job(updated)
                logger.info(
                    "Job %s → %s (stage %d)", job_id, target_status, stage_index
                )

        except Exception as exc:  # pragma: no cover
            logger.exception("Pipeline simulation failed for job %s: %s", job_id, exc)
            record = await self._store.get_job(job_id)
            if record is not None:
                failed = record.model_copy(
                    update={
                        "status": JobStatus.FAILED,
                        "current_stage_index": last_stage_index,
                        "error_message": str(exc),
                        "completed_at": datetime.now(tz=timezone.utc),
                    }
                )
                await self._store.update_job(failed)
