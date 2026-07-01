"""
File Upload API — POST /v1/files/upload, DELETE /v1/files/{file_id}

Accepts multipart/form-data with:
  - file:      binary file content
  - file_type: "job_description" | "resume"

Returns the standard BaseResponse[UploadedFileRead] envelope.
"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Form, UploadFile, status
from fastapi.responses import Response

from app.dependencies import get_analysis_job_service, get_upload_service
from app.logging_config import get_logger
from app.models.base import BaseResponse
from app.models.file import FileTypeAnnotation, UploadedFileRead
from app.services.upload import UploadService

logger = get_logger(__name__)

router = APIRouter(prefix="/files", tags=["Files"])


# ── POST /files/upload ─────────────────────────────────────────────────────


@router.post(
    "/upload",
    response_model=BaseResponse[UploadedFileRead],
    status_code=status.HTTP_201_CREATED,
    summary="Upload a file",
    description=(
        "Upload a Job Description or Resume file (PDF, DOCX, or TXT, max 5 MB). "
        "Duplicate files are detected by MD5 hash and the existing record is returned. "
        "Set ``file_type`` to ``job_description`` or ``resume``."
    ),
    responses={
        201: {"description": "File uploaded or duplicate detected."},
        400: {"description": "Unsupported file type or empty file."},
        413: {"description": "File exceeds the 5 MB size limit."},
        422: {"description": "File content is corrupt or does not match extension."},
    },
)
async def upload_file(
    file: UploadFile,
    file_type: Annotated[
        str,
        Form(
            description=(
                "Purpose of the uploaded file. "
                "Must be ``job_description`` or ``resume``."
            ),
        ),
    ],
    service: UploadService = Depends(get_upload_service),
) -> BaseResponse[UploadedFileRead]:
    """
    Upload a single file.

    - Validates extension, size, and magic bytes.
    - Detects duplicates by MD5 hash.
    - Persists to local disk under ``uploads/{year-month}/{uuid}/``.
    - Returns the file record immediately (synchronous — no background task).
    """
    _validate_file_type_param(file_type)

    result = await service.upload(upload_file=file, file_type=file_type)

    logger.info("Upload endpoint: returned file id=%s", result.id)
    return BaseResponse(data=result)


# ── DELETE /files/{file_id} ────────────────────────────────────────────────


@router.delete(
    "/{file_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an uploaded file",
    description=(
        "Remove an uploaded file record from the store and its bytes from disk. "
        "Returns 204 No Content on success."
    ),
    responses={
        204: {"description": "File deleted."},
        404: {"description": "File not found."},
    },
)
async def delete_file(
    file_id: UUID,
    service: UploadService = Depends(get_upload_service),
) -> Response:
    """
    Delete a previously uploaded file by its UUID.

    Raises 404 if the file does not exist in the store.
    """
    await service.delete(file_id=file_id)
    logger.info("Delete endpoint: file id=%s removed", file_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ── Helpers ────────────────────────────────────────────────────────────────


def _validate_file_type_param(file_type: str) -> None:
    """
    Reject invalid ``file_type`` form values early with a clear 400 error.

    FastAPI form validation doesn't support Literal types for Form() fields,
    so we enforce the constraint manually here.
    """
    from app.exceptions import AppError
    from fastapi import status as http_status

    if file_type not in FileTypeAnnotation.VALUES:
        raise AppError(
            error_code="VALIDATION_ERROR",
            message=(
                f"Invalid file_type '{file_type}'. "
                f"Allowed values: {', '.join(sorted(FileTypeAnnotation.VALUES))}"
            ),
            status_code=http_status.HTTP_400_BAD_REQUEST,
        )
