"""
Semantic Profile domain models.

Provides the schema for storing semantic embeddings generated from 
structured Job Descriptions and Resumes. These profiles are used 
by the scoring engine for matching.
"""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from app.models.base import AppBaseModel, IdentifiableMixin


class SemanticProfileBase(AppBaseModel):
    """
    Core semantic embeddings fields.

    Represented as arrays of floats. In memory, the service converts 
    these to numpy arrays, but for the API and storage, they remain list[float].
    """
    # The global context embedding for the entire document
    full_document_embedding: list[float] = Field(
        description="L2-normalized embedding vector of the full JD or Resume"
    )

    # Sub-component embeddings for granular matching
    skill_embeddings: list[float] | None = Field(
        default=None, description="L2-normalized embedding of all skills combined"
    )
    project_embeddings: list[float] | None = Field(
        default=None, description="L2-normalized embedding of all projects combined"
    )
    experience_embeddings: list[float] | None = Field(
        default=None, description="L2-normalized embedding of all work experience combined"
    )
    education_embeddings: list[float] | None = Field(
        default=None, description="L2-normalized embedding of all education combined"
    )
    certification_embeddings: list[float] | None = Field(
        default=None, description="L2-normalized embedding of all certifications combined"
    )


class SemanticProfileRecord(SemanticProfileBase, IdentifiableMixin):
    """
    Internal record representation stored in the system.
    """
    # Indicates what this profile is associated with
    profile_type: str = Field(description="'job_description' or 'resume'")
    
    # ID of the associated JDProfileRecord or ResumeProfileRecord
    source_id: UUID = Field(description="The ID of the JDProfile or ResumeProfile this represents")
    
    # ID of the analysis job this belongs to
    analysis_job_id: UUID = Field(description="The analysis job this profile is linked to")


class SemanticProfileRead(SemanticProfileRecord):
    """
    Public API response shape for a semantic profile.
    
    Note: Returning high-dimensional vectors in JSON can be large, 
    but for transparency/debugging it's useful.
    """
    pass
