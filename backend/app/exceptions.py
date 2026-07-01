"""
Custom application exceptions and FastAPI exception handlers.

Convention:
  - All domain exceptions inherit from AppError.
  - Each exception carries an error_code (matching the API contract constants)
    and an HTTP status_code.
  - The global exception handlers convert these into the standard error envelope:
      { "error": { "code": str, "message": str, "details"?: obj } }
"""

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.logging_config import get_logger

logger = get_logger(__name__)


# ── Base Exception ─────────────────────────────────────────────────────────


class AppError(Exception):
    """
    Base class for all application-level errors.

    Attributes:
        error_code:  Machine-readable string from constants (e.g. "FILE_NOT_FOUND").
        message:     Human-readable description sent to the client.
        status_code: HTTP status code that this error maps to.
        details:     Optional extra context (not sent in production; logged only).
    """

    def __init__(
        self,
        error_code: str,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


# ── Auth Errors ────────────────────────────────────────────────────────────


class InvalidCredentialsError(AppError):
    def __init__(self, message: str = "Invalid email or password.") -> None:
        super().__init__(
            error_code="INVALID_CREDENTIALS",
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class TokenExpiredError(AppError):
    def __init__(self, message: str = "Access token has expired.") -> None:
        super().__init__(
            error_code="TOKEN_EXPIRED",
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class RefreshTokenExpiredError(AppError):
    def __init__(self, message: str = "Refresh token has expired. Please log in again.") -> None:
        super().__init__(
            error_code="REFRESH_TOKEN_EXPIRED",
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class AlreadyLoggedOutError(AppError):
    def __init__(self, message: str = "Session has already been terminated.") -> None:
        super().__init__(
            error_code="ALREADY_LOGGED_OUT",
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class UserNotFoundError(AppError):
    def __init__(self, message: str = "No account found for that email.") -> None:
        super().__init__(
            error_code="USER_NOT_FOUND",
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class RateLimitedError(AppError):
    def __init__(self, message: str = "Too many requests. Please try again later.") -> None:
        super().__init__(
            error_code="RATE_LIMITED",
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )


class ForbiddenError(AppError):
    def __init__(self, message: str = "You don't have access to this resource.") -> None:
        super().__init__(
            error_code="FORBIDDEN",
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
        )


# ── File Errors ────────────────────────────────────────────────────────────


class UnsupportedFileTypeError(AppError):
    def __init__(self, message: str = "Only PDF, DOCX, and TXT files are supported.") -> None:
        super().__init__(
            error_code="UNSUPPORTED_FILE_TYPE",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class FileTooLargeError(AppError):
    def __init__(self, message: str = "File exceeds the 5 MB size limit.") -> None:
        super().__init__(
            error_code="FILE_TOO_LARGE",
            message=message,
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        )


class FileCorruptError(AppError):
    def __init__(self, message: str = "File could not be read. Please try another.") -> None:
        super().__init__(
            error_code="FILE_CORRUPT",
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class StorageFullError(AppError):
    def __init__(self, message: str = "Storage limit reached. Remove files before uploading.") -> None:
        super().__init__(
            error_code="STORAGE_FULL",
            message=message,
            status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
        )


class FileNotFoundError(AppError):  # noqa: A001 (shadows built-in intentionally)
    def __init__(self, message: str = "File not found.") -> None:
        super().__init__(
            error_code="FILE_NOT_FOUND",
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
        )


# ── Analysis Errors ────────────────────────────────────────────────────────


class AnalysisJobNotFoundError(AppError):
    def __init__(self, message: str = "Analysis session not found or has expired.") -> None:
        super().__init__(
            error_code="JOB_NOT_FOUND",
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class AnalysisFailedError(AppError):
    def __init__(self, message: str = "Analysis failed. Please try again.") -> None:
        super().__init__(
            error_code="ANALYSIS_FAILED",
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class JDParseFailedError(AppError):
    def __init__(self, message: str = "Could not parse the job description. Try a different file.") -> None:
        super().__init__(
            error_code="JD_PARSE_FAILED",
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class AIUnavailableError(AppError):
    def __init__(self, message: str = "AI service is temporarily unavailable. Please try again.") -> None:
        super().__init__(
            error_code="AI_UNAVAILABLE",
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class CandidateNotFoundError(AppError):
    def __init__(self, message: str = "Candidate not found.") -> None:
        super().__init__(
            error_code="CANDIDATE_NOT_FOUND",
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class InsufficientCandidatesError(AppError):
    def __init__(self, message: str = "Select at least 2 candidates to compare.") -> None:
        super().__init__(
            error_code="INSUFFICIENT_CANDIDATES",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


# ── Report Errors ──────────────────────────────────────────────────────────


class ExportFailedError(AppError):
    def __init__(self, message: str = "PDF export failed. Try printing instead.") -> None:
        super().__init__(
            error_code="EXPORT_FAILED",
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class ReportNotFoundError(AppError):
    def __init__(self, message: str = "Report not found. Please re-run the analysis.") -> None:
        super().__init__(
            error_code="REPORT_NOT_FOUND",
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
        )


# ── Support Errors ─────────────────────────────────────────────────────────


class SupportUnavailableError(AppError):
    def __init__(self, message: str = "Support system temporarily unavailable.") -> None:
        super().__init__(
            error_code="SUPPORT_UNAVAILABLE",
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


# ── Exception Handlers ─────────────────────────────────────────────────────


def _error_response(
    status_code: int,
    error_code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    """Build the standard error envelope defined in the API contract."""
    content: dict[str, Any] = {
        "error": {
            "code": error_code,
            "message": message,
        }
    }
    if details:
        content["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=content)


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Handle all AppError subclasses uniformly."""
    logger.warning(
        "Application error: %s — %s",
        exc.error_code,
        exc.message,
        extra={"path": str(request.url), "details": exc.details},
    )
    return _error_response(
        status_code=exc.status_code,
        error_code=exc.error_code,
        message=exc.message,
    )


async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Convert Pydantic / FastAPI validation errors into the API contract envelope."""
    field_errors: list[dict[str, Any]] = []
    for error in exc.errors():
        field_errors.append(
            {
                "field": " → ".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
        )

    logger.debug(
        "Request validation failed",
        extra={"path": str(request.url), "errors": field_errors},
    )
    return _error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        error_code="VALIDATION_ERROR",
        message="Request validation failed.",
        details={"fields": field_errors},
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for unexpected exceptions. Hides internals from the client."""
    logger.exception(
        "Unhandled exception on %s %s",
        request.method,
        str(request.url),
    )
    return _error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code="INTERNAL_ERROR",
        message="An unexpected error occurred. Please try again later.",
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Attach all exception handlers to the FastAPI application instance.

    Call this during app factory construction in main.py.
    """
    app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_exception_handler)  # type: ignore[arg-type]
