"""
Analytics Service.

Deterministically aggregates candidate and scoring data to generate
recruiter-level hiring metrics and reports. No AI/LLM is used.
"""

from __future__ import annotations

from collections import Counter
from uuid import UUID

from app.exceptions import AppError
from app.logging_config import get_logger
from app.models.analytics import (
    AnalyticsSummary,
    SkillGapDetail,
    SkillGapSummary,
    RecommendationCandidateDetail,
    RecommendationSummary,
    ExecutiveSummary,
)
from app.store.memory import InMemoryStore

logger = get_logger(__name__)


class AnalyticsService:
    def __init__(self, store: InMemoryStore):
        self._store = store

    def _determine_recommendation(self, score: float) -> str:
        if score >= 85:
            return "Strong Fit"
        elif score >= 70:
            return "Good Fit"
        elif score >= 50:
            return "Average Fit"
        else:
            return "Poor Fit"

    async def get_analytics_summary(self, job_id: UUID) -> AnalyticsSummary:
        logger.info("Computing analytics summary for job_id=%s", job_id)
        
        ranking = await self._store.get_ranking(job_id)
        if not ranking or not ranking.candidates:
            raise AppError("RANKING_NOT_FOUND", f"No ranking results found for job {job_id}.", 404)
            
        candidates = ranking.candidates
        count = len(candidates)
        
        scores = [c.overall_score for c in candidates]
        highest = max(scores)
        lowest = min(scores)
        avg_score = sum(scores) / count
        
        total_exp = 0.0
        total_skill_score = 0.0
        rec_dist = {"Strong Fit": 0, "Good Fit": 0, "Average Fit": 0, "Poor Fit": 0}
        
        for cand in candidates:
            # Experience
            resume = await self._store.get_resume_profile(cand.candidate_id)
            if resume and resume.professional_information.total_years_experience:
                total_exp += resume.professional_information.total_years_experience
                
            # Skill Score
            total_skill_score += cand.breakdown.skill_match.skill_score
            
            # Recommendation
            band = self._determine_recommendation(cand.overall_score)
            rec_dist[band] = rec_dist.get(band, 0) + 1
            
        return AnalyticsSummary(
            candidates_reviewed=count,
            avg_match_score=round(avg_score, 1),
            highest_match_score=round(highest, 1),
            lowest_match_score=round(lowest, 1),
            avg_experience_years=round(total_exp / count, 1) if count > 0 else 0.0,
            avg_skill_match_score=round(total_skill_score / count, 1) if count > 0 else 0.0,
            recommendation_distribution=rec_dist
        )

    async def get_skill_gap_summary(self, job_id: UUID) -> SkillGapSummary:
        logger.info("Computing skill gap summary for job_id=%s", job_id)
        
        ranking = await self._store.get_ranking(job_id)
        if not ranking or not ranking.candidates:
            raise AppError("RANKING_NOT_FOUND", f"No ranking results found for job {job_id}.", 404)
            
        job_record = await self._store.get_job(job_id)
        jd_profile = None
        if job_record and job_record.job_description_id:
            jd_profile = await self._store.get_jd_profile(job_record.job_description_id)
            
        candidates = ranking.candidates
        
        # Aggregate matched and missing skills
        matched_counter = Counter()
        missing_counter = Counter()
        cert_counter = Counter()
        tech_counter = Counter()
        
        all_jd_skills = set()
        if jd_profile:
            all_jd_skills.update(jd_profile.required_skills)
            all_jd_skills.update(jd_profile.preferred_skills)
            
        for cand in candidates:
            breakdown = cand.breakdown
            for skill in breakdown.skill_match.matched_skills:
                matched_counter[skill] += 1
            for skill in breakdown.skill_match.missing_skills:
                missing_counter[skill] += 1
                
            # Certifications & Technologies from Resume Profile
            resume = await self._store.get_resume_profile(cand.candidate_id)
            if resume:
                for cert in resume.certifications:
                    cert_counter[cert.name] += 1
                if resume.skills:
                    for tech in (resume.skills.technical_skills + resume.skills.frameworks + resume.skills.tools):
                        tech_counter[tech] += 1
                        
        # Ensure all JD skills are accounted for in at least one counter
        for skill in all_jd_skills:
            if skill not in matched_counter and skill not in missing_counter:
                missing_counter[skill] = 0
                
        # Format Top Matching and Top Missing
        top_matching = [
            SkillGapDetail(skill_name=skill, match_count=count, gap_count=missing_counter[skill])
            for skill, count in matched_counter.most_common()
        ]
        
        top_missing = [
            SkillGapDetail(skill_name=skill, match_count=matched_counter[skill], gap_count=count)
            for skill, count in missing_counter.most_common()
        ]
        
        return SkillGapSummary(
            top_missing_skills=top_missing[:10],
            top_matching_skills=top_matching[:10],
            most_common_certifications=[cert for cert, _ in cert_counter.most_common(5)],
            most_common_technologies=[tech for tech, _ in tech_counter.most_common(10)],
            most_requested_skills=jd_profile.required_skills if jd_profile else [],
            most_missing_certifications=jd_profile.certifications if jd_profile else []
        )

    async def get_recommendation_summary(self, job_id: UUID) -> RecommendationSummary:
        logger.info("Computing recommendation summary for job_id=%s", job_id)
        
        ranking = await self._store.get_ranking(job_id)
        if not ranking or not ranking.candidates:
            raise AppError("RANKING_NOT_FOUND", f"No ranking results found for job {job_id}.", 404)
            
        candidates = ranking.candidates
        sorted_candidates = sorted(candidates, key=lambda c: c.overall_score, reverse=True)
        
        details = [
            RecommendationCandidateDetail(
                candidate_id=c.candidate_id,
                candidate_name=c.candidate_name,
                overall_score=c.overall_score,
                recommendation=self._determine_recommendation(c.overall_score)
            )
            for c in sorted_candidates
        ]
        
        top_candidate = details[0] if details else None
        top_3 = details[:3]
        
        # Additional interview focus: scores < 70 in some categories
        interview_focus = []
        for c in sorted_candidates:
            b = c.breakdown
            if (b.project_relevance.project_score < 70 or 
                b.experience_match.experience_score < 70 or 
                b.skill_match.skill_score < 70):
                interview_focus.append(
                    RecommendationCandidateDetail(
                        candidate_id=c.candidate_id,
                        candidate_name=c.candidate_name,
                        overall_score=c.overall_score,
                        recommendation=self._determine_recommendation(c.overall_score)
                    )
                )
                
        # Suitable for future roles: Average or Good fit, not the top candidate
        future_roles = []
        for d in details:
            if d.recommendation in ["Good Fit", "Average Fit"] and d.candidate_id != (top_candidate.candidate_id if top_candidate else None):
                future_roles.append(d)
                
        return RecommendationSummary(
            top_candidate=top_candidate,
            top_3_candidates=top_3,
            additional_interview_focus=interview_focus,
            suitable_for_future_roles=future_roles
        )

    async def get_executive_summary(self, job_id: UUID) -> ExecutiveSummary:
        logger.info("Generating executive summary for job_id=%s", job_id)
        
        job_record = await self._store.get_job(job_id)
        job_title = "Unknown Role"
        if job_record and job_record.job_description_id:
            jd = await self._store.get_jd_profile(job_record.job_description_id)
            if jd:
                job_title = jd.job_title
                
        analytics = await self.get_analytics_summary(job_id)
        recs = await self.get_recommendation_summary(job_id)
        
        total_cands = analytics.candidates_reviewed
        highest_score = analytics.highest_match_score
        avg_score = analytics.avg_match_score
        
        exec_text = (
            f"A total of {total_cands} candidates were evaluated for the {job_title} role. "
            f"The evaluation shows a robust talent pipeline with a top score of {highest_score}% "
            f"and an overall average match score of {avg_score}%."
        )
        
        strong_count = analytics.recommendation_distribution.get("Strong Fit", 0)
        good_count = analytics.recommendation_distribution.get("Good Fit", 0)
        
        highlights = [
            f"Identified {strong_count} candidates matching criteria as a Strong Fit.",
            f"Top matching candidate is {recs.top_candidate.candidate_name if recs.top_candidate else 'None'} ({highest_score}% match).",
            f"Pipeline average professional experience stands at {analytics.avg_experience_years} years."
        ]
        
        top_names = ", ".join([c.candidate_name for c in recs.top_3_candidates])
        action = f"Proceed to schedule interviews for the top candidate(s): {top_names}." if top_names else "No suitable candidates found."
        
        return ExecutiveSummary(
            job_title=job_title,
            total_candidates=total_cands,
            executive_text_summary=exec_text,
            key_highlights=highlights,
            recommendation_action=action
        )
