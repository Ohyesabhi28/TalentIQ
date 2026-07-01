"""
Tests for ScoringService (Module 6).
"""

from __future__ import annotations

import uuid
import numpy as np
import pytest

from app.models.jd import JDProfileRecord, JDProfileBase
from app.models.resume import (
    ResumeProfileRecord, ResumeProfileBase, PersonalInformation,
    ProfessionalInformation, SkillGroup, WorkExperience, Project, Education
)
from app.models.semantic import SemanticProfileRecord
from app.services.embedding import EmbeddingService
from app.services.vector import VectorService
from app.services.scoring_service import ScoringService

class MockEmbeddingService(EmbeddingService):
    def generate_embeddings(self, texts):
        shape = (len(texts), 384)
        arr = np.random.rand(*shape).astype(np.float32)
        norms = np.linalg.norm(arr, axis=1, keepdims=True)
        return arr / norms

@pytest.fixture
def scoring_service():
    embed = MockEmbeddingService()
    vector = VectorService()
    return ScoringService(embedding_service=embed, vector_service=vector)

def test_scoring_logic_basic(scoring_service):
    jd_id = uuid.uuid4()
    res_id = uuid.uuid4()
    job_id = uuid.uuid4()
    
    jd = JDProfileRecord(
        id=jd_id,
        analysis_job_id=job_id,
        original_file_id=uuid.uuid4(),
        raw_text="",
        job_title="Dev",
        required_skills=["Python", "FastAPI"],
        responsibilities=["Code", "Deploy"],
        experience="2 years",
        education="BS CS"
    )
    
    resume = ResumeProfileRecord(
        id=res_id,
        analysis_job_id=job_id,
        original_file_id=uuid.uuid4(),
        raw_text="",
        personal_information=PersonalInformation(name="Alice"),
        professional_information=ProfessionalInformation(total_years_experience=3),
        skills=SkillGroup(technical_skills=["Python", "FastAPI"]),
        experience=[],
        projects=[Project(project_name="Web App", description="API", technologies=["Python"])],
        education=[Education(degree="BS CS", institution="MIT")],
        certifications=[],
        achievements=[],
        publications=[]
    )
    
    jd_sem = SemanticProfileRecord(
        id=uuid.uuid4(), profile_type="job_description", source_id=jd_id, analysis_job_id=job_id,
        full_document_embedding=[0.5]*384
    )
    
    res_sem = SemanticProfileRecord(
        id=uuid.uuid4(), profile_type="resume", source_id=res_id, analysis_job_id=job_id,
        full_document_embedding=[0.5]*384
    )
    
    score = scoring_service.score_candidate(jd, jd_sem, resume, res_sem)
    
    assert score.candidate_name == "Alice"
    assert score.overall_score > 0
    assert score.breakdown.experience_match.experience_score == 100.0
