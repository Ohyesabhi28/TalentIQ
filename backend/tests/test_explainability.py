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
                "why_ranked_here": "Good candidate overall.",
                "top_strengths": ["Python"],
                "top_weaknesses": ["Docker"],
                "matched_skills": ["Python"],
                "missing_skills": ["Docker"],
                "interview_focus_areas": ["System Design"],
                "suggested_next_step": "Interview"
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
    
    # Store ranking so service can find it
    store.get_ranking = AsyncMock(return_value=Mock(candidates=[cand]))
    
    recs = await service.generate_insights_for_job(job_id)
    assert len(recs) == 1
    
    rec = recs[0]
    assert rec.candidate_id == cand_id
    assert rec.recommendation == "Strong Fit"
    assert rec.insight.why_ranked_here == "Good candidate overall."
    assert rec.insight.matched_skills == ["Python"]
