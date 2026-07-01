"""
StorageService — local filesystem abstraction for uploaded files.

Responsibilities:
  - Determine safe storage paths for uploaded files.
  - Write raw bytes to disk.
  - Delete files from disk.
  - Create required directory trees.

Path layout:
    {UPLOAD_ROOT}/{year}-{month}/{file_id}/{safe_filename}

Example:
    uploads/2026-06/a1b2c3d4-…-ef56/senior_frontend_jd.pdf

This keeps files isolated by UUID so filename collisions are impossible,
and organises them by month for easy archival.
"""

from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from app.logging_config import get_logger

logger = get_logger(__name__)

# Root directory for all uploaded files (relative to where the server runs)
_UPLOAD_ROOT = Path("uploads")


class StorageService:
    """
    Manages local filesystem storage for uploaded files.

    Inject this service into UploadService via constructor DI.
    Replace it with an S3StorageService in production without touching
    any other service or route.
    """

    def __init__(self, upload_root: Path | None = None) -> None:
        self._root = upload_root or _UPLOAD_ROOT

    # ── Public API ──────────────────────────────────────────────────────────

    def build_path(self, file_id: UUID, safe_filename: str) -> Path:
        """
        Compute the full filesystem path for a file.

        Args:
            file_id:       UUID of the UploadedFileRecord.
            safe_filename: Already-sanitized filename (see sanitize_filename).

        Returns:
            Absolute Path where the file should be written.
        """
        month_dir = datetime.now(tz=timezone.utc).strftime("%Y-%m")
        return self._root / month_dir / str(file_id) / safe_filename

    async def save(self, path: Path, content: bytes) -> None:
        """
        Write file content to disk, creating any missing parent directories.

        Args:
            path:    Target path returned by build_path().
            content: Raw file bytes.

        Raises:
            OSError: If the write fails (e.g. disk full).
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        logger.debug("Saved file to disk: %s (%d bytes)", path, len(content))

    async def delete(self, path: Path) -> bool:
        """
        Remove a file from disk.

        Args:
            path: Absolute filesystem path.

        Returns:
            True  — file existed and was removed.
            False — file was not found (already deleted or never written).
        """
        try:
            path.unlink(missing_ok=True)
            logger.debug("Deleted file from disk: %s", path)
            return True
        except OSError as exc:
            logger.warning("Could not delete file %s: %s", path, exc)
            return False

    # ── Utilities ───────────────────────────────────────────────────────────

    @staticmethod
    def sanitize_filename(name: str) -> str:
        """
        Produce a filesystem-safe filename.

        Rules applied (in order):
          1. Strip any directory component (prevent path traversal).
          2. Replace sequences of non-alphanumeric characters with ``_``.
          3. Normalise repeated underscores.
          4. Truncate to 200 characters.
          5. Always preserve the ``.pdf`` suffix.

        Args:
            name: Raw filename from the upload request.

        Returns:
            Safe filename suitable for use in a filesystem path.

        Examples:
            "My Resume (v2).pdf"  →  "My_Resume_v2.pdf"
            "../../etc/passwd"    →  "etc_passwd"
            "résumé.PDF"          →  "résumé.pdf"
        """
        # 1. Strip directory components (defence against path traversal)
        name = Path(name).name

        # 2. Separate stem and extension
        p = Path(name)
        stem = p.stem
        suffix = p.suffix.lower()

        # 3. Replace unsafe characters in the stem
        stem = re.sub(r"[^\w\-. ]", "_", stem)
        stem = re.sub(r"_+", "_", stem).strip("_").strip()

        # 4. Truncate stem (leave room for extension)
        max_stem = 200 - len(suffix)
        stem = stem[:max_stem] if stem else "file"

        return f"{stem}{suffix}"

    def ensure_upload_root(self) -> None:
        """Create the upload root directory if it does not exist."""
        self._root.mkdir(parents=True, exist_ok=True)
        logger.debug("Upload root ensured: %s", self._root.resolve())
