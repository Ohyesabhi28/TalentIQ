"""
FastAPI dependency injection providers.
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends, Header

from app.config import Settings, get_settings as _get_settings
from app.logging_config import get_logger

logger = get_logger(__name__)


# ── Settings ───────────────────────────────────────────────────────────────


def get_settings() -> Settings:
    return _get_settings()


SettingsDep = Annotated[Settings, Depends(get_settings)]


# ── Request ID ─────────────────────────────────────────────────────────────


def get_request_id(
    x_request_id: str | None = Header(default=None, alias="X-Request-ID"),
) -> str:
    return x_request_id or str(uuid.uuid4())


RequestIdDep = Annotated[str, Depends(get_request_id)]


# ── Pagination ─────────────────────────────────────────────────────────────


class PaginationParams:
    def __init__(self, page: int = 1, per_page: int = 20) -> None:
        self.page = max(1, page)
        self.per_page = min(max(1, per_page), 100)


PaginationDep = Annotated[PaginationParams, Depends(PaginationParams)]


# ── Store ──────────────────────────────────────────────────────────────────


def get_store():  # type: ignore[return]
    from app.store.memory import get_store as _get_store
    return _get_store()


# ── Services ───────────────────────────────────────────────────────────────


def get_storage_service():
    from app.services.storage import StorageService
    return StorageService()


def get_upload_service(
    storage=Depends(get_storage_service),
    store=Depends(get_store),
):
    from app.services.upload import UploadService
    return UploadService(storage=storage, store=store)


def get_analysis_job_service(store=Depends(get_store)):
    from app.services.analysis_job import AnalysisJobService
    return AnalysisJobService(store=store)


def get_pdf_extractor():
    from app.services.pdf_extractor import PDFExtractorService
    return PDFExtractorService()


def get_gemini_parser(settings: Settings = Depends(get_settings)):
    from app.services.gemini_parser import GeminiJDParser
    return GeminiJDParser(settings=settings)


def get_jd_profile_service(
    store=Depends(get_store),
    extractor=Depends(get_pdf_extractor),
    parser=Depends(get_gemini_parser),
):
    from app.services.jd_profile import JDProfileService
    return JDProfileService(store=store, extractor=extractor, parser=parser)


def get_gemini_resume_parser(settings: Settings = Depends(get_settings)):
    from app.services.gemini_resume_parser import GeminiResumeParser
    return GeminiResumeParser(settings=settings)


def get_resume_profile_service(
    store=Depends(get_store),
    extractor=Depends(get_pdf_extractor),
    parser=Depends(get_gemini_resume_parser),
):
    from app.services.resume_profile import ResumeProfileService
    return ResumeProfileService(store=store, extractor=extractor, parser=parser)


# Singleton instances for ML services
_embedding_service = None
_vector_service = None

def get_embedding_service():
    global _embedding_service
    if _embedding_service is None:
        from app.services.embedding import EmbeddingService
        _embedding_service = EmbeddingService()
    return _embedding_service

def get_vector_service():
    global _vector_service
    if _vector_service is None:
        from app.services.vector import VectorService
        _vector_service = VectorService()
    return _vector_service

def get_semantic_profile_service(
    store=Depends(get_store),
    embedding_service=Depends(get_embedding_service),
    vector_service=Depends(get_vector_service),
):
    from app.services.semantic_profile import SemanticProfileService
    return SemanticProfileService(store=store, embedding_service=embedding_service, vector_service=vector_service)

def get_scoring_service(
    embedding_service=Depends(get_embedding_service),
    vector_service=Depends(get_vector_service),
):
    from app.services.scoring_service import ScoringService
    return ScoringService(embedding_service=embedding_service, vector_service=vector_service)
    
def get_ranking_service(
    store=Depends(get_store),
    scoring_service=Depends(get_scoring_service),
):
    from app.services.ranking_service import RankingService
    return RankingService(store=store, scoring_service=scoring_service)

def get_explainability_service(
    store=Depends(get_store),
    settings: Settings = Depends(get_settings),
):
    from app.services.explainability_service import ExplainabilityService
    return ExplainabilityService(store=store, settings=settings)

def get_analytics_service(
    store=Depends(get_store),
):
    from app.services.analytics_service import AnalyticsService
    return AnalyticsService(store=store)

def get_export_service(
    store=Depends(get_store),
):
    from app.services.export_service import ExportService
    return ExportService(store=store)


UploadServiceDep = Annotated[object, Depends(get_upload_service)]
AnalysisJobServiceDep = Annotated[object, Depends(get_analysis_job_service)]
JDProfileServiceDep = Annotated[object, Depends(get_jd_profile_service)]
ResumeProfileServiceDep = Annotated[object, Depends(get_resume_profile_service)]
SemanticProfileServiceDep = Annotated[object, Depends(get_semantic_profile_service)]
ScoringServiceDep = Annotated[object, Depends(get_scoring_service)]
RankingServiceDep = Annotated[object, Depends(get_ranking_service)]
ExplainabilityServiceDep = Annotated[object, Depends(get_explainability_service)]
AnalyticsServiceDep = Annotated[object, Depends(get_analytics_service)]
ExportServiceDep = Annotated[object, Depends(get_export_service)]


