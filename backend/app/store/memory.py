"""
In-memory store — temporary persistence layer for Modules 2, 3, 4, 5, 6, and 7.
"""

from __future__ import annotations

import asyncio
from uuid import UUID

from app.logging_config import get_logger
from app.models.analysis import AnalysisJobRecord
from app.models.file import UploadedFileRecord
from app.models.jd import JDProfileRecord
from app.models.resume import ResumeProfileRecord
from app.models.semantic import SemanticProfileRecord
from app.models.scoring import RankingResultRecord
from app.models.explainability import HiringRecommendationRecord

logger = get_logger(__name__)


class InMemoryStore:
    def __init__(self) -> None:
        self._files: dict[UUID, UploadedFileRecord] = {}
        self._jobs: dict[UUID, AnalysisJobRecord] = {}
        self._jd_profiles: dict[UUID, JDProfileRecord] = {}
        self._resume_profiles: dict[UUID, ResumeProfileRecord] = {}
        self._semantic_profiles: dict[UUID, SemanticProfileRecord] = {}
        self._rankings: dict[UUID, RankingResultRecord] = {}
        self._recommendations: dict[UUID, HiringRecommendationRecord] = {}
        self._lock: asyncio.Lock = asyncio.Lock()

    # ── File Operations ────────────────────────────────────────────────────
    async def save_file(self, record: UploadedFileRecord) -> None:
        async with self._lock:
            self._files[record.id] = record

    async def get_file(self, file_id: UUID) -> UploadedFileRecord | None:
        async with self._lock:
            return self._files.get(file_id)

    async def delete_file(self, file_id: UUID) -> bool:
        async with self._lock:
            if file_id in self._files:
                del self._files[file_id]
                return True
            return False

    async def find_files_by_md5(self, md5_hash: str) -> list[UploadedFileRecord]:
        async with self._lock:
            return [f for f in self._files.values() if f.md5_hash == md5_hash]

    async def list_files(self) -> list[UploadedFileRecord]:
        async with self._lock:
            return list(self._files.values())

    # ── Job Operations ─────────────────────────────────────────────────────
    async def save_job(self, job: AnalysisJobRecord) -> None:
        async with self._lock:
            self._jobs[job.id] = job

    async def get_job(self, job_id: UUID) -> AnalysisJobRecord | None:
        async with self._lock:
            return self._jobs.get(job_id)

    async def update_job(self, job: AnalysisJobRecord) -> None:
        async with self._lock:
            self._jobs[job.id] = job

    async def list_jobs(self) -> list[AnalysisJobRecord]:
        async with self._lock:
            return list(self._jobs.values())

    # ── JD Profile Operations ──────────────────────────────────────────────
    async def save_jd_profile(self, profile: JDProfileRecord) -> None:
        async with self._lock:
            self._jd_profiles[profile.id] = profile

    async def get_jd_profile(self, profile_id: UUID) -> JDProfileRecord | None:
        async with self._lock:
            return self._jd_profiles.get(profile_id)

    # ── Resume Profile Operations ──────────────────────────────────────────
    async def save_resume_profile(self, profile: ResumeProfileRecord) -> None:
        async with self._lock:
            self._resume_profiles[profile.id] = profile

    async def get_resume_profile(self, profile_id: UUID) -> ResumeProfileRecord | None:
        async with self._lock:
            return self._resume_profiles.get(profile_id)

    async def list_resume_profiles_by_job(self, job_id: UUID) -> list[ResumeProfileRecord]:
        async with self._lock:
            return [p for p in self._resume_profiles.values() if p.analysis_job_id == job_id]

    # ── Semantic Profile Operations ────────────────────────────────────────
    async def save_semantic_profile(self, profile: SemanticProfileRecord) -> None:
        async with self._lock:
            self._semantic_profiles[profile.id] = profile

    async def get_semantic_profile(self, profile_id: UUID) -> SemanticProfileRecord | None:
        async with self._lock:
            return self._semantic_profiles.get(profile_id)

    async def get_semantic_profile_by_source(self, source_id: UUID) -> SemanticProfileRecord | None:
        async with self._lock:
            for profile in self._semantic_profiles.values():
                if profile.source_id == source_id:
                    return profile
            return None

    async def list_semantic_profiles_by_job(self, job_id: UUID) -> list[SemanticProfileRecord]:
        async with self._lock:
            return [p for p in self._semantic_profiles.values() if p.analysis_job_id == job_id]

    # ── Ranking Operations ─────────────────────────────────────────────────
    async def save_ranking(self, ranking: RankingResultRecord) -> None:
        async with self._lock:
            self._rankings[ranking.analysis_job_id] = ranking

    async def get_ranking(self, job_id: UUID) -> RankingResultRecord | None:
        async with self._lock:
            return self._rankings.get(job_id)

    # ── Explainability Operations ──────────────────────────────────────────
    async def save_recommendation(self, recommendation: HiringRecommendationRecord) -> None:
        async with self._lock:
            self._recommendations[recommendation.candidate_id] = recommendation

    async def get_recommendation(self, candidate_id: UUID) -> HiringRecommendationRecord | None:
        async with self._lock:
            return self._recommendations.get(candidate_id)

    async def list_recommendations_by_job(self, job_id: UUID) -> list[HiringRecommendationRecord]:
        async with self._lock:
            return [r for r in self._recommendations.values() if r.analysis_job_id == job_id]

    # ── Maintenance ────────────────────────────────────────────────────────
    async def clear(self) -> None:
        async with self._lock:
            self._files.clear()
            self._jobs.clear()
            self._jd_profiles.clear()
            self._resume_profiles.clear()
            self._semantic_profiles.clear()
            self._rankings.clear()
            self._recommendations.clear()

    @property
    def file_count(self) -> int: return len(self._files)
    @property
    def job_count(self) -> int: return len(self._jobs)
    @property
    def jd_profile_count(self) -> int: return len(self._jd_profiles)
    @property
    def resume_profile_count(self) -> int: return len(self._resume_profiles)
    @property
    def semantic_profile_count(self) -> int: return len(self._semantic_profiles)
    @property
    def ranking_count(self) -> int: return len(self._rankings)
    @property
    def recommendation_count(self) -> int: return len(self._recommendations)


_store: InMemoryStore | None = None

def get_store() -> InMemoryStore:
    global _store
    if _store is None:
        _store = InMemoryStore()
    return _store
