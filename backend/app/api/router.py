"""
Master API router.

This module assembles all version-prefixed routers into a single
APIRouter that is mounted onto the FastAPI app in main.py.

Convention:
  - All v1 routers are imported here and included with the /v1 prefix.
  - When a new resource module is added (e.g. auth, files, analysis),
    import its router here and add an app.include_router() call.
"""

from fastapi import APIRouter

from app.api.v1 import health as health_module
from app.api.v1 import files as files_module
from app.api.v1 import analysis as analysis_module
from app.api.v1 import candidates as candidates_module

# Root router — all sub-routers are included here
api_router = APIRouter()

# ── v1 routes ──────────────────────────────────────────────────────────────
# Health / system
api_router.include_router(health_module.router, prefix="/v1")
api_router.include_router(files_module.router, prefix="/v1")
api_router.include_router(analysis_module.router, prefix="/v1")
api_router.include_router(candidates_module.router, prefix="/v1")
