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
                "Your job is to transform structured JSON scoring data into a human-readable explanation. "
                "CRITICAL: You MUST NOT invent, guess, or hallucinate any information. "
                "You must ONLY base your insights on the exact JSON evidence provided. "
                "Keep the tone professional, objective, and action-oriented."
            )
        )

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
        
        prompt = (
            f"Here is the deterministic scoring evidence for candidate '{candidate.candidate_name}'.\n"
            f"Overall Score: {candidate.overall_score}/100\n"
            f"Recommendation Band: {candidate.rank}\n"
            f"Score Breakdown JSON: {candidate.breakdown.model_dump_json()}\n\n"
            "Generate a structured explanation. For matched/missing skills, simply copy them exactly from the evidence JSON."
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
            insight = CandidateInsight.model_validate(insight_data)
            
            record = HiringRecommendationRecord(
                analysis_job_id=job_id,
                candidate_id=candidate.candidate_id,
                overall_score=candidate.overall_score,
                recommendation=candidate.rank,
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
