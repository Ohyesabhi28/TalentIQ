"""
Executive Sourcing Analytics models.

Defines the structure for deterministic aggregator metrics and executive hiring reports.
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional
from uuid import UUID

from pydantic import Field

from app.models.base import AppBaseModel


class AnalyticsSummary(AppBaseModel):
    """
    Detailed statistics generated from candidate evaluations.
    """
    candidates_reviewed: int = Field(description="Total number of candidates reviewed")
    avg_match_score: float = Field(description="Average overall match score")
    highest_match_score: float = Field(description="Highest match score found")
    lowest_match_score: float = Field(description="Lowest match score found")
    avg_experience_years: float = Field(description="Average years of experience")
    avg_skill_match_score: float = Field(description="Average skill match score")
    recommendation_distribution: Dict[str, int] = Field(description="Counts per recommendation band")


class SkillGapDetail(AppBaseModel):
    """
    Match and gap count details for a specific skill.
    """
    skill_name: str
    match_count: int
    gap_count: int


class SkillGapSummary(AppBaseModel):
    """
    Aggregate skill gap and technology frequency metrics.
    """
    top_missing_skills: List[SkillGapDetail] = Field(default_factory=list)
    top_matching_skills: List[SkillGapDetail] = Field(default_factory=list)
    most_common_certifications: List[str] = Field(default_factory=list)
    most_common_technologies: List[str] = Field(default_factory=list)
    most_requested_skills: List[str] = Field(default_factory=list)
    most_missing_certifications: List[str] = Field(default_factory=list)


class RecommendationCandidateDetail(AppBaseModel):
    """
    Lightweight candidate details for recommendations.
    """
    candidate_id: UUID
    candidate_name: str
    overall_score: float
    recommendation: str


class RecommendationSummary(AppBaseModel):
    """
    Deterministic actionable sourcing categories.
    """
    top_candidate: Optional[RecommendationCandidateDetail] = None
    top_3_candidates: List[RecommendationCandidateDetail] = Field(default_factory=list)
    additional_interview_focus: List[RecommendationCandidateDetail] = Field(default_factory=list)
    suitable_for_future_roles: List[RecommendationCandidateDetail] = Field(default_factory=list)


class ExecutiveSummary(AppBaseModel):
    """
    High-level overview summary for hiring leaders.
    """
    job_title: str
    total_candidates: int
    executive_text_summary: str
    key_highlights: List[str] = Field(default_factory=list)
    recommendation_action: str


class JobAnalyticsResponse(AppBaseModel):
    """
    Response schema for job analytics.
    """
    analytics: AnalyticsSummary
    skill_gap: SkillGapSummary


class JobExecutiveSummaryResponse(AppBaseModel):
    """
    Response schema for job executive summary.
    """
    executive_summary: ExecutiveSummary
    recommendations: RecommendationSummary

