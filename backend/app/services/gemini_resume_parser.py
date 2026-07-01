"""
Gemini Resume Parser.

Uses the Gemini SDK's Structured Outputs feature (passing a Pydantic schema)
to extract structured data from raw Resume text.
"""

from __future__ import annotations

import google.generativeai as genai
from pydantic import ValidationError

from app.config import Settings
from app.exceptions import AppError
from app.logging_config import get_logger
from app.models.resume import ResumeProfileBase

logger = get_logger(__name__)


class GeminiResumeParser:
    """
    Parses raw Resume text into a structured ResumeProfileBase object using Gemini.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        if not self.settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY is not set. API calls will fail.")
        
        genai.configure(api_key=self.settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            model_name=self.settings.GEMINI_MODEL,
            system_instruction=(
                "You are an expert technical recruiter and AI assistant. "
                "Your task is to extract structured information from the provided candidate resume text. "
                "Output strictly valid JSON matching the requested schema. "
                "Do not hallucinate data. If a field or category is not mentioned in the text, omit it or use an empty array/null."
            )
        )

    async def parse_resume(self, raw_text: str) -> ResumeProfileBase:
        """
        Extract structured data from the raw resume text.

        Args:
            raw_text: The full text of the resume.

        Returns:
            A validated ResumeProfileBase object.

        Raises:
            AppError: If the Gemini API fails or returns malformed data.
        """
        logger.info("Sending Resume text to Gemini for structured extraction.")
        try:
            # Generate content using Structured Outputs
            response = await self.model.generate_content_async(
                raw_text,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=ResumeProfileBase,
                    temperature=0.1,  # Low temperature for extraction tasks
                ),
            )
            
            if not response.text:
                raise ValueError("Received empty response from Gemini.")

            # Validate the JSON string against our Pydantic schema
            parsed_data = ResumeProfileBase.model_validate_json(response.text)
            logger.info("Successfully parsed Resume profile for: %s", parsed_data.personal_information.name)
            return parsed_data

        except ValidationError as exc:
            logger.error("Gemini returned invalid resume schema: %s", exc)
            raise AppError(
                error_code="AI_VALIDATION_ERROR",
                message="The AI returned malformed data that could not be parsed.",
                status_code=502,
            ) from exc
        except Exception as exc:
            logger.exception("Error calling Gemini API for resume extraction: %s", exc)
            raise AppError(
                error_code="AI_SERVICE_UNAVAILABLE",
                message="The AI extraction service is currently unavailable.",
                status_code=503,
            ) from exc
