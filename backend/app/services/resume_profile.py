"""
Resume Profile Service.

Orchestrates the extraction of raw text from uploaded Resume PDFs,
parsing them using Gemini, and saving the structured ResumeProfile records to the store.
"""

from __future__ import annotations

import asyncio
from uuid import UUID

from app.exceptions import AppError
from app.logging_config import get_logger
from app.models.resume import ResumeProfileRead, ResumeProfileRecord
from app.services.gemini_resume_parser import GeminiResumeParser
from app.services.pdf_extractor import PDFExtractorService
from app.store.memory import InMemoryStore

logger = get_logger(__name__)


class ResumeProfileService:
    """
    Service to handle full Resume parsing workflow.
    """

    def __init__(
        self,
        store: InMemoryStore,
        extractor: PDFExtractorService,
        parser: GeminiResumeParser,
    ) -> None:
        self._store = store
        self._extractor = extractor
        self._parser = parser

    async def parse_resumes_for_job(self, job_id: UUID) -> list[ResumeProfileRead]:
        """
        Extract and parse all Resumes associated with a given analysis job.

        Args:
            job_id: ID of the AnalysisJobRecord.

        Returns:
            A list of structured ResumeProfileRead outputs.

        Raises:
            AppError: If the job or file is not found, or parsing fails.
        """
        logger.info("Starting Resume parsing workflow for job_id=%s", job_id)
        
        job = await self._store.get_job(job_id)
        if not job:
            raise AppError(
                error_code="JOB_NOT_FOUND",
                message=f"Analysis job {job_id} not found.",
                status_code=404,
            )

        if not job.resume_file_ids:
            logger.warning("No resumes attached to job_id=%s", job_id)
            return []

        profiles = []
        for file_id in job.resume_file_ids:
            try:
                profile = await self.parse_single_resume(job_id, file_id)
                profiles.append(profile)
            except Exception as exc:
                logger.error("Failed to parse resume file_id=%s: %s", file_id, exc)
                # We log the error but allow other resumes to continue parsing
        
        logger.info("Successfully parsed %d resumes for job_id=%s", len(profiles), job_id)
        return profiles

    async def parse_single_resume(self, job_id: UUID, file_id: UUID) -> ResumeProfileRead:
        """
        Extract and parse a single Resume file.
        """
        file_record = await self._store.get_file(file_id)
        if not file_record or not file_record.local_path:
            raise AppError(
                error_code="FILE_NOT_FOUND",
                message=f"Resume file {file_id} not found or has no path.",
                status_code=404,
            )

        # 1. Extract raw text from PDF
        raw_text = self._extractor.extract_text(file_record.local_path)
        logger.debug("Successfully extracted %d characters from Resume file.", len(raw_text))

        # 2. Parse text with Gemini
        parsed_base = await self._parser.parse_resume(raw_text)

        # 3. Create full profile record and associate with job
        profile_record = ResumeProfileRecord(
            **parsed_base.model_dump(),
            analysis_job_id=job_id,
            original_file_id=file_id,
            raw_text=raw_text,
        )
        await self._store.save_resume_profile(profile_record)

        return ResumeProfileRead.model_validate(profile_record.model_dump())

    async def get_resumes_for_job(self, job_id: UUID) -> list[ResumeProfileRead]:
        """
        Retrieve all parsed Resume profiles for a given job ID.
        """
        profiles = await self._store.list_resume_profiles_by_job(job_id)
        return [ResumeProfileRead.model_validate(p.model_dump()) for p in profiles]
        
    async def get_candidate_profile(self, candidate_id: UUID) -> ResumeProfileRead:
        """
        Retrieve a single candidate's resume profile by ID.
        
        Raises:
            AppError if not found.
        """
        profile = await self._store.get_resume_profile(candidate_id)
        if not profile:
            raise AppError(
                error_code="CANDIDATE_NOT_FOUND",
                message=f"Candidate Profile {candidate_id} not found.",
                status_code=404,
            )
        return ResumeProfileRead.model_validate(profile.model_dump())
