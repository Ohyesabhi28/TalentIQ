"""
Semantic Profile Service.

Orchestrates fetching parsed JDs and Resumes, concatenating their text,
generating embeddings using EmbeddingService, indexing them using VectorService,
and persisting the SemanticProfileRecords to the store.
"""

from __future__ import annotations

import json
from uuid import UUID

from app.exceptions import AppError
from app.logging_config import get_logger
from app.models.jd import JDProfileRecord
from app.models.resume import ResumeProfileRecord
from app.models.semantic import SemanticProfileRecord, SemanticProfileRead
from app.services.embedding import EmbeddingService
from app.services.vector import VectorService
from app.store.memory import InMemoryStore

logger = get_logger(__name__)


class SemanticProfileService:
    def __init__(
        self,
        store: InMemoryStore,
        embedding_service: EmbeddingService,
        vector_service: VectorService,
    ) -> None:
        self._store = store
        self._embedding_service = embedding_service
        self._vector_service = vector_service

    async def generate_embeddings_for_job(self, job_id: UUID) -> None:
        """
        Generate semantic embeddings for a job description and all its associated resumes.
        """
        logger.info("Generating embeddings for job_id=%s", job_id)
        
        job = await self._store.get_job(job_id)
        if not job:
            raise AppError(
                error_code="JOB_NOT_FOUND",
                message=f"Analysis job {job_id} not found.",
                status_code=404,
            )

        # 1. Process JD Profile
        if job.job_description_id:
            jd_profile = await self._store.get_jd_profile(job.job_description_id)
            if jd_profile:
                await self._process_jd_profile(jd_profile, job_id)

        # 2. Process Resume Profiles
        resume_profiles = await self._store.list_resume_profiles_by_job(job_id)
        for resume in resume_profiles:
            await self._process_resume_profile(resume, job_id)
            
        logger.info("Successfully generated and stored embeddings for job_id=%s", job_id)

    async def _process_jd_profile(self, profile: JDProfileRecord, job_id: UUID) -> None:
        """
        Convert a JDProfileRecord to text and embed it.
        """
        # Create a rich text representation combining key fields
        full_text = f"Title: {profile.job_title}\n"
        full_text += f"Industry: {profile.industry or ''}\n"
        full_text += f"Required Skills: {', '.join(profile.required_skills)}\n"
        full_text += f"Responsibilities: {', '.join(profile.responsibilities)}\n"
        
        # Generate embedding
        full_embedding = self._embedding_service.generate_embedding(full_text)
        
        # Generate skill embedding
        skill_text = ", ".join(profile.required_skills + profile.preferred_skills)
        skill_embedding = self._embedding_service.generate_embedding(skill_text) if skill_text else None
        
        # Create Semantic Profile
        semantic_record = SemanticProfileRecord(
            profile_type="job_description",
            source_id=profile.id,
            analysis_job_id=job_id,
            full_document_embedding=full_embedding.tolist(),
            skill_embeddings=skill_embedding.tolist() if skill_embedding is not None else None,
        )
        
        await self._store.save_semantic_profile(semantic_record)
        # Store in FAISS
        self._vector_service.add_vectors(
            full_embedding.reshape(1, -1), 
            source_ids=[str(profile.id)]
        )

    async def _process_resume_profile(self, profile: ResumeProfileRecord, job_id: UUID) -> None:
        """
        Convert a ResumeProfileRecord to text and embed it.
        """
        # Create a rich text representation combining key fields
        full_text = f"Role: {profile.professional_information.current_role or ''}\n"
        full_text += f"Skills: {', '.join(profile.skills.technical_skills)}\n"
        full_text += f"Experience: {profile.professional_information.total_years_experience or 0} years\n"
        
        for exp in profile.experience:
            full_text += f"{exp.job_title} at {exp.company}: {exp.description or ''}\n"
            
        # Generate embedding
        full_embedding = self._embedding_service.generate_embedding(full_text)
        
        # Generate skill embedding
        skill_text = ", ".join(
            profile.skills.technical_skills + 
            profile.skills.frameworks + 
            profile.skills.languages + 
            profile.skills.tools + 
            profile.skills.cloud_platforms + 
            profile.skills.databases
        )
        skill_embedding = self._embedding_service.generate_embedding(skill_text) if skill_text else None
        
        # Create Semantic Profile
        semantic_record = SemanticProfileRecord(
            profile_type="resume",
            source_id=profile.id,
            analysis_job_id=job_id,
            full_document_embedding=full_embedding.tolist(),
            skill_embeddings=skill_embedding.tolist() if skill_embedding is not None else None,
        )
        
        await self._store.save_semantic_profile(semantic_record)
        # Store in FAISS
        self._vector_service.add_vectors(
            full_embedding.reshape(1, -1), 
            source_ids=[str(profile.id)]
        )

    async def get_semantic_profile(self, source_id: UUID) -> SemanticProfileRead:
        """
        Retrieve a semantic profile by its source ID (JD or Resume ID).
        """
        profile = await self._store.get_semantic_profile_by_source(source_id)
        if not profile:
            raise AppError(
                error_code="SEMANTIC_PROFILE_NOT_FOUND",
                message=f"Semantic profile for source {source_id} not found.",
                status_code=404,
            )
        return SemanticProfileRead.model_validate(profile.model_dump())

    async def get_embedding_status(self, job_id: UUID) -> dict[str, int]:
        """
        Return the count of embedded profiles for a job.
        """
        profiles = await self._store.list_semantic_profiles_by_job(job_id)
        return {
            "total_embedded": len(profiles),
            "faiss_total_vectors": self._vector_service.total_vectors,
        }
