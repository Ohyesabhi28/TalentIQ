"""
Tests for JD Parsing Pipeline — Module 3.
"""

from __future__ import annotations

import pytest
from app.models.jd import JDProfileBase

class TestJDProfileBase:
    def test_schema_validates_correct_json(self):
        data = {
            "job_title": "Senior Backend Engineer",
            "industry": "Fintech",
            "seniority": "Senior",
            "required_skills": ["Python", "FastAPI"],
            "preferred_skills": ["AWS", "Redis"],
            "education": "BS CS",
            "experience": "5+ years",
            "certifications": [],
            "responsibilities": ["Write code", "Review PRs"],
            "soft_skills": ["Communication"],
            "keywords": ["startup", "fast-paced"]
        }
        profile = JDProfileBase.model_validate(data)
        assert profile.job_title == "Senior Backend Engineer"
        assert "Python" in profile.required_skills
