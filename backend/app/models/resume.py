"""
Resume Profile domain models.

Provides the schema for structuring raw Resume text via the Gemini AI.
These models define the shape of candidate data used for matching.
"""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from app.models.base import AppBaseModel, IdentifiableMixin


class PersonalInformation(AppBaseModel):
    name: str = Field(description="Full name of the candidate")
    email: str | None = Field(default=None, description="Email address")
    phone: str | None = Field(default=None, description="Phone number")
    linkedin: str | None = Field(default=None, description="LinkedIn profile URL")
    github: str | None = Field(default=None, description="GitHub profile URL")


class ProfessionalInformation(AppBaseModel):
    current_role: str | None = Field(default=None, description="Current or most recent job title")
    industry: str | None = Field(default=None, description="Primary industry (e.g. Software, Finance)")
    seniority: str | None = Field(default=None, description="Inferred seniority level (e.g. Junior, Senior, Staff)")
    total_years_experience: float | None = Field(default=None, description="Total years of professional experience")


class SkillGroup(AppBaseModel):
    technical_skills: list[str] = Field(default_factory=list, description="General technical skills")
    frameworks: list[str] = Field(default_factory=list, description="Software frameworks (e.g. React, Django)")
    languages: list[str] = Field(default_factory=list, description="Programming languages")
    tools: list[str] = Field(default_factory=list, description="Development tools (e.g. Git, Docker)")
    cloud_platforms: list[str] = Field(default_factory=list, description="Cloud platforms (e.g. AWS, GCP)")
    databases: list[str] = Field(default_factory=list, description="Database technologies")
    soft_skills: list[str] = Field(default_factory=list, description="Soft skills and behavioral traits")


class WorkExperience(AppBaseModel):
    company: str = Field(description="Name of the company")
    job_title: str = Field(description="Job title held")
    start_date: str | None = Field(default=None, description="Start date (e.g. Jan 2020 or 2020-01)")
    end_date: str | None = Field(default=None, description="End date (e.g. Present or Dec 2022)")
    description: str | None = Field(default=None, description="Summary of responsibilities and achievements")
    technologies_used: list[str] = Field(default_factory=list, description="Technologies used in this role")


class Project(AppBaseModel):
    project_name: str = Field(description="Name of the project")
    description: str | None = Field(default=None, description="Description of the project")
    technologies: list[str] = Field(default_factory=list, description="Technologies used")
    domain: str | None = Field(default=None, description="Business domain or topic")


class Education(AppBaseModel):
    degree: str = Field(description="Degree obtained (e.g. Bachelor of Science)")
    specialization: str | None = Field(default=None, description="Major or specialization")
    institution: str = Field(description="Name of the educational institution")
    graduation_year: str | None = Field(default=None, description="Year of graduation")


class Certification(AppBaseModel):
    name: str = Field(description="Name of the certification")
    issuer: str | None = Field(default=None, description="Issuing organization")
    year: str | None = Field(default=None, description="Year obtained")


class ResumeProfileBase(AppBaseModel):
    """
    Core Resume fields extracted by the AI engine.

    Used directly as the Pydantic schema passed to the Gemini API.
    """
    personal_information: PersonalInformation = Field(description="Candidate contact and personal info")
    professional_information: ProfessionalInformation = Field(description="Candidate professional summary")
    skills: SkillGroup = Field(description="Categorized skills")
    experience: list[WorkExperience] = Field(default_factory=list, description="Work history")
    projects: list[Project] = Field(default_factory=list, description="Notable projects")
    education: list[Education] = Field(default_factory=list, description="Educational background")
    certifications: list[Certification] = Field(default_factory=list, description="Professional certifications")
    achievements: list[str] = Field(default_factory=list, description="Notable achievements or awards")
    publications: list[str] = Field(default_factory=list, description="Publications, patents, or papers")
    summary: str | None = Field(default=None, description="Overall professional summary")


class ResumeProfileRecord(ResumeProfileBase, IdentifiableMixin):
    """
    Internal record representation stored in the system.
    """
    analysis_job_id: UUID = Field(description="The analysis job this resume is linked to")
    original_file_id: UUID = Field(description="The original uploaded PDF file ID")
    raw_text: str = Field(description="The raw text extracted from the PDF")


class ResumeProfileRead(ResumeProfileRecord):
    """
    Public API response shape for a parsed Resume Profile.
    """
    pass
