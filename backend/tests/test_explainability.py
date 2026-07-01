"""
Tests for ExplainabilityService (Module 7).
"""

from __future__ import annotations

import json
import uuid
import pytest
from unittest.mock import Mock, AsyncMock

from app.models.explainability import CandidateInsight
from app.models.scoring import CandidateScore, ScoreBreakdown, SkillMatchDetail, ProjectMatchDetail, ExperienceMatchDetail, EducationMatchDetail, CertificationMatchDetail
from app.models.resume import ResumeProfileRecord, PersonalInformation, ProfessionalInformation, SkillGroup
from app.services.explainability_service import ExplainabilityService
from app.store.memory import InMemoryStore
from app.config import Settings

@pytest.fixture
def store():
    return InMemoryStore()

@pytest.fixture
def settings():
    return Settings(GEMINI_API_KEY="mock_key")

@pytest.mark.asyncio
async def test_explainability_generation(store, settings, monkeypatch):
    service = ExplainabilityService(store, settings)
    
    # Mock Gemini response
    class MockResponse:
        def __init__(self):
            self.text = json.dumps({
                "overall_summary": "Good candidate overall.",
                "top_strengths": ["Python"],
                "top_weaknesses": ["Docker"],
                "matched_skills": ["Python"],
                "missing_skills": ["Docker"],
                "relevant_projects": ["Built Python API"],
                "experience_highlights": ["3 years as Dev"],
                "education_summary": "BS CS",
                "certification_summary": "None",
                "interview_focus_areas": ["Interview Docker"],
                "hiring_recommendation": "Strong Fit"
            })
            
    mock_model = Mock()
    mock_model.generate_content_async = AsyncMock(return_value=MockResponse())
    service.model = mock_model
    
    cand_id = uuid.uuid4()
    job_id = uuid.uuid4()
    
    cand = CandidateScore(
        candidate_id=cand_id,
        candidate_name="Alice",
        overall_score=85.0,
        rank="Strong Fit",
        breakdown=ScoreBreakdown(
            skill_match=SkillMatchDetail(skill_score=90.0, matched_skills=["Python"], missing_skills=["Docker"]),
            semantic_similarity=80.0,
            experience_match=ExperienceMatchDetail(experience_score=100.0),
            project_relevance=ProjectMatchDetail(project_score=80.0),
            education_match=EducationMatchDetail(education_score=100.0),
            certification_match=CertificationMatchDetail(certification_score=100.0)
        )
    )
    
    resume = ResumeProfileRecord(
        id=cand_id,
        analysis_job_id=job_id,
        original_file_id=uuid.uuid4(),
        raw_text="Alice Resume",
        personal_information=PersonalInformation(name="Alice", email="alice@test.com"),
        professional_information=ProfessionalInformation(total_years_experience=3.0, current_role="Dev"),
        skills=SkillGroup(languages=["Python"]),
        experience=[],
        projects=[],
        education=[],
        certifications=[]
    )
    
    # Mock store methods
    store.get_ranking = AsyncMock(return_value=Mock(candidates=[cand]))
    store.get_resume_profile = AsyncMock(return_value=resume)
    store.save_recommendation = AsyncMock()
    
    recs = await service.generate_insights_for_job(job_id)
    assert len(recs) == 1
    
    rec = recs[0]
    assert rec.candidate_id == cand_id
    assert rec.recommendation == "Strong Fit"
    assert rec.insight.overall_summary == "Good candidate overall."
    assert rec.insight.matched_skills == ["Python"]
