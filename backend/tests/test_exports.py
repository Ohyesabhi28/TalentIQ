"""
Tests for ExportService (Module 9).
"""

from __future__ import annotations

import io
import uuid
import openpyxl
import pytest
from unittest.mock import Mock, AsyncMock

from app.models.scoring import CandidateScore, ScoreBreakdown, SkillMatchDetail, ProjectMatchDetail, ExperienceMatchDetail, EducationMatchDetail, CertificationMatchDetail, RankingResultRecord
from app.models.resume import ResumeProfileRecord, PersonalInformation, ProfessionalInformation, SkillGroup
from app.models.jd import JDProfileRecord
from app.models.analysis import AnalysisJobRecord
from app.models.explainability import HiringRecommendationRecord, CandidateInsight
from app.services.export_service import ExportService
from app.store.memory import InMemoryStore


@pytest.fixture
def store():
    return InMemoryStore()


@pytest.mark.asyncio
async def test_excel_export(store):
    service = ExportService(store)
    
    cand_id = uuid.uuid4()
    job_id = uuid.uuid4()
    jd_id = uuid.uuid4()
    
    # Mock data
    job = AnalysisJobRecord(id=job_id, job_description_file_id=uuid.uuid4(), job_description_id=jd_id)
    jd = JDProfileRecord(id=jd_id, raw_text="Req", job_title="Engineer", required_skills=["Python"])
    
    cand = CandidateScore(
        candidate_id=cand_id,
        candidate_name="Alice",
        overall_score=85.0,
        rank="Strong Fit",
        breakdown=ScoreBreakdown(
            skill_match=SkillMatchDetail(skill_score=90.0, matched_skills=["Python"], missing_skills=[]),
            semantic_similarity=80.0,
            experience_match=ExperienceMatchDetail(experience_score=100.0),
            project_relevance=ProjectMatchDetail(project_score=80.0),
            education_match=EducationMatchDetail(education_score=100.0),
            certification_match=CertificationMatchDetail(certification_score=100.0)
        )
    )
    
    res = ResumeProfileRecord(
        id=cand_id,
        analysis_job_id=job_id,
        original_file_id=uuid.uuid4(),
        raw_text="Alice",
        personal_information=PersonalInformation(name="Alice"),
        professional_information=ProfessionalInformation(total_years_experience=3.0),
        skills=SkillGroup(languages=["Python"]),
        experience=[],
        projects=[],
        education=[],
        certifications=[]
    )
    
    ranking = RankingResultRecord(analysis_job_id=job_id, candidates=[cand])
    
    rec = HiringRecommendationRecord(
        analysis_job_id=job_id,
        candidate_id=cand_id,
        overall_score=85.0,
        recommendation="Strong Fit",
        insight=CandidateInsight(
            overall_summary="Great",
            top_strengths=["Python"],
            top_weaknesses=[],
            matched_skills=["Python"],
            missing_skills=[],
            relevant_projects=[],
            experience_highlights=[],
            education_summary="BSc",
            certification_summary="None",
            interview_focus_areas=[],
            hiring_recommendation="Strong Fit"
        )
    )
    
    await store.save_job(job)
    await store.save_jd_profile(jd)
    await store.save_resume_profile(res)
    await store.save_ranking(ranking)
    await store.save_recommendation(rec)
    
    # Verify Excel
    xlsx_bytes = await service.export_to_excel(job_id)
    assert len(xlsx_bytes) > 0
    wb = openpyxl.load_workbook(io.BytesIO(xlsx_bytes))
    sheet = wb.active
    assert sheet["B2"].value == "Alice"
    
    # Verify PDF
    pdf_bytes = await service.export_to_pdf(job_id)
    assert len(pdf_bytes) > 0
    assert pdf_bytes.startswith(b"%PDF")
    
    # Verify JSON
    json_data = await service.export_to_json(job_id)
    assert json_data["job_id"] == str(job_id)
    assert json_data["ranking"]["candidates"][0]["candidate_name"] == "Alice"
