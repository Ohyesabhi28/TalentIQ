"""
UploadService — file validation, deduplication, and persistence.

Responsibilities:
  1. Validate file type (extension + magic bytes for PDFs).
  2. Validate file size.
  3. Compute MD5 hash and detect duplicates.
  4. Sanitize the filename.
  5. Persist bytes to disk via StorageService.
  6. Save UploadedFileRecord to the store.
  7. Return the public UploadedFileRead DTO.

This service contains NO business logic beyond upload handling.
It does not parse, embed, or score files.
"""

from __future__ import annotations

import hashlib
from uuid import UUID

from fastapi import UploadFile

from app.exceptions import (
    FileCorruptError,
    FileTooLargeError,
    UnsupportedFileTypeError,
)
from app.logging_config import get_logger
from app.models.file import FileTypeAnnotation, UploadedFileRead, UploadedFileRecord
from app.services.storage import StorageService
from app.store.memory import InMemoryStore

logger = get_logger(__name__)

# Maximum allowed file size in bytes (5 MB — matches config + API contract)
_MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

# Allowed MIME types
_ALLOWED_MIME_TYPES: frozenset[str] = frozenset(
    {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
    }
)

# Allowed file extensions (lower-case, with dot)
_ALLOWED_EXTENSIONS: frozenset[str] = frozenset({".pdf", ".docx", ".txt"})

# PDF magic bytes — first 4 bytes of every valid PDF
_PDF_MAGIC = b"%PDF"

# DOCX magic bytes — ZIP PK header
_DOCX_MAGIC = b"PK\x03\x04"


class UploadService:
    """
    Orchestrates the complete file upload workflow.

    Constructor DI allows test doubles for storage and store.
    """

    def __init__(self, storage: StorageService, store: InMemoryStore) -> None:
        self._storage = storage
        self._store = store

    # ── Public API ──────────────────────────────────────────────────────────

    async def upload(
        self,
        upload_file: UploadFile,
        file_type: str,
        max_size_bytes: int = _MAX_FILE_SIZE,
    ) -> UploadedFileRead:
        """
        Validate, deduplicate, persist, and register an uploaded file.

        Args:
            upload_file:    FastAPI UploadFile from the multipart request.
            file_type:      "job_description" or "resume" (validated upstream).
            max_size_bytes: Override for tests (defaults to 5 MB).

        Returns:
            Public UploadedFileRead DTO.

        Raises:
            UnsupportedFileTypeError: Extension or MIME type not allowed.
            FileTooLargeError:        Content exceeds max_size_bytes.
            FileCorruptError:         Magic bytes don't match the extension.
        """
        original_name = upload_file.filename or "upload"
        content = await upload_file.read()

        logger.info(
            "Processing upload: %s (%d bytes) as %s",
            original_name,
            len(content),
            file_type,
        )

        # ── Validation pipeline ─────────────────────────────────────────────
        self._validate_extension(original_name)
        self._validate_size(content, max_size_bytes)
        self._validate_magic_bytes(content, original_name)

        # ── Deduplication ───────────────────────────────────────────────────
        md5 = _compute_md5(content)
        existing = await self._store.find_files_by_md5(md5)
        if existing:
            logger.info(
                "Duplicate file detected (md5=%s). Returning existing record %s.",
                md5,
                existing[0].id,
            )
            return UploadedFileRead.from_record(existing[0])

        # ── Persist ─────────────────────────────────────────────────────────
        safe_name = self._storage.sanitize_filename(original_name)
        record = UploadedFileRecord(
            name=safe_name,
            original_name=original_name,
            size=len(content),
            mime_type=_resolve_mime(original_name),
            file_type=file_type,  # type: ignore[arg-type]
            local_path="",        # filled in after path is computed
            md5_hash=md5,
        )

        path = self._storage.build_path(record.id, safe_name)
        record = record.model_copy(update={"local_path": str(path.resolve())})

        await self._storage.save(path, content)
        await self._store.save_file(record)

        logger.info(
            "File uploaded successfully: id=%s name=%s size=%d",
            record.id,
            record.name,
            record.size,
        )
        return UploadedFileRead.from_record(record)

    async def delete(self, file_id: UUID) -> None:
        """
        Remove a file record from the store and its bytes from disk.

        Args:
            file_id: UUID of the UploadedFileRecord.

        Raises:
            app.exceptions.FileNotFoundError: Record does not exist.
        """
        from app.exceptions import FileNotFoundError as AppFileNotFoundError

        record = await self._store.get_file(file_id)
        if record is None:
            raise AppFileNotFoundError()

        # Delete physical file first, then the record
        await self._storage.delete(path=__import__("pathlib").Path(record.local_path))
        await self._store.delete_file(file_id)

        logger.info("File deleted: id=%s name=%s", file_id, record.name)

    # ── Private Validators ──────────────────────────────────────────────────

    @staticmethod
    def _validate_extension(filename: str) -> None:
        """Reject files whose extension is not in the allow-list."""
        from pathlib import Path as _Path

        ext = _Path(filename).suffix.lower()
        if ext not in _ALLOWED_EXTENSIONS:
            raise UnsupportedFileTypeError(
                f"File type '{ext}' is not allowed. "
                f"Supported: {', '.join(sorted(_ALLOWED_EXTENSIONS))}"
            )

    @staticmethod
    def _validate_size(content: bytes, max_bytes: int) -> None:
        """Reject files that exceed the configured size limit."""
        if len(content) > max_bytes:
            limit_mb = max_bytes / (1024 * 1024)
            raise FileTooLargeError(
                f"File size {len(content):,} bytes exceeds the {limit_mb:.0f} MB limit."
            )

    @staticmethod
    def _validate_magic_bytes(content: bytes, filename: str) -> None:
        """
        Verify the actual file content matches the claimed extension.

        Prevents MIME-type spoofing (e.g. a .pdf file that is actually
        an executable).
        """
        from pathlib import Path as _Path

        ext = _Path(filename).suffix.lower()
        if not content:
            raise FileCorruptError("Uploaded file is empty.")

        if ext == ".pdf" and not content.startswith(_PDF_MAGIC):
            raise FileCorruptError(
                "File does not appear to be a valid PDF (magic bytes mismatch)."
            )

        if ext == ".docx" and not content.startswith(_DOCX_MAGIC):
            raise FileCorruptError(
                "File does not appear to be a valid DOCX (magic bytes mismatch)."
            )
        # .txt files have no magic bytes — no extra check needed.


# ── Helpers ────────────────────────────────────────────────────────────────


def _compute_md5(content: bytes) -> str:
    """Return the hex MD5 digest of the given bytes."""
    return hashlib.md5(content, usedforsecurity=False).hexdigest()


def _resolve_mime(filename: str) -> str:
    """Map a filename extension to its MIME type."""
    from pathlib import Path as _Path

    ext = _Path(filename).suffix.lower()
    return {
        ".pdf":  "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".txt":  "text/plain",
    }.get(ext, "application/octet-stream")
