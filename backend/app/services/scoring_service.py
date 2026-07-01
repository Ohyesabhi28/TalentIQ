"""
Scoring Service.

Deterministic scoring engine evaluating a Resume against a Job Description.
"""

from __future__ import annotations

import numpy as np

from app.logging_config import get_logger
from app.models.jd import JDProfileRecord
from app.models.resume import ResumeProfileRecord
from app.models.semantic import SemanticProfileRecord
from app.models.scoring import (
    ScoreBreakdown,
    SkillMatchDetail,
    ProjectMatchDetail,
    ExperienceMatchDetail,
    EducationMatchDetail,
    CertificationMatchDetail,
    CandidateScore,
)
from app.services.embedding import EmbeddingService
from app.services.vector import VectorService

logger = get_logger(__name__)

# Scoring Weights
WEIGHT_SKILL = 0.35
WEIGHT_SEMANTIC = 0.25
WEIGHT_EXPERIENCE = 0.15
WEIGHT_PROJECT = 0.10
WEIGHT_EDUCATION = 0.10
WEIGHT_CERTIFICATION = 0.05

class ScoringService:
    def __init__(self, embedding_service: EmbeddingService, vector_service: VectorService):
        self._embedding = embedding_service
        self._vector = vector_service

    def score_candidate(
        self,
        jd: JDProfileRecord,
        jd_semantic: SemanticProfileRecord,
        resume: ResumeProfileRecord,
        resume_semantic: SemanticProfileRecord,
    ) -> CandidateScore:
        
        # 1. Skill Match (35%)
        skill_detail = self._score_skills(jd, resume)
        
        # 2. Semantic Similarity (25%)
        semantic_score = self._score_semantics(jd_semantic, resume_semantic)
        
        # 3. Experience Match (15%)
        experience_detail = self._score_experience(jd, resume)
        
        # 4. Project Relevance (10%)
        project_detail = self._score_projects(jd, resume)
        
        # 5. Education Match (10%)
        education_detail = self._score_education(jd, resume)
        
        # 6. Certification Match (5%)
        certification_detail = self._score_certifications(jd, resume)
        
        # Calculate Weighted Overall Score
        overall = (
            (skill_detail.skill_score * WEIGHT_SKILL) +
            (semantic_score * WEIGHT_SEMANTIC) +
            (experience_detail.experience_score * WEIGHT_EXPERIENCE) +
            (project_detail.project_score * WEIGHT_PROJECT) +
            (education_detail.education_score * WEIGHT_EDUCATION) +
            (certification_detail.certification_score * WEIGHT_CERTIFICATION)
        )
        
        # Note: Rank is set by the RankingService later, we use a placeholder here.
        
        breakdown = ScoreBreakdown(
            skill_match=skill_detail,
            semantic_similarity=semantic_score,
            experience_match=experience_detail,
            project_relevance=project_detail,
            education_match=education_detail,
            certification_match=certification_detail,
        )
        
        return CandidateScore(
            candidate_id=resume.id,
            candidate_name=resume.personal_information.name,
            overall_score=round(overall, 2),
            breakdown=breakdown,
            rank="",
        )

    def _score_skills(self, jd: JDProfileRecord, resume: ResumeProfileRecord) -> SkillMatchDetail:
        jd_skills = set(jd.required_skills + (jd.preferred_skills or []))
        if not jd_skills:
            return SkillMatchDetail(matched_skills=[], missing_skills=[], skill_score=100.0)
            
        resume_skills_list = (
            resume.skills.technical_skills +
            resume.skills.frameworks +
            resume.skills.languages +
            resume.skills.tools +
            resume.skills.cloud_platforms +
            resume.skills.databases +
            resume.skills.soft_skills
        )
        
        matched = []
        missing = []
        
        if not resume_skills_list:
            return SkillMatchDetail(matched_skills=[], missing_skills=list(jd_skills), skill_score=0.0)
            
        # Create a temporary FAISS index for resume skills
        # This is a naive but effective way to do semantic matching
        resume_vecs = self._embedding.generate_embeddings(resume_skills_list)
        temp_index = VectorService(dimension=resume_vecs.shape[1])
        temp_index.add_vectors(resume_vecs, resume_skills_list)
        
        for req_skill in jd_skills:
            q_vec = self._embedding.generate_embedding(req_skill)
            results = temp_index.search(q_vec, top_k=1)
            # Threshold for "semantic match" - inner product > 0.8
            if results and results[0][1] > 0.8:
                matched.append(req_skill)
            else:
                missing.append(req_skill)
                
        score = (len(matched) / len(jd_skills)) * 100.0 if jd_skills else 100.0
        return SkillMatchDetail(
            matched_skills=matched,
            missing_skills=missing,
            skill_score=round(score, 2)
        )

    def _score_semantics(self, jd_sem: SemanticProfileRecord, res_sem: SemanticProfileRecord) -> float:
        jd_vec = np.array(jd_sem.full_document_embedding, dtype=np.float32)
        res_vec = np.array(res_sem.full_document_embedding, dtype=np.float32)
        
        if len(jd_vec) == 0 or len(res_vec) == 0:
            return 0.0
            
        similarity = float(np.dot(jd_vec, res_vec))
        # Ensure it maps nicely to a 0-100 scale (clip negative values)
        score = max(0.0, min(1.0, similarity)) * 100.0
        return round(score, 2)

    def _score_experience(self, jd: JDProfileRecord, resume: ResumeProfileRecord) -> ExperienceMatchDetail:
        req_years_str = jd.experience
        req_years = 0.0
        if req_years_str:
            import re
            nums = re.findall(r'\d+', req_years_str)
            if nums:
                req_years = float(nums[0])
                
        cand_years = resume.professional_information.total_years_experience or 0.0
        
        if req_years == 0.0:
            score = 100.0
        else:
            score = min(100.0, (cand_years / req_years) * 100.0)
            
        return ExperienceMatchDetail(
            required_years=req_years,
            candidate_years=cand_years,
            experience_score=round(score, 2)
        )

    def _score_projects(self, jd: JDProfileRecord, resume: ResumeProfileRecord) -> ProjectMatchDetail:
        if not jd.responsibilities or not resume.projects:
            # If JD asks for nothing or candidate has no projects, neutral score
            return ProjectMatchDetail(top_matching_projects=[], project_score=50.0 if jd.responsibilities else 100.0)
            
        resp_text = " ".join(jd.responsibilities)
        resp_vec = self._embedding.generate_embedding(resp_text)
        
        proj_texts = [p.description or p.project_name for p in resume.projects]
        proj_vecs = self._embedding.generate_embeddings(proj_texts)
        
        temp_index = VectorService(dimension=proj_vecs.shape[1])
        temp_index.add_vectors(proj_vecs, [p.project_name for p in resume.projects])
        
        results = temp_index.search(resp_vec, top_k=3)
        top_projects = [r[0] for r in results]
        
        # Average similarity of top projects
        avg_sim = sum(r[1] for r in results) / len(results) if results else 0.0
        score = max(0.0, min(1.0, avg_sim)) * 100.0
        
        return ProjectMatchDetail(
            top_matching_projects=top_projects,
            project_score=round(score, 2)
        )

    def _score_education(self, jd: JDProfileRecord, resume: ResumeProfileRecord) -> EducationMatchDetail:
        req_edu = jd.education
        cand_edu = resume.education[0].degree if resume.education else "None"
        
        # Basic heuristic: if both exist, do a quick semantic check
        score = 50.0 
        if not req_edu:
            score = 100.0
        elif req_edu and cand_edu != "None":
            req_vec = self._embedding.generate_embedding(req_edu)
            cand_vec = self._embedding.generate_embedding(cand_edu)
            sim = float(np.dot(req_vec, cand_vec))
            score = max(0.0, min(1.0, sim)) * 100.0
            
        return EducationMatchDetail(
            required_degree=req_edu,
            candidate_degree=cand_edu,
            education_score=round(score, 2)
        )

    def _score_certifications(self, jd: JDProfileRecord, resume: ResumeProfileRecord) -> CertificationMatchDetail:
        req_certs = jd.certifications or []
        cand_certs = [c.name for c in resume.certifications]
        
        if not req_certs:
            return CertificationMatchDetail(
                matched_certifications=[],
                missing_certifications=[],
                certification_score=100.0
            )
            
        if not cand_certs:
            return CertificationMatchDetail(
                matched_certifications=[],
                missing_certifications=req_certs,
                certification_score=0.0
            )
            
        matched = []
        missing = []
        
        cand_vecs = self._embedding.generate_embeddings(cand_certs)
        temp_index = VectorService(dimension=cand_vecs.shape[1])
        temp_index.add_vectors(cand_vecs, cand_certs)
        
        for req in req_certs:
            q_vec = self._embedding.generate_embedding(req)
            results = temp_index.search(q_vec, top_k=1)
            if results and results[0][1] > 0.8:
                matched.append(req)
            else:
                missing.append(req)
                
        score = (len(matched) / len(req_certs)) * 100.0
        return CertificationMatchDetail(
            matched_certifications=matched,
            missing_certifications=missing,
            certification_score=round(score, 2)
        )
