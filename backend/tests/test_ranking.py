"""
Tests for RankingService (Module 6).
"""

from __future__ import annotations

import uuid
import pytest
from unittest.mock import Mock, AsyncMock

from app.models.scoring import (
    CandidateScore, ScoreBreakdown, SkillMatchDetail, ProjectMatchDetail, 
    ExperienceMatchDetail, EducationMatchDetail, CertificationMatchDetail
)
from app.services.ranking_service import RankingService
from app.store.memory import InMemoryStore

def create_mock_breakdown():
    return ScoreBreakdown(
        skill_match=SkillMatchDetail(skill_score=0),
        semantic_similarity=0,
        experience_match=ExperienceMatchDetail(experience_score=0),
        project_relevance=ProjectMatchDetail(project_score=0),
        education_match=EducationMatchDetail(education_score=0),
        certification_match=CertificationMatchDetail(certification_score=0)
    )

@pytest.mark.asyncio
async def test_ranking_service_sorts_correctly():
    store = InMemoryStore()
    
    job_id = uuid.uuid4()
    
    class MockScoringService:
        def __init__(self):
            self.scores = [
                CandidateScore(candidate_id=uuid.uuid4(), candidate_name="Bob", overall_score=60.0, rank="", breakdown=create_mock_breakdown()),
                CandidateScore(candidate_id=uuid.uuid4(), candidate_name="Alice", overall_score=90.0, rank="", breakdown=create_mock_breakdown()),
                CandidateScore(candidate_id=uuid.uuid4(), candidate_name="Charlie", overall_score=40.0, rank="", breakdown=create_mock_breakdown()),
            ]
            self.index = 0
            
        def score_candidate(self, jd, jd_sem, res, res_sem):
            score = self.scores[self.index]
            self.index += 1
            return score

    store.get_job = AsyncMock(return_value=Mock(job_description_id=uuid.uuid4()))
    store.get_jd_profile = AsyncMock(return_value=Mock(id=uuid.uuid4()))
    store.get_semantic_profile_by_source = AsyncMock(return_value=Mock())
    store.list_resume_profiles_by_job = AsyncMock(return_value=[Mock(id=uuid.uuid4()), Mock(id=uuid.uuid4()), Mock(id=uuid.uuid4())])
    
    service = RankingService(store, MockScoringService())
    result = await service.rank_candidates_for_job(job_id)
    
    assert len(result.candidates) == 3
    assert result.candidates[0].candidate_name == "Alice"
    assert result.candidates[0].rank == "Strong Fit"
    
    assert result.candidates[1].candidate_name == "Bob"
    assert result.candidates[1].rank == "Average Fit"
    
    assert result.candidates[2].candidate_name == "Charlie"
    assert result.candidates[2].rank == "Poor Fit"
