"""
Tests for AnalyticsService (Module 8).
"""

from __future__ import annotations

import uuid
import pytest
from unittest.mock import Mock, AsyncMock

from app.models.scoring import CandidateScore, ScoreBreakdown, SkillMatchDetail, ProjectMatchDetail, ExperienceMatchDetail, EducationMatchDetail, CertificationMatchDetail, RankingResultRecord
from app.models.resume import ResumeProfileRecord, PersonalInformation, ProfessionalInformation, SkillGroup
from app.models.jd import JDProfileRecord
from app.models.analysis import AnalysisJobRecord
from app.services.analytics_service import AnalyticsService
from app.store.memory import InMemoryStore

@pytest.fixture
def store():
    return InMemoryStore()

@pytest.mark.asyncio
async def test_analytics_generation(store):
    service = AnalyticsService(store)
    
    cand_id_1 = uuid.uuid4()
    cand_id_2 = uuid.uuid4()
    job_id = uuid.uuid4()
    jd_id = uuid.uuid4()
    
    # Mock Job & JD
    job = AnalysisJobRecord(
        id=job_id,
        job_description_file_id=uuid.uuid4(),
        job_description_id=jd_id
    )
    jd = JDProfileRecord(
        id=jd_id,
        raw_text="Required: Python, Go. Certifications: AWS",
        job_title="DevOps Engineer",
        required_skills=["Python", "Go"],
        preferred_skills=[],
        certifications=["AWS"]
    )
    
    # Mock Candidates
    cand1 = CandidateScore(
        candidate_id=cand_id_1,
        candidate_name="Alice",
        overall_score=90.0,
        rank="Strong Fit",
        breakdown=ScoreBreakdown(
            skill_match=SkillMatchDetail(skill_score=95.0, matched_skills=["Python", "Go"], missing_skills=[]),
            semantic_similarity=90.0,
            experience_match=ExperienceMatchDetail(experience_score=100.0),
            project_relevance=ProjectMatchDetail(project_score=90.0),
            education_match=EducationMatchDetail(education_score=100.0),
            certification_match=CertificationMatchDetail(certification_score=100.0)
        )
    )
    
    # Bob has scores < 70
    cand2 = CandidateScore(
        candidate_id=cand_id_2,
        candidate_name="Bob",
        overall_score=65.0,
        rank="Average Fit",
        breakdown=ScoreBreakdown(
            skill_match=SkillMatchDetail(skill_score=60.0, matched_skills=["Python"], missing_skills=["Go"]),
            semantic_similarity=65.0,
            experience_match=ExperienceMatchDetail(experience_score=50.0),
            project_relevance=ProjectMatchDetail(project_score=65.0),
            education_match=EducationMatchDetail(education_score=100.0),
            certification_match=CertificationMatchDetail(certification_score=0.0)
        )
    )
    
    # Resumes
    res1 = ResumeProfileRecord(
        id=cand_id_1,
        analysis_job_id=job_id,
        original_file_id=uuid.uuid4(),
        raw_text="Alice Resume",
        personal_information=PersonalInformation(name="Alice"),
        professional_information=ProfessionalInformation(total_years_experience=5.0, current_role="Senior DevOps"),
        skills=SkillGroup(languages=["Python", "Go"]),
        experience=[],
        projects=[],
        education=[],
        certifications=[]
    )
    
    res2 = ResumeProfileRecord(
        id=cand_id_2,
        analysis_job_id=job_id,
        original_file_id=uuid.uuid4(),
        raw_text="Bob Resume",
        personal_information=PersonalInformation(name="Bob"),
        professional_information=ProfessionalInformation(total_years_experience=2.0, current_role="DevOps"),
        skills=SkillGroup(languages=["Python"]),
        experience=[],
        projects=[],
        education=[],
        certifications=[]
    )
    
    ranking = RankingResultRecord(analysis_job_id=job_id, candidates=[cand1, cand2])
    
    # Save to store
    await store.save_job(job)
    await store.save_jd_profile(jd)
    await store.save_resume_profile(res1)
    await store.save_resume_profile(res2)
    await store.save_ranking(ranking)
    
    # Run tests
    analytics = await service.get_analytics_summary(job_id)
    assert analytics.candidates_reviewed == 2
    assert analytics.highest_match_score == 90.0
    assert analytics.lowest_match_score == 65.0
    assert analytics.avg_match_score == 77.5
    assert analytics.avg_experience_years == 3.5
    assert analytics.recommendation_distribution["Strong Fit"] == 1
    assert analytics.recommendation_distribution["Average Fit"] == 1
    
    skill_gap = await service.get_skill_gap_summary(job_id)
    assert len(skill_gap.top_matching_skills) > 0
    assert skill_gap.top_matching_skills[0].skill_name == "Python"
    
    recs = await service.get_recommendation_summary(job_id)
    assert recs.top_candidate.candidate_name == "Alice"
    assert len(recs.top_3_candidates) == 2
    assert len(recs.additional_interview_focus) == 1
    assert len(recs.suitable_for_future_roles) == 1
    
    exec_summary = await service.get_executive_summary(job_id)
    assert exec_summary.total_candidates == 2
    assert "DevOps Engineer" in exec_summary.executive_text_summary
