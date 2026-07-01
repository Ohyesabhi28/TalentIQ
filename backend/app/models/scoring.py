"""
Scoring and Ranking models.

Defines the output structure for deterministic Candidate evaluation.
"""

from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from pydantic import Field

from app.models.base import AppBaseModel, IdentifiableMixin


class SkillMatchDetail(AppBaseModel):
    matched_skills: List[str] = Field(default_factory=list, description="Skills that were semantically matched")
    missing_skills: List[str] = Field(default_factory=list, description="Skills required but not found")
    skill_score: float = Field(description="Score out of 100 for skills")


class ProjectMatchDetail(AppBaseModel):
    top_matching_projects: List[str] = Field(default_factory=list, description="Projects matching JD responsibilities")
    project_score: float = Field(description="Score out of 100 for projects")


class ExperienceMatchDetail(AppBaseModel):
    required_years: float = Field(default=0.0, description="Years required by JD")
    candidate_years: float = Field(default=0.0, description="Years candidate has")
    experience_score: float = Field(description="Score out of 100 for experience")


class EducationMatchDetail(AppBaseModel):
    required_degree: Optional[str] = Field(default=None)
    candidate_degree: Optional[str] = Field(default=None)
    education_score: float = Field(description="Score out of 100 for education")


class CertificationMatchDetail(AppBaseModel):
    matched_certifications: List[str] = Field(default_factory=list)
    missing_certifications: List[str] = Field(default_factory=list)
    certification_score: float = Field(description="Score out of 100 for certifications")


class ScoreBreakdown(AppBaseModel):
    skill_match: SkillMatchDetail
    semantic_similarity: float = Field(description="Overall FAISS similarity score out of 100")
    experience_match: ExperienceMatchDetail
    project_relevance: ProjectMatchDetail
    education_match: EducationMatchDetail
    certification_match: CertificationMatchDetail


class CandidateScore(AppBaseModel):
    candidate_id: UUID = Field(description="ID of the ResumeProfile")
    candidate_name: str = Field(description="Name of the candidate")
    overall_score: float = Field(description="Weighted overall score out of 100")
    breakdown: ScoreBreakdown
    rank: str = Field(description="Strong Fit, Good Fit, Average Fit, or Poor Fit")


class RankingResultRecord(IdentifiableMixin):
    analysis_job_id: UUID = Field(description="ID of the AnalysisJob")
    candidates: List[CandidateScore] = Field(description="Ranked list of candidates, descending by overall_score")


class RankingResultRead(RankingResultRecord):
    pass
