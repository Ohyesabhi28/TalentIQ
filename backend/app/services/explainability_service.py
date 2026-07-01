"""
Explainability Service.

Transforms deterministic JSON scoring data into human-readable insights
using Google Gemini, strictly enforcing no hallucination.
"""

from __future__ import annotations

import json
from uuid import UUID

import google.generativeai as genai

from app.config import Settings
from app.exceptions import AppError
from app.logging_config import get_logger
from app.models.explainability import CandidateInsight, HiringRecommendationRecord
from app.models.scoring import CandidateScore
from app.store.memory import InMemoryStore

logger = get_logger(__name__)


class ExplainabilityService:
    def __init__(self, store: InMemoryStore, settings: Settings):
        self._store = store
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # We use standard gemini-2.5-flash for rewriting structured data
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=(
                "You are an expert technical recruiter AI. "
                "Your job is to transform structured JSON candidate and scoring evidence into a human-readable explanation. "
                "CRITICAL: You MUST NOT invent, guess, or hallucinate any information. "
                "Every statement must be strictly backed by the provided candidate profile (ResumeProfile) and score breakdown. "
                "No unsupported claims. No invented skills. No invented experience. "
                "Keep the tone professional, objective, and action-oriented."
            )
        )

    def _determine_recommendation(self, score: float) -> str:
        if score >= 85:
            return "Strong Fit"
        elif score >= 70:
            return "Good Fit"
        elif score >= 50:
            return "Average Fit"
        else:
            return "Poor Fit"

    def _generate_interview_focus_areas(self, candidate: CandidateScore) -> list[str]:
        focus_areas = []
        breakdown = candidate.breakdown
        
        # Missing skills -> Interview [Skill]
        if breakdown.skill_match.missing_skills:
            for skill in breakdown.skill_match.missing_skills:
                focus_areas.append(f"Interview {skill}")
                
        # Weak scoring categories (< 70)
        if breakdown.project_relevance.project_score < 70:
            focus_areas.append("Ask about real-world projects")
        if breakdown.experience_match.experience_score < 70:
            focus_areas.append("Inquire about depth of experience and years of professional work")
        if breakdown.skill_match.skill_score < 70:
            focus_areas.append("Assess hands-on technical abilities and foundational coding")
        if breakdown.education_match.education_score < 70:
            focus_areas.append("Discuss educational background or equivalent industry training")
        if breakdown.certification_match.certification_score < 70:
            focus_areas.append("Verify relevant professional certifications and credentials")
            
        return focus_areas

    async def generate_insights_for_job(self, job_id: UUID) -> list[HiringRecommendationRecord]:
        logger.info("Starting insight generation for job_id=%s", job_id)
        
        ranking = await self._store.get_ranking(job_id)
        if not ranking:
            raise AppError("RANKING_NOT_FOUND", f"No ranking found for job {job_id}. Must rank first.", 400)
            
        recommendations = []
        for candidate_score in ranking.candidates:
            rec = await self._generate_insight_for_candidate(job_id, candidate_score)
            recommendations.append(rec)
            
        logger.info("Successfully generated insights for %d candidates on job_id=%s", len(recommendations), job_id)
        return recommendations

    async def _generate_insight_for_candidate(self, job_id: UUID, candidate: CandidateScore) -> HiringRecommendationRecord:
        logger.debug("Generating insight for candidate %s", candidate.candidate_name)
        
        resume = await self._store.get_resume_profile(candidate.candidate_id)
        if not resume:
            raise AppError("RESUME_PROFILE_NOT_FOUND", f"Resume profile not found for candidate {candidate.candidate_id}", 404)
            
        rec_label = self._determine_recommendation(candidate.overall_score)
        focus_areas = self._generate_interview_focus_areas(candidate)
        
        # Prepare structured context for Gemini
        evidence = {
            "candidate_name": candidate.candidate_name,
            "overall_score": candidate.overall_score,
            "deterministic_recommendation": rec_label,
            "score_breakdown": candidate.breakdown.model_dump(),
            "resume_profile": {
                "personal_info": resume.personal_information.model_dump(),
                "professional_info": resume.professional_information.model_dump(),
                "skills": resume.skills.model_dump(),
                "experience": [exp.model_dump() for exp in resume.experience],
                "projects": [proj.model_dump() for proj in resume.projects],
                "education": [edu.model_dump() for edu in resume.education],
                "certifications": [cert.model_dump() for cert in resume.certifications],
                "summary": resume.summary
            }
        }
        
        prompt = (
            f"Here is the deterministic scoring evidence and candidate profile:\n"
            f"{json.dumps(evidence, indent=2)}\n\n"
            f"Generate a CandidateInsight object matching the response schema.\n"
            f"Requirements:\n"
            f"1. overall_summary: Summary of candidate's qualifications and fit.\n"
            f"2. top_strengths: Factual list of 2-3 key strengths matching JD. Strictly use facts from the resume.\n"
            f"3. top_weaknesses: Factual list of 2-3 gaps or weaknesses based on missing skills or lower scores.\n"
            f"4. matched_skills: Copy exactly from score_breakdown.skill_match.matched_skills.\n"
            f"5. missing_skills: Copy exactly from score_breakdown.skill_match.missing_skills.\n"
            f"6. relevant_projects: Highlight actual projects from the projects list that align with the role.\n"
            f"7. experience_highlights: Key professional achievements/milestones from work history.\n"
            f"8. education_summary: Summarize candidate's degree, specialization, and institution.\n"
            f"9. certification_summary: Summarize candidate's certifications.\n"
            f"10. interview_focus_areas: Populate using exactly this list: {focus_areas}.\n"
            f"11. hiring_recommendation: Output exactly '{rec_label}'.\n"
        )
        
        try:
            # We use generate_content_async with a strict response schema
            response = await self.model.generate_content_async(
                contents=prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=CandidateInsight,
                    temperature=0.1,  # Keep it deterministic and strict
                )
            )
            
            raw_text = response.text
            insight_data = json.loads(raw_text)
            
            # Double check recommendation & interview focus areas to ensure safety & determinism
            insight_data["hiring_recommendation"] = rec_label
            insight_data["interview_focus_areas"] = focus_areas
            
            insight = CandidateInsight.model_validate(insight_data)
            
            record = HiringRecommendationRecord(
                analysis_job_id=job_id,
                candidate_id=candidate.candidate_id,
                overall_score=candidate.overall_score,
                recommendation=rec_label,
                insight=insight
            )
            
            await self._store.save_recommendation(record)
            return record
            
        except Exception as e:
            logger.exception("Failed to generate insight for candidate %s", candidate.candidate_id)
            raise AppError("INSIGHT_GENERATION_FAILED", "Failed to generate AI insights from scoring data.", 500) from e

    async def get_insights_for_job(self, job_id: UUID) -> list[HiringRecommendationRecord]:
        return await self._store.list_recommendations_by_job(job_id)
        
    async def get_insight_for_candidate(self, candidate_id: UUID) -> HiringRecommendationRecord:
        rec = await self._store.get_recommendation(candidate_id)
        if not rec:
            raise AppError("INSIGHT_NOT_FOUND", f"No insights generated for candidate {candidate_id}.", 404)
        return rec
