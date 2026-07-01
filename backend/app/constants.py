"""
Application-wide constants.

Rules:
  - No logic here, only primitive values.
  - Import from here instead of scattering magic strings across the codebase.
"""

# ── API ────────────────────────────────────────────────────────────────────
API_VERSION = "v1"
API_V1_PREFIX = "/v1"

# ── HTTP Status Codes (semantic aliases) ───────────────────────────────────
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_202_ACCEPTED = 202
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_401_UNAUTHORIZED = 401
HTTP_403_FORBIDDEN = 403
HTTP_404_NOT_FOUND = 404
HTTP_409_CONFLICT = 409
HTTP_413_REQUEST_ENTITY_TOO_LARGE = 413
HTTP_422_UNPROCESSABLE_ENTITY = 422
HTTP_429_TOO_MANY_REQUESTS = 429
HTTP_500_INTERNAL_SERVER_ERROR = 500
HTTP_503_SERVICE_UNAVAILABLE = 503
HTTP_507_INSUFFICIENT_STORAGE = 507

# ── Application Error Codes (match the API contract) ──────────────────────
# Auth
ERR_INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
ERR_TOKEN_EXPIRED = "TOKEN_EXPIRED"
ERR_REFRESH_TOKEN_EXPIRED = "REFRESH_TOKEN_EXPIRED"
ERR_ALREADY_LOGGED_OUT = "ALREADY_LOGGED_OUT"
ERR_USER_NOT_FOUND = "USER_NOT_FOUND"
ERR_RATE_LIMITED = "RATE_LIMITED"
ERR_DEMO_UNAVAILABLE = "DEMO_UNAVAILABLE"
ERR_VALIDATION_ERROR = "VALIDATION_ERROR"

# Files
ERR_UNSUPPORTED_FILE_TYPE = "UNSUPPORTED_FILE_TYPE"
ERR_FILE_TOO_LARGE = "FILE_TOO_LARGE"
ERR_FILE_CORRUPT = "FILE_CORRUPT"
ERR_STORAGE_FULL = "STORAGE_FULL"
ERR_FILE_NOT_FOUND = "FILE_NOT_FOUND"

# Analysis
ERR_MISSING_JD = "MISSING_JD"
ERR_NO_RESUMES = "NO_RESUMES"
ERR_JD_PARSE_FAILED = "JD_PARSE_FAILED"
ERR_AI_UNAVAILABLE = "AI_UNAVAILABLE"
ERR_ANALYSIS_FAILED = "ANALYSIS_FAILED"
ERR_JOB_NOT_FOUND = "JOB_NOT_FOUND"
ERR_INSUFFICIENT_CANDIDATES = "INSUFFICIENT_CANDIDATES"
ERR_CANDIDATE_NOT_FOUND = "CANDIDATE_NOT_FOUND"

# Reports / Export
ERR_EXPORT_FAILED = "EXPORT_FAILED"
ERR_REPORT_NOT_FOUND = "REPORT_NOT_FOUND"

# Support
ERR_SUPPORT_UNAVAILABLE = "SUPPORT_UNAVAILABLE"

# Generic
ERR_FORBIDDEN = "FORBIDDEN"
ERR_INTERNAL_ERROR = "INTERNAL_ERROR"

# ── File Upload ────────────────────────────────────────────────────────────
ALLOWED_EXTENSIONS: frozenset[str] = frozenset({".pdf", ".docx", ".txt"})

MIME_TO_EXTENSION: dict[str, str] = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "text/plain": ".txt",
}

FILE_TYPE_JOB_DESCRIPTION = "job_description"
FILE_TYPE_RESUME = "resume"

# ── Analysis Job ───────────────────────────────────────────────────────────
JOB_STATUS_QUEUED = "queued"
JOB_STATUS_PROCESSING = "processing"
JOB_STATUS_COMPLETED = "completed"
JOB_STATUS_FAILED = "failed"

# Analysis pipeline stage labels (must match the frontend's copy)
ANALYSIS_STAGES = [
    {"id": 1, "label": "Extracting semantic layers from job description..."},
    {"id": 2, "label": "Parsing candidate resumes..."},
    {"id": 3, "label": "Performing cross-signal skill gap matching..."},
    {"id": 4, "label": "Generating recruiter insights..."},
]

STAGE_STATUS_PENDING = "pending"
STAGE_STATUS_LOADING = "loading"
STAGE_STATUS_DONE = "done"
STAGE_STATUS_ERROR = "error"

# ── Candidate Match ────────────────────────────────────────────────────────
MATCH_TYPE_STRONG = "Strong Fit"
MATCH_TYPE_GOOD = "Good Fit"
MATCH_TYPE_AVERAGE = "Average Fit"

SCORE_THRESHOLD_STRONG = 90
SCORE_THRESHOLD_GOOD = 80

SKILL_STATUS_MATCH = "match"
SKILL_STATUS_GAP = "gap"

# ── Token ──────────────────────────────────────────────────────────────────
TOKEN_TYPE_BEARER = "Bearer"
TOKEN_SUBJECT_CLAIM = "sub"
TOKEN_EXPIRY_CLAIM = "exp"
TOKEN_TYPE_CLAIM = "type"
TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"

# ── Pagination ─────────────────────────────────────────────────────────────
DEFAULT_PAGE = 1
DEFAULT_PER_PAGE = 20
MAX_PER_PAGE = 100

# ── Sorting ────────────────────────────────────────────────────────────────
SORT_SCORE_DESC = "score_desc"
SORT_SCORE_ASC = "score_asc"

# ── Notification Types ─────────────────────────────────────────────────────
NOTIF_TYPE_ANALYSIS_COMPLETE = "analysis_complete"
NOTIF_TYPE_TICKET_UPDATED = "ticket_updated"
NOTIF_TYPE_SYSTEM = "system"

# ── Support Ticket Statuses ────────────────────────────────────────────────
TICKET_STATUS_OPEN = "open"
TICKET_STATUS_IN_PROGRESS = "in_progress"
TICKET_STATUS_RESOLVED = "resolved"

# ── User Roles ─────────────────────────────────────────────────────────────
ROLE_RECRUITER = "recruiter"
ROLE_ADMIN = "admin"
ROLE_VIEWER = "viewer"

# ── Report Export Formats ──────────────────────────────────────────────────
EXPORT_FORMAT_PDF = "pdf"

# ── Health Check ───────────────────────────────────────────────────────────
HEALTH_STATUS_HEALTHY = "healthy"
HEALTH_STATUS_DEGRADED = "degraded"
HEALTH_STATUS_UNHEALTHY = "unhealthy"

# ── Misc ───────────────────────────────────────────────────────────────────
TICKET_NUMBER_PREFIX = "TKT-"
ANALYSIS_POLL_INTERVAL_SECONDS = 2
SEARCH_DEBOUNCE_HINT_MS = 300  # documented for frontend consumers
