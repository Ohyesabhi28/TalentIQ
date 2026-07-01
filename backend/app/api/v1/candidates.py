"""
Candidates API — GET /v1/candidates/{candidate_id}

Provides access to parsed Resume Profiles and their semantic representations.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.dependencies import get_resume_profile_service, get_semantic_profile_service, get_explainability_service
from app.logging_config import get_logger
from app.models.base import BaseResponse
from app.models.resume import ResumeProfileRead
from app.models.semantic import SemanticProfileRead
from app.models.explainability import HiringRecommendationRead
from app.services.resume_profile import ResumeProfileService
from app.services.semantic_profile import SemanticProfileService
from app.services.explainability_service import ExplainabilityService

logger = get_logger(__name__)

router = APIRouter(prefix="/candidates", tags=["Candidates"])


# ── GET /candidates/{candidate_id} ─────────────────────────────────────────


@router.get(
    "/{candidate_id}",
    response_model=BaseResponse[ResumeProfileRead],
    status_code=status.HTTP_200_OK,
    summary="Get candidate profile",
)
async def get_candidate(
    candidate_id: UUID,
    service: ResumeProfileService = Depends(get_resume_profile_service),
) -> BaseResponse[ResumeProfileRead]:
    profile = await service.get_candidate_profile(candidate_id)
    return BaseResponse(data=profile)


# ── GET /candidates/{candidate_id}/semantic ────────────────────────────────


@router.get(
    "/{candidate_id}/semantic",
    response_model=BaseResponse[SemanticProfileRead],
    status_code=status.HTTP_200_OK,
    summary="Get semantic profile",
)
async def get_candidate_semantic(
    candidate_id: UUID,
    service: SemanticProfileService = Depends(get_semantic_profile_service),
) -> BaseResponse[SemanticProfileRead]:
    profile = await service.get_semantic_profile(candidate_id)
    return BaseResponse(data=profile)


# ── GET /candidates/{candidate_id}/insights ────────────────────────────────


@router.get(
    "/{candidate_id}/insights",
    response_model=BaseResponse[HiringRecommendationRead],
    status_code=status.HTTP_200_OK,
    summary="Get AI insights for a candidate",
)
async def get_candidate_insights(
    candidate_id: UUID,
    service: ExplainabilityService = Depends(get_explainability_service),
) -> BaseResponse[HiringRecommendationRead]:
    insight = await service.get_insight_for_candidate(candidate_id)
    return BaseResponse(data=insight)
