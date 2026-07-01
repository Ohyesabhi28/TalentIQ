"""
Reusable utility functions used across the application.

Rules:
  - Pure functions only — no side effects, no I/O.
  - Each function is independently testable.
  - Import from here, not from random internal modules.
"""

from __future__ import annotations

import hashlib
import math
import mimetypes
import os
import random
import string
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import UUID

from app.constants import (
    ALLOWED_EXTENSIONS,
    MATCH_TYPE_AVERAGE,
    MATCH_TYPE_GOOD,
    MATCH_TYPE_STRONG,
    SCORE_THRESHOLD_GOOD,
    SCORE_THRESHOLD_STRONG,
    TICKET_NUMBER_PREFIX,
)


# ── Time ───────────────────────────────────────────────────────────────────


def utcnow() -> datetime:
    """Return the current UTC time as a timezone-aware datetime object."""
    return datetime.now(tz=timezone.utc)


def format_iso(dt: datetime) -> str:
    """Format a datetime to an ISO 8601 string with timezone offset."""
    return dt.isoformat()


# ── Identifiers ────────────────────────────────────────────────────────────


def generate_ticket_number() -> str:
    """
    Generate a unique support ticket number in the format TKT-XXXXX.

    Uses 5 random digits, matching the frontend's display expectation.
    """
    digits = "".join(random.choices(string.digits, k=5))
    return f"{TICKET_NUMBER_PREFIX}{digits}"


def short_id(uuid: UUID) -> str:
    """Return the first 8 hex characters of a UUID for compact display."""
    return str(uuid).replace("-", "")[:8]


# ── Files ──────────────────────────────────────────────────────────────────


def get_file_extension(filename: str) -> str:
    """
    Extract and lowercase the file extension from a filename.

    Args:
        filename: e.g. "resume_sarah.PDF"

    Returns:
        Lowercased extension including the dot, e.g. ".pdf"
    """
    return Path(filename).suffix.lower()


def is_allowed_extension(filename: str) -> bool:
    """Return True if the file extension is in the allow-list."""
    return get_file_extension(filename) in ALLOWED_EXTENSIONS


def guess_mime_type(filename: str) -> str:
    """
    Guess the MIME type from a filename.

    Falls back to "application/octet-stream" if unknown.
    """
    mime, _ = mimetypes.guess_type(filename)
    return mime or "application/octet-stream"


def human_readable_size(size_bytes: int) -> str:
    """
    Convert a byte count to a human-readable string.

    Examples:
        204800  → "200.0 KB"
        5242880 → "5.0 MB"
    """
    if size_bytes == 0:
        return "0 B"
    units = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    i = min(i, len(units) - 1)
    p = math.pow(1024, i)
    return f"{size_bytes / p:.1f} {units[i]}"


def compute_md5(content: bytes) -> str:
    """Compute an MD5 hex digest for content integrity checks."""
    return hashlib.md5(content).hexdigest()


# ── Candidate Scoring ──────────────────────────────────────────────────────


def score_to_match_type(score: int) -> str:
    """
    Convert a numeric AI match score (0–100) to a human-readable match type.

    Thresholds match the API contract:
      ≥ 90 → Strong Fit
      ≥ 80 → Good Fit
      <  80 → Average Fit
    """
    if score >= SCORE_THRESHOLD_STRONG:
        return MATCH_TYPE_STRONG
    if score >= SCORE_THRESHOLD_GOOD:
        return MATCH_TYPE_GOOD
    return MATCH_TYPE_AVERAGE


def compute_fit_ratios(scores: list[int]) -> dict[str, int]:
    """
    Compute the count of Strong / Good / Average candidates.

    Args:
        scores: List of integer match scores (0–100).

    Returns:
        Dict with keys "strong", "good", "average".
    """
    strong = sum(1 for s in scores if s >= SCORE_THRESHOLD_STRONG)
    good = sum(1 for s in scores if SCORE_THRESHOLD_GOOD <= s < SCORE_THRESHOLD_STRONG)
    average = sum(1 for s in scores if s < SCORE_THRESHOLD_GOOD)
    return {"strong": strong, "good": good, "average": average}


# ── Pagination ─────────────────────────────────────────────────────────────


def paginate(
    items: list[Any],
    page: int,
    per_page: int,
) -> tuple[list[Any], int]:
    """
    Slice a list into a single page.

    Args:
        items:    Full list of items (already filtered/sorted).
        page:     1-indexed page number.
        per_page: Number of items per page.

    Returns:
        A tuple of (page_items, total_count).
    """
    total = len(items)
    start = (page - 1) * per_page
    end = start + per_page
    return items[start:end], total


# ── Text ───────────────────────────────────────────────────────────────────


def slugify(text: str) -> str:
    """
    Convert arbitrary text to a URL-safe slug.

    Examples:
        "Senior Frontend Engineer" → "senior-frontend-engineer"
    """
    # Normalise unicode characters
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    # Replace non-alphanumeric with hyphens
    import re
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def truncate(text: str, max_length: int, suffix: str = "…") -> str:
    """
    Truncate a string to at most max_length characters, appending a suffix.

    Args:
        text:       The input string.
        max_length: Maximum total length including the suffix.
        suffix:     Appended when the string is truncated (default "…").
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def name_to_initials(name: str, max_chars: int = 2) -> str:
    """
    Convert a full name to uppercase initials.

    Examples:
        "Alex Carter" → "AC"
        "Sarah J."    → "SJ"
    """
    parts = name.strip().split()
    return "".join(p[0].upper() for p in parts if p)[:max_chars]


# ── Collections ────────────────────────────────────────────────────────────


def chunk(lst: list[Any], size: int) -> list[list[Any]]:
    """Split a list into sublists of at most *size* items."""
    return [lst[i : i + size] for i in range(0, len(lst), size)]


def flatten(nested: list[list[Any]]) -> list[Any]:
    """Flatten one level of nesting in a list of lists."""
    return [item for sublist in nested for item in sublist]
