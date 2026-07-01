"""
Job Description Profile domain models.

Provides the schema for structuring raw Job Description text via the Gemini AI.
These models define the shape of the data used for matching candidate resumes.
"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.models.base import AppBaseModel, IdentifiableMixin


class JDProfileBase(AppBaseModel):
    """
    Core Job Description fields extracted by the AI engine.

    Used directly as the Pydantic schema passed to the Gemini API
    to enforce structured JSON output.
    """

    job_title: str = Field(description="The primary title of the role (e.g. Senior Backend Engineer)")
    industry: str | None = Field(default=None, description="The industry or sector (e.g. Fintech, Healthcare)")
    seniority: str | None = Field(default=None, description="The seniority level (e.g. Junior, Mid, Senior, Lead)")
    required_skills: list[str] = Field(default_factory=list, description="Must-have technical or domain skills")
    preferred_skills: list[str] = Field(default_factory=list, description="Nice-to-have or bonus skills")
    education: str | None = Field(default=None, description="Required education level (e.g. Bachelor's Degree in Computer Science)")
    experience: str | None = Field(default=None, description="Minimum years of experience required")
    certifications: list[str] = Field(default_factory=list, description="Required or preferred certifications (e.g. AWS Certified Solutions Architect)")
    responsibilities: list[str] = Field(default_factory=list, description="Key duties and responsibilities of the role")
    soft_skills: list[str] = Field(default_factory=list, description="Required interpersonal or behavioral skills (e.g. Communication, Leadership)")
    keywords: list[str] = Field(default_factory=list, description="General buzzwords or domain terms found in the description")


class JDProfileRecord(JDProfileBase, IdentifiableMixin):
    """
    Internal record representation stored in the system.
    """

    raw_text: str = Field(description="The raw text extracted from the uploaded PDF")


class JDProfileRead(JDProfileRecord):
    """
    Public API response shape for a parsed Job Description.
    """

    # We inherit all fields from JDProfileRecord including ID and dates.
    # No extra fields needed for now.
    pass
