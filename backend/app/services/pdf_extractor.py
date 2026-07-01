"""
PDF Extractor Service.

Uses PyMuPDF to extract readable text from PDF documents.
Handles standard formatting and produces clean text output.
"""

from __future__ import annotations

from pathlib import Path

import pymupdf  # type: ignore[import-untyped]

from app.exceptions import AppError
from app.logging_config import get_logger

logger = get_logger(__name__)


class PDFExtractorService:
    """
    Extracts raw text from PDF files.
    """

    def extract_text(self, file_path: str) -> str:
        """
        Extract text from a PDF file located at file_path.

        Args:
            file_path: Absolute path to the PDF file on disk.

        Returns:
            Extracted text as a single string.

        Raises:
            AppError: If the file cannot be opened or parsed.
        """
        path = Path(file_path)
        if not path.exists():
            raise AppError(
                error_code="FILE_NOT_FOUND",
                message=f"PDF file not found at path: {file_path}",
                status_code=404,
            )

        logger.info("Extracting text from PDF: %s", file_path)

        text_blocks = []
        try:
            with pymupdf.open(file_path) as doc:
                for page in doc:
                    text_blocks.append(page.get_text())
        except Exception as exc:
            logger.error("Failed to parse PDF %s: %s", file_path, exc)
            raise AppError(
                error_code="PDF_PARSING_ERROR",
                message="Failed to parse the PDF document.",
                status_code=422,
            ) from exc

        raw_text = "\n".join(text_blocks).strip()
        if not raw_text:
            raise AppError(
                error_code="PDF_EMPTY",
                message="PDF document contains no extractable text.",
                status_code=422,
            )

        logger.debug("Extracted %d characters from PDF.", len(raw_text))
        return raw_text
