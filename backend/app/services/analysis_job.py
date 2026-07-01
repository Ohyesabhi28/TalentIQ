"""
AnalysisJobService — job lifecycle management and progress simulation.

Responsibilities:
  1. Validate that referenced file IDs exist in the store.
  2. Create an AnalysisJobRecord and persist it.
  3. Launch a background coroutine that runs the actual processing services
     sequentially through the pipeline (UPLOADED → … → COMPLETED).
  4. Retrieve job status and convert to the public AnalysisJobRead shape.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from uuid import UUID

from app.exceptions import (
    AnalysisJobNotFoundError,
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

# ProgressStage indexes
_STATUS_STAGE_INDEX: dict[JobStatus, int] = {
    JobStatus.UPLOADED:    -1,
    JobStatus.PROCESSING:   0,
    JobStatus.PARSING:      1,
    JobStatus.EMBEDDING:    2,
    JobStatus.SCORING:      2,
    JobStatus.RANKING:      3,
    JobStatus.COMPLETED:    4,
    JobStatus.FAILED:       -1,
}


class AnalysisJobService:
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store

    async def create_job(self, payload: AnalysisJobCreate) -> AnalysisJobRead:
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

        # Fire-and-forget background execution of the actual pipeline
        asyncio.create_task(
            self._run_pipeline(record.id),
            name=f"pipeline-{record.id}",
        )

        return AnalysisJobRead.from_record(record)

    async def get_job(self, job_id: UUID) -> AnalysisJobRead:
        record = await self._store.get_job(job_id)
        if record is None:
            raise AnalysisJobNotFoundError()
        return AnalysisJobRead.from_record(record)

    async def _validate_files(
        self,
        jd_file_id: UUID,
        resume_file_ids: list[UUID],
    ) -> None:
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

    async def _update_job_status(self, job_id: UUID, status: JobStatus) -> None:
        record = await self._store.get_job(job_id)
        if record is None:
            return
            
        stage_index = _STATUS_STAGE_INDEX.get(status, record.current_stage_index)
        updated = record.model_copy(
            update={
                "status": status,
                "current_stage_index": stage_index,
                "completed_at": (
                    datetime.now(tz=timezone.utc)
                    if status == JobStatus.COMPLETED
                    else None
                ),
            }
        )
        await self._store.update_job(updated)
        logger.info("Job %s → %s (stage %d)", job_id, status, stage_index)

    async def _run_pipeline(self, job_id: UUID) -> None:
        logger.info("Starting background pipeline execution for job %s", job_id)
        
        # Instantiate actual services using dependency injection functions
        from app.config import get_settings
        from app.dependencies import (
            get_pdf_extractor,
            get_gemini_parser,
            get_jd_profile_service,
            get_gemini_resume_parser,
            get_resume_profile_service,
            get_embedding_service,
            get_vector_service,
            get_semantic_profile_service,
            get_scoring_service,
            get_ranking_service,
            get_explainability_service,
        )
        
        settings = get_settings()
        extractor = get_pdf_extractor()
        
        jd_parser = get_gemini_parser(settings)
        jd_service = get_jd_profile_service(self._store, extractor, jd_parser)
        
        resume_parser = get_gemini_resume_parser(settings)
        resume_service = get_resume_profile_service(self._store, extractor, resume_parser)
        
        embedding_service = get_embedding_service()
        vector_service = get_vector_service()
        semantic_service = get_semantic_profile_service(self._store, embedding_service, vector_service)
        
        scoring_service = get_scoring_service(embedding_service, vector_service)
        ranking_service = get_ranking_service(self._store, scoring_service)
        
        explainability_service = get_explainability_service(self._store, settings)
        
        try:
            # ── 1. JD Sourcing / Parsing ──
            await self._update_job_status(job_id, JobStatus.PROCESSING)
            await jd_service.parse_jd(job_id)
            
            # ── 2. Resume Parsing ──
            await self._update_job_status(job_id, JobStatus.PARSING)
            await resume_service.parse_resumes_for_job(job_id)
            
            # ── 3. Embeddings Generation ──
            await self._update_job_status(job_id, JobStatus.EMBEDDING)
            await semantic_service.generate_embeddings_for_job(job_id)
            
            # ── 4. Scoring ──
            await self._update_job_status(job_id, JobStatus.SCORING)
            # Scoring is performed during the ranking process
            
            # ── 5. Ranking ──
            await self._update_job_status(job_id, JobStatus.RANKING)
            await ranking_service.rank_candidates_for_job(job_id)
            
            # ── 6. Recruiter Insights (Explainability) ──
            # Run explainability service to automatically populate CandidateInsight models
            await explainability_service.generate_insights_for_job(job_id)
            
            # ── 7. Completed ──
            await self._update_job_status(job_id, JobStatus.COMPLETED)
            
        except Exception as exc:
            logger.exception("Pipeline execution failed for job %s: %s", job_id, exc)
            record = await self._store.get_job(job_id)
            if record is not None:
                failed = record.model_copy(
                    update={
                        "status": JobStatus.FAILED,
                        "error_message": str(exc),
                        "completed_at": datetime.now(tz=timezone.utc),
                    }
                )
                await self._store.update_job(failed)
