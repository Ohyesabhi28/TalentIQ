# TalentIQ Backend

Enterprise AI Recruiter Platform — REST API built with FastAPI, Pydantic v2, and Python 3.12.

---

## Quick Start

### 1. Prerequisites

| Tool | Minimum version |
|---|---|
| Python | 3.12 |
| PostgreSQL | 15 (Module 2+) |
| Redis | 7 (Module 2+) |

### 2. Create virtual environment

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env and fill in your values (SECRET_KEY at minimum)
```

### 5. Run the development server

```bash
uvicorn app.main:app --reload
```

The API will be available at **http://localhost:8000**

Interactive docs: **http://localhost:8000/docs**

---

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app factory + lifespan
│   ├── config.py            # Pydantic-Settings (env vars)
│   ├── constants.py         # App-wide constants & error codes
│   ├── logging_config.py    # Colour + JSON log formatters
│   ├── exceptions.py        # Custom exception hierarchy + handlers
│   ├── middleware.py        # RequestID + access logging middleware
│   ├── dependencies.py      # FastAPI DI providers
│   ├── api/
│   │   ├── router.py        # Master API router
│   │   └── v1/
│   │       └── health.py    # GET /v1/health, GET /ping
│   ├── models/
│   │   ├── base.py          # AppBaseModel, BaseResponse, PaginatedResponse
│   │   └── common.py        # Shared DTOs (User, Session, UploadedFile, …)
│   └── utils/
│       └── helpers.py       # Pure utility functions
├── tests/
│   └── test_foundation.py   # Smoke tests for Module 1
├── .env.example             # Environment variable template
├── .gitignore
├── pyproject.toml           # Build, lint, test configuration
├── requirements.txt
└── README.md
```

---

## API Overview

| Endpoint | Module | Description |
|---|---|---|
| `GET /v1/health` | 1 | Service health check |
| `GET /ping` | 1 | Liveness probe |
| `POST /v1/auth/login` | 2 | Sign in with email + password |
| `POST /v1/auth/demo-login` | 2 | Instant demo account login |
| `POST /v1/auth/logout` | 2 | Invalidate session |
| `POST /v1/auth/refresh` | 2 | Refresh access token |
| `POST /v1/auth/forgot-password` | 2 | Send password reset email |
| `POST /v1/files/upload` | 3 | Upload JD or resume file |
| `DELETE /v1/files/{id}` | 3 | Remove uploaded file |
| `POST /v1/analysis/jobs` | 4 | Start AI analysis job |
| `GET /v1/analysis/jobs/{id}` | 4 | Poll job status |
| `GET /v1/analysis/jobs/{id}/candidates` | 5 | Ranked candidate list |
| `GET /v1/analysis/jobs/{id}/summary` | 5 | AI recruiter summary |
| `GET /v1/candidates/{id}` | 5 | Single candidate profile |
| `GET /v1/analysis/jobs/{id}/candidates/compare` | 5 | Comparison matrix |
| `GET /v1/analysis/jobs/{id}/skill-gaps` | 6 | Skill gap distribution |
| `POST /v1/training-plans/generate` | 6 | Generate AI training plan |
| `GET /v1/analysis/jobs/{id}/reports/summary` | 7 | Hiring report data |
| `POST /v1/analysis/jobs/{id}/reports/export` | 7 | Export PDF report |
| `GET /v1/notifications` | 8 | List notifications |
| `PATCH /v1/notifications/{id}/read` | 8 | Mark notification read |
| `POST /v1/support/tickets` | 8 | Submit support ticket |

Full contract: see `api_contract.md` in the project root.

---

## Development

### Run tests

```bash
pytest
```

### Lint

```bash
ruff check .
```

### Type check

```bash
mypy app/
```

---

## Module Build Plan

| Module | Status | Scope |
|---|---|---|
| 1 — Foundation | ✅ Complete | App skeleton, middleware, models, health |
| 2 — Auth | ⬜ Pending | JWT login, refresh, logout |
| 3 — Files | ⬜ Pending | Upload, S3 storage, validation |
| 4 — Analysis Engine | ⬜ Pending | Job queue, AI orchestration |
| 5 — Candidates | ⬜ Pending | Ranked results, profiles, comparison |
| 6 — Analytics | ⬜ Pending | Skill gap, training plans |
| 7 — Reports | ⬜ Pending | Hiring report, PDF export |
| 8 — Notifications & Support | ⬜ Pending | Notifications, support tickets |
