"""
Analysis Jobs API — POST /v1/analysis/jobs, GET /v1/analysis/jobs/{job_id}
POST /v1/analysis/jobs/{job_id}/parse-jd, GET /v1/analysis/jobs/{job_id}/jd
POST /v1/analysis/jobs/{job_id}/parse-resumes, GET /v1/analysis/jobs/{job_id}/resumes
POST /v1/analysis/jobs/{job_id}/generate-embeddings, GET /v1/analysis/jobs/{job_id}/embedding-status
POST /v1/analysis/jobs/{job_id}/rank, GET /v1/analysis/jobs/{job_id}/ranking
POST /v1/analysis/jobs/{job_id}/generate-insights, GET /v1/analysis/jobs/{job_id}/insights
"""

from __future__ import annotations

from typing import List, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.dependencies import (
    get_analysis_job_service,
    get_jd_profile_service,
    get_resume_profile_service,
    get_semantic_profile_service,
    get_ranking_service,
    get_explainability_service,
)
from app.logging_config import get_logger
from app.models.analysis import AnalysisJobCreate, AnalysisJobRead
from app.models.base import BaseResponse
from app.models.jd import JDProfileRead
from app.models.resume import ResumeProfileRead
from app.models.scoring import RankingResultRead
from app.models.explainability import HiringRecommendationRead
from app.services.analysis_job import AnalysisJobService
from app.services.jd_profile import JDProfileService
from app.services.resume_profile import ResumeProfileService
from app.services.semantic_profile import SemanticProfileService
from app.services.ranking_service import RankingService
from app.services.explainability_service import ExplainabilityService

logger = get_logger(__name__)

router = APIRouter(prefix="/analysis", tags=["Analysis Jobs"])


# ── POST /analysis/jobs ────────────────────────────────────────────────────


@router.post(
    "/jobs",
    response_model=BaseResponse[AnalysisJobRead],
    status_code=status.HTTP_202_ACCEPTED,
    summary="Create an analysis job",
)
async def create_analysis_job(
    payload: AnalysisJobCreate,
    service: AnalysisJobService = Depends(get_analysis_job_service),
) -> BaseResponse[AnalysisJobRead]:
    job = await service.create_job(payload)
    logger.info("Analysis job accepted: id=%s", job.id)
    return BaseResponse(data=job)


# ── GET /analysis/jobs/{job_id} ────────────────────────────────────────────


@router.get(
    "/jobs/{job_id}",
    response_model=BaseResponse[AnalysisJobRead],
    status_code=status.HTTP_200_OK,
    summary="Get analysis job status",
)
async def get_analysis_job(
    job_id: UUID,
    service: AnalysisJobService = Depends(get_analysis_job_service),
) -> BaseResponse[AnalysisJobRead]:
    job = await service.get_job(job_id)
    return BaseResponse(data=job)


# ── POST /analysis/jobs/{job_id}/parse-jd ──────────────────────────────────


@router.post(
    "/jobs/{job_id}/parse-jd",
    response_model=BaseResponse[JDProfileRead],
    status_code=status.HTTP_200_OK,
    summary="Parse Job Description with AI",
)
async def parse_jd(
    job_id: UUID,
    service: JDProfileService = Depends(get_jd_profile_service),
) -> BaseResponse[JDProfileRead]:
    profile = await service.parse_jd(job_id)
    return BaseResponse(data=profile)


# ── GET /analysis/jobs/{job_id}/jd ─────────────────────────────────────────


@router.get(
    "/jobs/{job_id}/jd",
    response_model=BaseResponse[JDProfileRead],
    status_code=status.HTTP_200_OK,
    summary="Get parsed Job Description",
)
async def get_parsed_jd(
    job_id: UUID,
    job_service: AnalysisJobService = Depends(get_analysis_job_service),
    jd_service: JDProfileService = Depends(get_jd_profile_service),
) -> BaseResponse[JDProfileRead]:
    from app.exceptions import AppError
    
    job = await job_service.get_job(job_id)
    if not job.job_description_id:
        raise AppError(
            error_code="JD_PROFILE_NOT_FOUND",
            message=f"No parsed JD profile found for job {job_id}.",
            status_code=404,
        )

    profile = await jd_service.get_jd_profile(job.job_description_id)
    return BaseResponse(data=profile)


# ── POST /analysis/jobs/{job_id}/parse-resumes ─────────────────────────────


@router.post(
    "/jobs/{job_id}/parse-resumes",
    response_model=BaseResponse[List[ResumeProfileRead]],
    status_code=status.HTTP_200_OK,
    summary="Parse Resumes with AI",
)
async def parse_resumes(
    job_id: UUID,
    service: ResumeProfileService = Depends(get_resume_profile_service),
) -> BaseResponse[List[ResumeProfileRead]]:
    profiles = await service.parse_resumes_for_job(job_id)
    return BaseResponse(data=profiles)


# ── GET /analysis/jobs/{job_id}/resumes ────────────────────────────────────


@router.get(
    "/jobs/{job_id}/resumes",
    response_model=BaseResponse[List[ResumeProfileRead]],
    status_code=status.HTTP_200_OK,
    summary="Get parsed Resumes",
)
async def get_parsed_resumes(
    job_id: UUID,
    service: ResumeProfileService = Depends(get_resume_profile_service),
) -> BaseResponse[List[ResumeProfileRead]]:
    profiles = await service.get_resumes_for_job(job_id)
    return BaseResponse(data=profiles)


# ── POST /analysis/jobs/{job_id}/generate-embeddings ───────────────────────


@router.post(
    "/jobs/{job_id}/generate-embeddings",
    response_model=BaseResponse[Dict[str, str]],
    status_code=status.HTTP_200_OK,
    summary="Generate semantic embeddings",
)
async def generate_embeddings(
    job_id: UUID,
    service: SemanticProfileService = Depends(get_semantic_profile_service),
) -> BaseResponse[Dict[str, str]]:
    await service.generate_embeddings_for_job(job_id)
    return BaseResponse(data={"status": "completed", "job_id": str(job_id)})


# ── GET /analysis/jobs/{job_id}/embedding-status ───────────────────────────


@router.get(
    "/jobs/{job_id}/embedding-status",
    response_model=BaseResponse[Dict[str, int]],
    status_code=status.HTTP_200_OK,
    summary="Get embedding generation status",
)
async def get_embedding_status(
    job_id: UUID,
    service: SemanticProfileService = Depends(get_semantic_profile_service),
) -> BaseResponse[Dict[str, int]]:
    stats = await service.get_embedding_status(job_id)
    return BaseResponse(data=stats)


# ── POST /analysis/jobs/{job_id}/rank ──────────────────────────────────────


@router.post(
    "/jobs/{job_id}/rank",
    response_model=BaseResponse[RankingResultRead],
    status_code=status.HTTP_200_OK,
    summary="Score and rank all candidates for a job",
)
async def rank_candidates(
    job_id: UUID,
    service: RankingService = Depends(get_ranking_service),
) -> BaseResponse[RankingResultRead]:
    ranking = await service.rank_candidates_for_job(job_id)
    return BaseResponse(data=ranking)


# ── GET /analysis/jobs/{job_id}/ranking ────────────────────────────────────


@router.get(
    "/jobs/{job_id}/ranking",
    response_model=BaseResponse[RankingResultRead],
    status_code=status.HTTP_200_OK,
    summary="Get candidate ranking results",
)
async def get_ranking(
    job_id: UUID,
    service: RankingService = Depends(get_ranking_service),
) -> BaseResponse[RankingResultRead]:
    ranking = await service.get_ranking(job_id)
    return BaseResponse(data=ranking)


# ── POST /analysis/jobs/{job_id}/generate-insights ─────────────────────────


@router.post(
    "/jobs/{job_id}/generate-insights",
    response_model=BaseResponse[List[HiringRecommendationRead]],
    status_code=status.HTTP_200_OK,
    summary="Generate AI insights for all ranked candidates",
)
async def generate_insights(
    job_id: UUID,
    service: ExplainabilityService = Depends(get_explainability_service),
) -> BaseResponse[List[HiringRecommendationRead]]:
    insights = await service.generate_insights_for_job(job_id)
    return BaseResponse(data=insights)


# ── GET /analysis/jobs/{job_id}/insights ───────────────────────────────────


@router.get(
    "/jobs/{job_id}/insights",
    response_model=BaseResponse[List[HiringRecommendationRead]],
    status_code=status.HTTP_200_OK,
    summary="Get AI insights for all candidates",
)
async def get_insights(
    job_id: UUID,
    service: ExplainabilityService = Depends(get_explainability_service),
) -> BaseResponse[List[HiringRecommendationRead]]:
    insights = await service.get_insights_for_job(job_id)
    return BaseResponse(data=insights)
