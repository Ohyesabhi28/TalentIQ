"""
Ranking Service.

Orchestrates fetching all profiles for a Job, generating scores for each via 
ScoringService, ranking them, and persisting the RankingResult.
"""

from __future__ import annotations

from uuid import UUID

from app.exceptions import AppError
from app.logging_config import get_logger
from app.models.scoring import RankingResultRecord, RankingResultRead
from app.services.scoring_service import ScoringService
from app.store.memory import InMemoryStore

logger = get_logger(__name__)


class RankingService:
    def __init__(self, store: InMemoryStore, scoring_service: ScoringService):
        self._store = store
        self._scoring_service = scoring_service

    async def rank_candidates_for_job(self, job_id: UUID) -> RankingResultRead:
        logger.info("Starting candidate ranking for job_id=%s", job_id)
        
        job = await self._store.get_job(job_id)
        if not job:
            raise AppError("JOB_NOT_FOUND", f"Analysis job {job_id} not found.", 404)
            
        if not job.job_description_id:
            raise AppError("JD_NOT_FOUND", "No JD profile attached to this job.", 400)
            
        jd = await self._store.get_jd_profile(job.job_description_id)
        jd_sem = await self._store.get_semantic_profile_by_source(jd.id)
        
        if not jd or not jd_sem:
            raise AppError("JD_DATA_MISSING", "JD structural or semantic profile is missing.", 400)

        resumes = await self._store.list_resume_profiles_by_job(job_id)
        if not resumes:
            logger.warning("No resumes found for job_id=%s", job_id)
            empty_record = RankingResultRecord(analysis_job_id=job_id, candidates=[])
            await self._store.save_ranking(empty_record)
            return RankingResultRead.model_validate(empty_record.model_dump())

        scored_candidates = []
        for res in resumes:
            res_sem = await self._store.get_semantic_profile_by_source(res.id)
            if not res_sem:
                logger.warning("Skipping resume %s: Semantic profile missing.", res.id)
                continue
                
            score = self._scoring_service.score_candidate(jd, jd_sem, res, res_sem)
            scored_candidates.append(score)
            
        # Sort descending by overall_score
        scored_candidates.sort(key=lambda x: x.overall_score, reverse=True)
        
        # Assign rank bands
        for cand in scored_candidates:
            if cand.overall_score >= 85:
                cand.rank = "Strong Fit"
            elif cand.overall_score >= 70:
                cand.rank = "Good Fit"
            elif cand.overall_score >= 50:
                cand.rank = "Average Fit"
            else:
                cand.rank = "Poor Fit"

        # Persist ranking result
        ranking_record = RankingResultRecord(
            analysis_job_id=job_id,
            candidates=scored_candidates
        )
        
        await self._store.save_ranking(ranking_record)
        logger.info("Successfully ranked %d candidates for job_id=%s", len(scored_candidates), job_id)
        
        return RankingResultRead.model_validate(ranking_record.model_dump())

    async def get_ranking(self, job_id: UUID) -> RankingResultRead:
        ranking = await self._store.get_ranking(job_id)
        if not ranking:
            raise AppError("RANKING_NOT_FOUND", f"No ranking found for job {job_id}", 404)
            
        return RankingResultRead.model_validate(ranking.model_dump())
