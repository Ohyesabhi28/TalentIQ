"""
Tests for Resume Parsing Pipeline — Module 4.
"""

from __future__ import annotations

import pytest
from app.models.resume import ResumeProfileBase

class TestResumeProfileBase:
    def test_schema_validates_correct_json(self):
        data = {
            "personal_information": {
                "name": "Jane Doe",
                "email": "jane@example.com",
            },
            "professional_information": {
                "current_role": "Senior Engineer",
                "total_years_experience": 8,
            },
            "skills": {
                "technical_skills": ["Python", "FastAPI"],
                "frameworks": ["Django"],
                "languages": ["Python", "JavaScript"],
                "tools": ["Git"],
                "cloud_platforms": ["AWS"],
                "databases": ["PostgreSQL"],
                "soft_skills": ["Leadership"],
            },
            "experience": [
                {
                    "company": "Tech Corp",
                    "job_title": "Senior Engineer",
                    "start_date": "Jan 2020",
                    "end_date": "Present",
                    "technologies_used": ["Python"],
                }
            ],
            "projects": [],
            "education": [
                {
                    "degree": "B.S. Computer Science",
                    "institution": "University of Tech",
                    "graduation_year": "2018",
                }
            ],
            "certifications": [],
            "achievements": [],
            "publications": [],
        }
        profile = ResumeProfileBase.model_validate(data)
        assert profile.personal_information.name == "Jane Doe"
        assert len(profile.experience) == 1
        assert profile.experience[0].company == "Tech Corp"
