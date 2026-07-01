"""
JD Profile Service.

Orchestrates the extraction of raw text from an uploaded Job Description PDF,
parsing it using Gemini, and saving the structured JDProfile record to the store.
"""

from __future__ import annotations

from uuid import UUID

from app.exceptions import AppError
from app.logging_config import get_logger
from app.models.jd import JDProfileRead, JDProfileRecord
from app.services.gemini_parser import GeminiJDParser
from app.services.pdf_extractor import PDFExtractorService
from app.store.memory import InMemoryStore

logger = get_logger(__name__)


class JDProfileService:
    """
    Service to handle full JD parsing workflow.
    """

    def __init__(
        self,
        store: InMemoryStore,
        extractor: PDFExtractorService,
        parser: GeminiJDParser,
    ) -> None:
        self._store = store
        self._extractor = extractor
        self._parser = parser

    async def parse_jd(self, job_id: UUID) -> JDProfileRead:
        """
        Extract and parse a Job Description for the given analysis job.

        Args:
            job_id: ID of the AnalysisJobRecord.

        Returns:
            The structured JDProfileRead output.

        Raises:
            AppError: If the job or file is not found, or parsing fails.
        """
        logger.info("Starting JD parsing workflow for job_id=%s", job_id)
        
        job = await self._store.get_job(job_id)
        if not job:
            raise AppError(
                error_code="JOB_NOT_FOUND",
                message=f"Analysis job {job_id} not found.",
                status_code=404,
            )

        file_record = await self._store.get_file(job.job_description_file_id)
        if not file_record or not file_record.local_path:
            raise AppError(
                error_code="FILE_NOT_FOUND",
                message=f"Job description file {job.job_description_file_id} not found or has no path.",
                status_code=404,
            )

        # 1. Extract raw text from PDF
        raw_text = self._extractor.extract_text(file_record.local_path)
        logger.debug("Successfully extracted %d characters from JD file.", len(raw_text))

        # 2. Parse text with Gemini
        parsed_base = await self._parser.parse_jd(raw_text)

        # 3. Create full profile record and associate with job
        profile_record = JDProfileRecord(
            **parsed_base.model_dump(),
            raw_text=raw_text,
        )
        await self._store.save_jd_profile(profile_record)

        # Update the analysis job with the jd profile id
        updated_job = job.model_copy(update={"job_description_id": profile_record.id})
        await self._store.update_job(updated_job)

        logger.info("Successfully parsed and saved JDProfile id=%s", profile_record.id)
        return JDProfileRead.model_validate(profile_record.model_dump())

    async def get_jd_profile(self, profile_id: UUID) -> JDProfileRead:
        """
        Retrieve a JD profile by its ID.

        Raises:
            AppError if not found.
        """
        profile = await self._store.get_jd_profile(profile_id)
        if not profile:
            raise AppError(
                error_code="JD_PROFILE_NOT_FOUND",
                message=f"JD Profile {profile_id} not found.",
                status_code=404,
            )
        return JDProfileRead.model_validate(profile.model_dump())
